# Support Infrastructure Patterns

Defines the shared infrastructure packages generated in Phase 2. These types are imported by all context-specific layers.

## Output Files

- `internal/support/basedomain/base_entity.go` - Base entity with event tracking
- `internal/support/basedomain/domain_event.go` - Domain event interface
- `internal/support/validation/validator.go` - Struct validation wrapper
- `internal/support/config/config.go` - Environment configuration
- `internal/support/errors/errors.go` - Common error types and HTTP mapping
- `internal/support/logging/logger.go` - Structured logger interface
- `internal/support/server/server.go` - HTTP server setup
- `internal/support/eventbus/event_bus.go` - In-memory event bus (pattern in `adapters.md`)

Note: `auth/` patterns (including `jwt.go` for signing/parsing and `cmd/gentoken/` for the token generation CLI) are defined in `authorization.md`. Auth middleware (`httpmiddleware/`) is a driving adapter defined in `authorization.md`, generated in Phase 4.

## Patterns

### Base Entity

```go
package basedomain

import "time"

// DomainEvent is the interface all domain events must implement
type DomainEvent interface {
	EventName() string
	OccurredAt() time.Time
}

// BaseEntity provides identity and event tracking for all aggregate roots
type BaseEntity[T any] struct {
	Id        T            `json:"id"`
	CreatedAt time.Time    `json:"createdAt"`
	UpdatedAt time.Time    `json:"updatedAt"`
	events    []DomainEvent
}

// NewBaseEntity creates a new BaseEntity with the given ID
func NewBaseEntity[T any](id T) BaseEntity[T] {
	now := time.Now()
	return BaseEntity[T]{
		Id:        id,
		CreatedAt: now,
		UpdatedAt: now,
	}
}

// GetId returns the entity's identifier
func (e *BaseEntity[T]) GetId() T {
	return e.Id
}

// AddEvent records a domain event to be published after persistence
func (e *BaseEntity[T]) AddEvent(event DomainEvent) {
	e.events = append(e.events, event)
}

// GetEvents returns all pending domain events
func (e *BaseEntity[T]) GetEvents() []DomainEvent {
	return e.events
}

// ClearEvents removes all pending domain events (called after publishing)
func (e *BaseEntity[T]) ClearEvents() {
	e.events = nil
}
```

### Validation

```go
package validation

import (
	"github.com/go-playground/validator/v10"
)

var validate = validator.New()

// Validate validates a struct using its `validate` tags
func Validate(s any) error {
	return validate.Struct(s)
}
```

### Configuration

```go
package config

import "os"

// Config holds application configuration loaded from environment variables
type Config struct {
	Port      string
	LogLevel  string
	JWTSecret string
	AppMode   string // "mock" enables test data seeding; empty or "live" for production
}

// Load reads configuration from environment variables with defaults
func Load() Config {
	return Config{
		Port:      getEnv("PORT", "8080"),
		LogLevel:  getEnv("LOG_LEVEL", "info"),
		JWTSecret: getEnv("JWT_SECRET", "dev-secret-change-me"),
		AppMode:   getEnv("APP_MODE", ""),
	}
}

func getEnv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return fallback
}
```

### Common Errors

```go
package errors

import "net/http"

// NotFoundError indicates a requested resource does not exist
type NotFoundError struct {
	Resource string
	ID       string
}

func NewNotFoundError(resource, id string) NotFoundError {
	return NotFoundError{Resource: resource, ID: id}
}

func (e NotFoundError) Error() string {
	return e.Resource + " not found: " + e.ID
}

// ValidationError indicates invalid input or domain rule violation
type ValidationError struct {
	Message string
}

func NewValidationError(message string) ValidationError {
	return ValidationError{Message: message}
}

func (e ValidationError) Error() string {
	return "validation: " + e.Message
}

// ConflictError indicates a resource already exists or state conflict
type ConflictError struct {
	Message string
}

func NewConflictError(message string) ConflictError {
	return ConflictError{Message: message}
}

func (e ConflictError) Error() string {
	return "conflict: " + e.Message
}

// HTTPStatusCode maps domain/support error types to HTTP status codes.
// Used by HTTP handlers to translate errors into responses.
func HTTPStatusCode(err error) int {
	switch err.(type) {
	case ValidationError:
		return http.StatusUnprocessableEntity
	case NotFoundError:
		return http.StatusNotFound
	case ConflictError:
		return http.StatusConflict
	default:
		return http.StatusInternalServerError
	}
}
```

Note: `auth.AuthenticationError` maps to 401 and `auth.AuthorizationError` maps to 403. Those types are defined in `authorization.md`. HTTP handlers should check for auth errors first, then call `errors.HTTPStatusCode` for remaining errors. If a context defines additional domain-specific error types, add cases to `HTTPStatusCode` or check for them via type assertion in the handler before falling through to this function.

### Logging

```go
package logging

import "log/slog"

// NewLogger creates a structured logger with the given service name
func NewLogger(service string) *slog.Logger {
	return slog.Default().With("service", service)
}
```

### HTTP Server

```go
package server

import (
	"context"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

// Run starts the HTTP server and blocks until a shutdown signal is received
func Run(mux *http.ServeMux, addr string, logger *slog.Logger) error {
	srv := &http.Server{
		Addr:         addr,
		Handler:      mux,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	errCh := make(chan error, 1)
	go func() {
		logger.Info("server starting", "addr", addr)
		errCh <- srv.ListenAndServe()
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

	select {
	case err := <-errCh:
		return err
	case sig := <-quit:
		logger.Info("shutting down", "signal", sig)
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		return srv.Shutdown(ctx)
	}
}
```

## Guidelines

1. Support packages have **zero dependencies** on context-specific code
2. All support types should be minimal — just enough for the walking skeleton
3. `basedomain.DomainEvent` is the contract that all context-specific events implement
4. `BaseEntity` uses pointer receivers for event mutation methods (`AddEvent`, `ClearEvents`)
5. The `errors.HTTPStatusCode` function is extensible — domain-specific errors can be added via type switch cases in HTTP handlers
