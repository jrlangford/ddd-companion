# Ports Layer Patterns

## Input

From manifest and BCR:
- Context name
- Operations (use cases) from BCR
- Entities referenced by operations
- External dependencies (other contexts, external services)

## Output Files

For each context:
- `internal/{context}/ports/{context}primary/{context}_service.go` - Primary port interfaces
- `internal/{context}/ports/{context}secondary/repositories.go` - Repository interfaces
- `internal/{context}/ports/{context}secondary/services.go` - External service interfaces (if needed)

## Naming Rationale

The term "Service" appears in several port-related names with distinct meanings:

| Name | Role | Why "Service" |
|------|------|---------------|
| `{Context}Service` | Primary port interface | Facade over all use cases in this context — named after the context it serves |
| `{Context}ApplicationService` | Concrete implementation of the primary port | Standard DDD application service — orchestrates domain objects |
| `{ExternalContext}Service` | Secondary port for cross-context integration | Represents a dependency on another context's capabilities |

Primary ports use **context-level** naming (`BookingService`) because one facade groups all inbound operations. Secondary ports use **entity-level** naming (`CargoRepository`) because each aggregate root has its own persistence boundary. This granularity difference is intentional: a context exposes a unified API surface, but persists aggregates independently.

## Patterns

### Primary Port Interface Pattern

```go
package {context}primary

import (
	"context"

	"{module}/internal/{context}/{context}domain"
)

// {Context}Service defines the primary port for {context} operations
type {Context}Service interface {
	{{range .Operations}}
	// {OperationName} {operation_description}
	{OperationName}(ctx context.Context{{range .InputParams}}, {param_name} {context}domain.{ParamType}{{end}}) ({{if .ReturnType}}{context}domain.{ReturnType}, {{end}}error)
	{{end}}
}

{{if .HasTracker}}
// {Entity}Tracker defines the primary port for {entity} tracking queries
type {Entity}Tracker interface {
	// Track{Entity} returns the current status of {entity} by ID
	Track{Entity}(ctx context.Context, id {context}domain.{EntityId}) ({context}domain.{Entity}, error)
}
{{end}}
```

### Repository Interface Pattern

```go
package {context}secondary

import (
	"context"

	"{module}/internal/{context}/{context}domain"
)

// {Entity}Repository defines the secondary port for {entity} persistence
type {Entity}Repository interface {
	// Store persists a {entity} aggregate
	Store(ctx context.Context, entity {context}domain.{Entity}) error

	// FindById retrieves a {entity} by its ID
	FindById(ctx context.Context, id {context}domain.{EntityId}) ({context}domain.{Entity}, error)

	// FindAll retrieves all {entities} (mainly for administrative purposes)
	FindAll(ctx context.Context) ([]{context}domain.{Entity}, error)

	// Update updates an existing {entity}
	Update(ctx context.Context, entity {context}domain.{Entity}) error

	// Delete removes a {entity} by its ID
	Delete(ctx context.Context, id {context}domain.{EntityId}) error

	{{range .CustomQueries}}
	// {QueryName} {query_description}
	{QueryName}(ctx context.Context{{range .QueryParams}}, {param_name} {param_type}{{end}}) ({{.ReturnType}}, error)
	{{end}}
}
```

### External Service Interface Pattern

For synchronous cross-context integration:

```go
package {context}secondary

import (
	"context"

	"{module}/internal/{context}/{context}domain"
)

// {ExternalContext}Service defines the secondary port for {external_context} integration.
// Parameters and return types use LOCAL context domain types — the ACL adapter
// (implementation) handles translation to/from the external context's types.
type {ExternalContext}Service interface {
	{{range .ExternalOperations}}
	// {OperationName} {operation_description}
	{OperationName}(ctx context.Context{{range .InputParams}}, {param_name} {context}domain.{ParamType}{{end}}) ({context}domain.{ReturnType}, error)
	{{end}}
}
```

### Event Publisher Interface Pattern

```go
package {context}secondary

import (
	"{module}/internal/support/basedomain"
)

// EventPublisher defines the secondary port for publishing domain events
type EventPublisher interface {
	// Publish publishes a domain event
	Publish(event basedomain.DomainEvent) error
}
```

## Example: Booking Context Ports

### Primary Port

