# Adapters Layer Patterns

## Input

From manifest and BCR:
- Context name and entities
- Port interfaces to implement
- HTTP endpoints to expose
- Cross-context integrations

This file covers driven (outbound) and integration (ACL) adapter patterns. For driving (inbound/HTTP) adapter patterns, see `adapters-driving.md`.

## Output Files

### Driven Adapters (Outbound)
- `internal/adapters/driven/in_memory_{entity}_repo/in_memory_{entity}_repository.go`
- `internal/adapters/driven/event_bus/in_memory_event_bus.go`
- `internal/adapters/driven/stdout_event_publisher/stdout_event_publisher.go`

### Integration Adapters (ACL)
- `internal/adapters/integration/{source}_to_{target}_handler.go`
- `internal/adapters/integration/{context}_service_adapter.go`

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

// List retrieves a paginated set of {entities}
// Include this method when the FQBC API Binding defines a paginated list endpoint.
func (r *InMemory{Entity}Repository) List(ctx context.Context, query {context}domain.ListQuery) ({context}domain.ListResult[{context}domain.{Entity}], error) {
	r.mutex.RLock()
	defer r.mutex.RUnlock()

	all := make([]{context}domain.{Entity}, 0, len(r.{entities}))
	for _, {entity} := range r.{entities} {
		all = append(all, {entity})
	}

	totalCount := len(all)
	start := query.Offset
	if start > totalCount {
		start = totalCount
	}
	end := start + query.Limit
	if end > totalCount {
		end = totalCount
	}

	return {context}domain.ListResult[{context}domain.{Entity}]{
		Items:      all[start:end],
		TotalCount: totalCount,
	}, nil
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

### Stdout Event Publisher Pattern

```go
package stdout_event_publisher

import (
	"encoding/json"
	"log/slog"

	"{module}/internal/support/basedomain"
)

// StdoutEventPublisher logs domain events to stdout for development/debugging
type StdoutEventPublisher struct {
	logger *slog.Logger
}

// NewStdoutEventPublisher creates a new stdout event publisher
func NewStdoutEventPublisher(logger *slog.Logger) *StdoutEventPublisher {
	return &StdoutEventPublisher{logger: logger}
}

// Publish logs the event as structured JSON
func (p *StdoutEventPublisher) Publish(event basedomain.DomainEvent) error {
	payload, _ := json.Marshal(event)
	p.logger.Info("DomainEvent published",
		"eventName", event.EventName(),
		"occurredAt", event.OccurredAt(),
		"payload", string(payload),
	)
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
	// ACL Translation: Convert {Source} domain types → {Target} domain types.
	// Field mapping rules:
	//   - Same-name, same-type fields: assign directly (e.g., Name → Name)
	//   - Same-concept, different-name: map explicitly (e.g., source.ItemId → target.ProductId)
	//   - Value object unwrap/wrap: call constructors (e.g., source.Price.Amount() → target.Cost)
	//   - Missing fields: use zero values or domain defaults with a comment explaining why
	{target}Input := {target_context}domain.{TargetInputType}{
		{TargetField1}: input.{SourceField1},           // direct mapping
		{TargetField2}: input.{SourceValueObj}.Value(),  // value object unwrap example
	}

	// Call the target service
	{target}Output, err := a.{target}Service.{TargetOperation}(ctx, {target}Input)
	if err != nil {
		return nil, err
	}

	// ACL Translation: Convert {Target} domain types → {Source} domain types (reverse)
	{source}Output := make([]{source_context}domain.{OutputType}, len({target}Output))
	for i, item := range {target}Output {
		{source}Output[i] = {source_context}domain.{OutputType}{
			{SourceField1}: item.{TargetField1},
			{SourceField2}: {source_context}domain.New{ValueObj}(item.{TargetField2}),  // value object wrap example
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

	// TODO: Translate {Source} event fields to {Target} context domain types (ACL translation)
	// TODO: Call h.{target}Service.{TargetOperation}(ctx, ...) to update {Target} state

	return nil
}
```

