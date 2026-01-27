# Application Layer Patterns

## Input

From manifest and BCR:
- Context name
- Operations (use cases)
- Required permissions per operation
- Dependencies (repositories, external services)

## Output Files

For each context:
- `internal/{context}/{context}application/{context}_service.go` - Application service
- `internal/{context}/{context}application/permissions.go` - Domain-specific authorization

## Patterns

### Application Service Pattern

```go
package {context}application

import (
	"context"
	"log/slog"

	"{module}/internal/{context}/{context}domain"
	"{module}/internal/{context}/ports/{context}primary"
	"{module}/internal/{context}/ports/{context}secondary"
	"{module}/internal/support/auth"
)

// {Context}ApplicationService implements the primary ports for {context} operations
type {Context}ApplicationService struct {
	{entity}Repo     {context}secondary.{Entity}Repository
	{{if .HasExternalService}}
	{external}Service {context}secondary.{External}Service
	{{end}}
	eventPublisher  {context}secondary.EventPublisher
	logger          *slog.Logger
}

// Ensure {Context}ApplicationService implements the primary ports
var _ {context}primary.{Context}Service = (*{Context}ApplicationService)(nil)

// New{Context}ApplicationService creates a new {Context}ApplicationService
func New{Context}ApplicationService(
	{entity}Repo {context}secondary.{Entity}Repository,
	{{if .HasExternalService}}
	{external}Service {context}secondary.{External}Service,
	{{end}}
	eventPublisher {context}secondary.EventPublisher,
	logger *slog.Logger,
) *{Context}ApplicationService {
	return &{Context}ApplicationService{
		{entity}Repo:     {entity}Repo,
		{{if .HasExternalService}}
		{external}Service: {external}Service,
		{{end}}
		eventPublisher:  eventPublisher,
		logger:          logger,
	}
}

{{range .Operations}}
// {OperationName} {operation_description}
func (s *{Context}ApplicationService) {OperationName}(ctx context.Context{{range .InputParams}}, {param_name} {param_type}{{end}}) ({{if .ReturnType}}{return_type}, {{end}}error) {
	// Check permissions
	claims, err := auth.ExtractClaims(ctx)
	if err != nil {
		s.logger.Warn("Unauthorized {operation_name} attempt", "error", err)
		return {{if .ReturnType}}{zero_value}, {{end}}err
	}
	if err := Require{Context}Permission(claims, auth.Permission{PermissionName}); err != nil {
		s.logger.Warn("Unauthorized {operation_name} attempt", "error", err)
		return {{if .ReturnType}}{zero_value}, {{end}}err
	}

	s.logger.Info("{Operation description}"{{range .LogParams}}, "{log_key}", {log_value}{{end}})

	// TODO: Implement business logic
	// 1. Load domain objects from repository
	// 2. Execute domain operations
	// 3. Save changes to repository
	// 4. Publish domain events

	{{if .ReturnType}}
	return {result}, nil
	{{else}}
	return nil
	{{end}}
}
{{end}}

// publish{Entity}Events publishes all pending events from the {entity} aggregate
func (s *{Context}ApplicationService) publish{Entity}Events({entity} {context}domain.{Entity}) {
	events := {entity}.GetEvents()
	for _, event := range events {
		if err := s.eventPublisher.Publish(event); err != nil {
			s.logger.Error("Failed to publish event",
				"eventName", event.EventName(),
				"error", err)
		}
	}
	{entity}.ClearEvents()
}
```

### Permissions Pattern

```go
package {context}application

import (
	"{module}/internal/support/auth"
)

// {Context} permissions
const (
	{{range .Permissions}}
	Permission{PermissionName} auth.Permission = "{permission_code}"
	{{end}}
)

// Require{Context}Permission checks if claims have the required {context} permission
func Require{Context}Permission(claims *auth.Claims, permission auth.Permission) error {
	if claims == nil {
		return auth.NewAuthorizationError("no claims present")
	}

	// Admin role has all permissions
	if claims.HasRole(auth.RoleAdmin) {
		return nil
	}

	// Check specific permission based on role
	switch permission {
	{{range .PermissionChecks}}
	case Permission{PermissionName}:
		if claims.HasRole(auth.RoleUser) || claims.HasRole(auth.RoleReadOnly) {
			return nil
		}
	{{end}}
	}

	return auth.NewAuthorizationError("insufficient permissions for " + string(permission))
}
```

