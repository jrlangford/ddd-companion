# Adapters Layer Patterns

## Input

From manifest and BCR:
- Context name and entities
- Port interfaces to implement
- HTTP endpoints to expose
- Cross-context integrations

## Output Files

### Driven Adapters (Outbound)
- `internal/adapters/driven/in_memory_{entity}_repo/in_memory_{entity}_repository.go`
- `internal/adapters/driven/event_bus/in_memory_event_bus.go`
- `internal/adapters/driven/stdout_event_publisher/stdout_event_publisher.go`

### Integration Adapters (ACL)
- `internal/adapters/integration/{source}_to_{target}_handler.go`
- `internal/adapters/integration/{context}_service_adapter.go`

### Driving Adapters (Inbound)
- `internal/adapters/driving/httpadapter/dto.go`
- `internal/adapters/driving/httpadapter/http_handlers.go`
- `internal/adapters/driving/httpadapter/routes.go`
- `internal/adapters/driving/httpadapter/httpmiddleware/auth_middleware.go`

---

## Driven Adapter Patterns

### In-Memory Repository Pattern

```go
package in_memory_{entity}_repo

import (
	"context"
	"fmt"
	"sync"

	"{module}/internal/{context}/{context}domain"
	"{module}/internal/{context}/ports/{context}secondary"
)

// InMemory{Entity}Repository provides an in-memory implementation of the {Entity}Repository
type InMemory{Entity}Repository struct {
	{entities} map[string]{context}domain.{Entity}
	mutex     sync.RWMutex
}

// NewInMemory{Entity}Repository creates a new in-memory {entity} repository
func NewInMemory{Entity}Repository() {context}secondary.{Entity}Repository {
	return &InMemory{Entity}Repository{
		{entities}: make(map[string]{context}domain.{Entity}),
	}
}

// Store saves a {entity} to the repository
func (r *InMemory{Entity}Repository) Store(ctx context.Context, {entity} {context}domain.{Entity}) error {
	r.mutex.Lock()
	defer r.mutex.Unlock()

	id := {entity}.Get{EntityId}().String()
	r.{entities}[id] = {entity}
	return nil
}

// FindById retrieves a {entity} by its ID
func (r *InMemory{Entity}Repository) FindById(ctx context.Context, id {context}domain.{EntityId}) ({context}domain.{Entity}, error) {
	r.mutex.RLock()
	defer r.mutex.RUnlock()

	{entity}, exists := r.{entities}[id.String()]
	if !exists {
		return {context}domain.{Entity}{}, fmt.Errorf("{entity} with ID %s not found", id.String())
	}
	return {entity}, nil
}

// FindAll retrieves all {entities} in the repository
func (r *InMemory{Entity}Repository) FindAll(ctx context.Context) ([]{context}domain.{Entity}, error) {
	r.mutex.RLock()
	defer r.mutex.RUnlock()

	{entities} := make([]{context}domain.{Entity}, 0, len(r.{entities}))
	for _, {entity} := range r.{entities} {
		{entities} = append({entities}, {entity})
	}
	return {entities}, nil
}

// Update updates an existing {entity}
func (r *InMemory{Entity}Repository) Update(ctx context.Context, {entity} {context}domain.{Entity}) error {
	r.mutex.Lock()
	defer r.mutex.Unlock()

	id := {entity}.Get{EntityId}().String()
	if _, exists := r.{entities}[id]; !exists {
		return fmt.Errorf("{entity} with ID %s not found", id)
	}
	r.{entities}[id] = {entity}
	return nil
}

// Delete removes a {entity} from the repository
func (r *InMemory{Entity}Repository) Delete(ctx context.Context, id {context}domain.{EntityId}) error {
	r.mutex.Lock()
	defer r.mutex.Unlock()

	delete(r.{entities}, id.String())
	return nil
}
```

### Event Bus Pattern