```go
package bookingprimary

import (
	"context"

	"myproject/internal/booking/bookingdomain"
)

// BookingService defines the primary port for cargo booking operations
type BookingService interface {
	// BookNewCargo initiates the creation of a new cargo based on customer's request
	BookNewCargo(ctx context.Context, origin, destination string, arrivalDeadline string) (bookingdomain.Cargo, error)

	// AssignRouteToCargo assigns a chosen itinerary to an existing cargo
	AssignRouteToCargo(ctx context.Context, trackingId bookingdomain.TrackingId, itinerary bookingdomain.Itinerary) error

	// GetCargoDetails retrieves the full state of a cargo for tracking
	GetCargoDetails(ctx context.Context, trackingId bookingdomain.TrackingId) (bookingdomain.Cargo, error)

	// ListAllCargo retrieves all cargo
	ListAllCargo(ctx context.Context) ([]bookingdomain.Cargo, error)

	// RequestRouteCandidates gets possible itineraries for a cargo
	RequestRouteCandidates(ctx context.Context, trackingId bookingdomain.TrackingId) ([]bookingdomain.Itinerary, error)

	// UpdateCargoDelivery updates cargo delivery status based on handling events
	UpdateCargoDelivery(ctx context.Context, trackingId bookingdomain.TrackingId, handlingHistory []bookingdomain.HandlingEventSummary) error
}

// CargoTracker defines the primary port for cargo tracking queries
type CargoTracker interface {
	// TrackCargo returns the current status of cargo by tracking ID
	TrackCargo(ctx context.Context, trackingId bookingdomain.TrackingId) (bookingdomain.Cargo, error)
}
```

### Secondary Ports

```go
package bookingsecondary

import (
	"context"

	"myproject/internal/booking/bookingdomain"
	"myproject/internal/support/basedomain"
)

// CargoRepository defines the secondary port for cargo persistence
type CargoRepository interface {
	Store(ctx context.Context, cargo bookingdomain.Cargo) error
	FindByTrackingId(ctx context.Context, trackingId bookingdomain.TrackingId) (bookingdomain.Cargo, error)
	FindUnrouted(ctx context.Context) ([]bookingdomain.Cargo, error)
	FindAll(ctx context.Context) ([]bookingdomain.Cargo, error)
	Update(ctx context.Context, cargo bookingdomain.Cargo) error
	Delete(ctx context.Context, id bookingdomain.TrackingId) error
}

// RoutingService defines the secondary port for route calculation
// Implemented by ACL adapter to Routing context
type RoutingService interface {
	FindOptimalItineraries(ctx context.Context, routeSpec bookingdomain.RouteSpecification) ([]bookingdomain.Itinerary, error)
}

// EventPublisher defines the secondary port for publishing domain events
type EventPublisher interface {
	Publish(event basedomain.DomainEvent) error
}
```

## Constraints

- **Port packages MUST contain only Go interface definitions.** No structs, type aliases, enums, or other concrete types may be defined in port files. All domain types (entities, value objects, IDs, enums, events) referenced by port interfaces MUST be imported from `{context}domain`. If a type does not yet exist in the domain package, create it there first.

## Pagination

When a list endpoint uses pagination (per FQBC API Binding / api-conventions.md), add a paginated list method to the repository alongside `FindAll`. The query and result types live in the domain package since port packages contain only interfaces.

### Domain types (in `{context}domain`)

```go
// ListQuery holds pagination parameters
type ListQuery struct {
	Offset int
	Limit  int
}

// ListResult holds a paginated result set
type ListResult[T any] struct {
	Items      []T
	TotalCount int
}
```

### Repository method (added to interface)

```go
	// List retrieves a paginated set of {entities}
	List(ctx context.Context, query {context}domain.ListQuery) ({context}domain.ListResult[{context}domain.{Entity}], error)
```

The HTTP handler reads `offset` and `limit` from query parameters, calls `List`, and builds the response envelope with `next`/`previous` links per api-conventions.md.

## Guidelines

1. **Primary ports** define what the context offers to the outside world
2. **Secondary ports** define what the context needs from the outside world
3. All ports use **context-local domain types** (never cross-context domain types)
4. Repository interfaces follow standard patterns: `Store`, `FindById`, `FindAll`, `Update`, `Delete`, and optionally `List` for paginated endpoints
5. Use `context.Context` as first parameter for all operations
6. Return `error` as last return value
7. Document each method with its purpose