## Example: Booking Application Service

```go
package bookingapplication

import (
	"context"
	"log/slog"
	"time"

	"myproject/internal/booking/bookingdomain"
	"myproject/internal/booking/ports/bookingprimary"
	"myproject/internal/booking/ports/bookingsecondary"
	"myproject/internal/support/auth"
)

type BookingApplicationService struct {
	cargoRepo      bookingsecondary.CargoRepository
	routingService bookingsecondary.RoutingService
	eventPublisher bookingsecondary.EventPublisher
	logger         *slog.Logger
}

var _ bookingprimary.BookingService = (*BookingApplicationService)(nil)

func NewBookingApplicationService(
	cargoRepo bookingsecondary.CargoRepository,
	routingService bookingsecondary.RoutingService,
	eventPublisher bookingsecondary.EventPublisher,
	logger *slog.Logger,
) *BookingApplicationService {
	return &BookingApplicationService{
		cargoRepo:      cargoRepo,
		routingService: routingService,
		eventPublisher: eventPublisher,
		logger:         logger,
	}
}

func (s *BookingApplicationService) BookNewCargo(ctx context.Context, origin, destination string, arrivalDeadlineStr string) (bookingdomain.Cargo, error) {
	// Check permissions
	claims, err := auth.ExtractClaims(ctx)
	if err != nil {
		s.logger.Warn("Unauthorized cargo booking attempt", "error", err)
		return bookingdomain.Cargo{}, err
	}
	if err := RequireBookingPermission(claims, PermissionBookCargo); err != nil {
		s.logger.Warn("Unauthorized cargo booking attempt", "error", err)
		return bookingdomain.Cargo{}, err
	}

	s.logger.Info("Booking new cargo",
		"origin", origin,
		"destination", destination,
		"arrivalDeadline", arrivalDeadlineStr)

	// Parse arrival deadline
	arrivalDeadline, err := time.Parse(time.RFC3339, arrivalDeadlineStr)
	if err != nil {
		s.logger.Error("Invalid arrival deadline format", "error", err)
		return bookingdomain.Cargo{}, bookingdomain.NewDomainValidationError("invalid arrival deadline format", err)
	}

	// Create new cargo (domain logic)
	cargo, err := bookingdomain.NewCargo(origin, destination, arrivalDeadline)
	if err != nil {
		s.logger.Error("Failed to create new cargo", "error", err)
		return bookingdomain.Cargo{}, err
	}

	// Store cargo (infrastructure)
	if err := s.cargoRepo.Store(cargo); err != nil {
		s.logger.Error("Failed to store cargo", "trackingId", cargo.GetTrackingId(), "error", err)
		return bookingdomain.Cargo{}, err
	}

	// Publish domain events
	s.publishCargoEvents(cargo)

	s.logger.Info("Cargo booked successfully", "trackingId", cargo.GetTrackingId())
	return cargo, nil
}

func (s *BookingApplicationService) publishCargoEvents(cargo bookingdomain.Cargo) {
	events := cargo.GetEvents()
	for _, event := range events {
		if err := s.eventPublisher.Publish(event); err != nil {
			s.logger.Error("Failed to publish event",
				"eventName", event.EventName(),
				"error", err)
		}
	}
	cargo.ClearEvents()
}
```

## Guidelines

1. **Authorization first**: Check permissions before any business logic
2. **Logging**: Log operation start, errors, and completion
3. **Error handling**: Wrap domain errors appropriately
4. **Event publishing**: Publish events after successful persistence
5. **No direct infrastructure**: Use injected ports only
6. **Stateless**: No mutable state in service