```go
package event_bus

import (
	"context"
	"log/slog"
	"sync"

	"{module}/internal/support/basedomain"
)

// EventHandler handles domain events
type EventHandler interface {
	Handle(ctx context.Context, event basedomain.DomainEvent) error
}

// InMemoryEventBus provides an in-memory event bus implementation
type InMemoryEventBus struct {
	handlers map[string][]EventHandler
	mutex    sync.RWMutex
	logger   *slog.Logger
}

// NewInMemoryEventBus creates a new in-memory event bus
func NewInMemoryEventBus(logger *slog.Logger) *InMemoryEventBus {
	return &InMemoryEventBus{
		handlers: make(map[string][]EventHandler),
		logger:   logger,
	}
}

// Subscribe registers a handler for an event type
func (b *InMemoryEventBus) Subscribe(eventType string, handler EventHandler) {
	b.mutex.Lock()
	defer b.mutex.Unlock()

	b.handlers[eventType] = append(b.handlers[eventType], handler)
	b.logger.Debug("Subscribed handler to event", "eventType", eventType)
}

// Publish publishes a domain event to all registered handlers
func (b *InMemoryEventBus) Publish(event basedomain.DomainEvent) error {
	b.mutex.RLock()
	handlers := b.handlers[event.EventName()]
	b.mutex.RUnlock()

	b.logger.Debug("Publishing event", "eventName", event.EventName(), "handlerCount", len(handlers))

	ctx := context.Background()
	for _, handler := range handlers {
		if err := handler.Handle(ctx, event); err != nil {
			b.logger.Error("Handler failed to process event",
				"eventName", event.EventName(),
				"error", err)
			// Continue with other handlers
		}
	}

	return nil
}
```

---

## Integration Adapter Patterns

### ACL Service Adapter Pattern (Synchronous Integration)

```go
package integration

import (
	"context"
	"time"

	"{module}/internal/{source_context}/{source_context}domain"
	"{module}/internal/{source_context}/ports/{source_context}secondary"
	"{module}/internal/{target_context}/ports/{target_context}primary"
	"{module}/internal/{target_context}/{target_context}domain"
)

// {Target}ServiceAdapter adapts the {Target} context's application service
// to the interface expected by the {Source} context (Anti-Corruption Layer)
type {Target}ServiceAdapter struct {
	{target}Service {target_context}primary.{Target}Service
}

// New{Target}ServiceAdapter creates a new adapter for the {target} service
func New{Target}ServiceAdapter({target}Service {target_context}primary.{Target}Service) {source_context}secondary.{Target}Service {
	return &{Target}ServiceAdapter{
		{target}Service: {target}Service,
	}
}

// {OperationName} adapts the {target} service's interface to the {source} context's needs
func (a *{Target}ServiceAdapter) {OperationName}(ctx context.Context, input {source_context}domain.{InputType}) ([]{source_context}domain.{OutputType}, error) {
	// Convert {Source} domain types to {Target} domain types (ACL translation)
	{target}Input := {target_context}domain.{TargetInputType}{
		// Map fields from source domain to target domain
		{field_mappings}
	}

	// Call the target service
	{target}Output, err := a.{target}Service.{TargetOperation}(ctx, {target}Input)
	if err != nil {
		return nil, err
	}

	// Convert {Target} domain types back to {Source} domain types (ACL translation)
	{source}Output := make([]{source_context}domain.{OutputType}, len({target}Output))
	for i, item := range {target}Output {
		{source}Output[i] = {source_context}domain.{OutputType}{
			// Map fields from target domain to source domain
			{reverse_field_mappings}
		}
	}

	return {source}Output, nil
}
```

### Event Handler Pattern (Asynchronous Integration)

```go
package integration

import (
	"context"
	"log/slog"

	"{module}/internal/{source_context}/{source_context}domain"
	"{module}/internal/{target_context}/ports/{target_context}primary"
	"{module}/internal/support/basedomain"
)

// {Source}To{Target}EventHandler handles events from {Source} context
// and updates {Target} context accordingly
type {Source}To{Target}EventHandler struct {
	{target}Service {target_context}primary.{Target}Service
	logger         *slog.Logger
}

// New{Source}To{Target}EventHandler creates a new event handler
func New{Source}To{Target}EventHandler(
	{target}Service {target_context}primary.{Target}Service,
	logger *slog.Logger,
) *{Source}To{Target}EventHandler {
	return &{Source}To{Target}EventHandler{
		{target}Service: {target}Service,
		logger:         logger,
	}
}

// Handle processes domain events from {Source} context
func (h *{Source}To{Target}EventHandler) Handle(ctx context.Context, event basedomain.DomainEvent) error {
	switch e := event.(type) {
	case {source_context}domain.{EventName}Event:
		return h.handle{EventName}(ctx, e)
	default:
		h.logger.Debug("Ignoring unhandled event type", "eventName", event.EventName())
		return nil
	}
}

func (h *{Source}To{Target}EventHandler) handle{EventName}(ctx context.Context, event {source_context}domain.{EventName}Event) error {
	h.logger.Info("Handling {EventName} event", "payload", event)

	// Translate event to {Target} context operation
	// Call {Target} service to update state

	return nil
}
```

---

## Driving Adapter Patterns

> **Spec-First**: HTTP adapters are generated AFTER TypeSpec contracts. The TypeSpec
> specification serves as the source of truth for API design. DTOs, handlers, and routes
> should conform to the TypeSpec contract defined in `api/main.tsp`.

### HTTP Handler Pattern

```go
package httpadapter

import (
	"encoding/json"
	"net/http"

	"{module}/internal/{context}/ports/{context}primary"
	"{module}/internal/{context}/{context}domain"
	"{module}/internal/support/validation"
)

// Handler is the main HTTP handler
type Handler struct {
	{context}Service {context}primary.{Context}Service
}

// NewHandler creates a new HTTP handler
func NewHandler({context}Service {context}primary.{Context}Service) *Handler {
	return &Handler{
		{context}Service: {context}Service,
	}
}

// {Operation}Handler handles {operation} requests
func (h *Handler) {Operation}Handler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	// Parse request body
	var req {Operation}Request
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.writeErrorResponse(w, "invalid_request", "Invalid JSON format", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	// Validate request
	if err := validation.Validate(req); err != nil {
		h.writeErrorResponse(w, "validation_error", err.Error(), http.StatusBadRequest)
		return
	}

	// Call service
	result, err := h.{context}Service.{Operation}(r.Context(), req.{Params}...)
	if err != nil {
		h.writeErrorResponse(w, "{operation}_failed", err.Error(), http.StatusInternalServerError)
		return
	}

	// Return response
	response := {Operation}ToResponse(result)
	w.WriteHeader(http.StatusOK) // or http.StatusCreated for POST
	json.NewEncoder(w).Encode(SuccessResponse{
		Status: "success",
		Data:   response,
	})
}

func (h *Handler) writeErrorResponse(w http.ResponseWriter, errorCode, message string, httpStatus int) {
	w.WriteHeader(httpStatus)
	json.NewEncoder(w).Encode(ErrorResponse{
		Error:   errorCode,
		Message: message,
		Code:    httpStatus,
	})
}
```

### DTO Pattern

```go
package httpadapter

import (
	"time"

	"{module}/internal/{context}/{context}domain"
)

// {Operation}Request represents the request payload
type {Operation}Request struct {
	{{range .RequestFields}}
	{FieldName} {FieldType} `json:"{json_name}" validate:"{validation_tags}"`
	{{end}}
}

// {Entity}Response represents the response payload
type {Entity}Response struct {
	{{range .ResponseFields}}
	{FieldName} {FieldType} `json:"{json_name}{{if .OmitEmpty}},omitempty{{end}}"`
	{{end}}
}

// SuccessResponse wraps successful responses
type SuccessResponse struct {
	Status string      `json:"status"`
	Data   interface{} `json:"data,omitempty"`
}

// ErrorResponse represents error responses
type ErrorResponse struct {
	Error   string `json:"error"`
	Message string `json:"message"`
	Code    int    `json:"code"`
}

// {Entity}ToResponse converts domain entity to response DTO
func {Entity}ToResponse(entity {context}domain.{Entity}) {Entity}Response {
	return {Entity}Response{
		{{range .FieldMappings}}
		{ResponseField}: entity.{DomainGetter}(),
		{{end}}
	}
}
```

### Routes Pattern

```go
package httpadapter

import (
	"net/http"

	"{module}/internal/adapters/driving/httpadapter/httpmiddleware"
)

// RegisterRoutes registers all HTTP routes
func (h *Handler) RegisterRoutes(mux *http.ServeMux, authMiddleware *httpmiddleware.AuthMiddleware) {
	// Public endpoints
	mux.HandleFunc("GET /health", h.HealthHandler)
	mux.HandleFunc("GET /info", h.InfoHandler)

	// Protected endpoints - {Context}
	mux.HandleFunc("POST /api/v1/{entities}", authMiddleware.RequireAuth(h.Create{Entity}Handler))
	mux.HandleFunc("GET /api/v1/{entities}", authMiddleware.RequireAuth(h.List{Entities}Handler))
	mux.HandleFunc("GET /api/v1/{entities}/{id}", authMiddleware.RequireAuth(h.Get{Entity}Handler))
	mux.HandleFunc("PUT /api/v1/{entities}/{id}", authMiddleware.RequireAuth(h.Update{Entity}Handler))
	mux.HandleFunc("DELETE /api/v1/{entities}/{id}", authMiddleware.RequireAuth(h.Delete{Entity}Handler))
}
```
