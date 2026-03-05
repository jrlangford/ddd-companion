# Mock Application Patterns

## Input

From manifest and BCR:
- Context name
- Entities and their properties
- Application service interface

## Output Files

For each context:
- `internal/{context}/{context}mock/mock_{context}_application.go`

## Patterns

### Mock Application Pattern

```go
package {context}mock

import (
	"context"
	"log/slog"
	"math/rand"

	"{module}/internal/{context}/{context}application"
	"{module}/internal/{context}/{context}domain"
	"{module}/internal/{context}/ports/{context}primary"
	"{module}/internal/{context}/ports/{context}secondary"
	"{module}/internal/support/auth"
)

// Mock{Context}Application embeds the real application service, wired with in-memory adapters.
// It satisfies the same primary port interface as the real service, adding only test data
// population capabilities. In mock mode, this IS the service that handlers use.
type Mock{Context}Application struct {
	*{context}application.{Context}ApplicationService
	logger *slog.Logger
	random *rand.Rand
}

// NewMock{Context}Application creates a mock {context} application with embedded real application service
func NewMock{Context}Application(
	{entity}Repo {context}secondary.{Entity}Repository,
	{{if .HasExternalService}}
	{external}Service {context}secondary.{External}Service,
	{{end}}
	eventPublisher {context}secondary.EventPublisher,
	logger *slog.Logger,
	seed int64,
) *Mock{Context}Application {
	realApp := {context}application.New{Context}ApplicationService(
		{entity}Repo,
		{{if .HasExternalService}}
		{external}Service,
		{{end}}
		eventPublisher,
		logger,
	)

	return &Mock{Context}Application{
		{Context}ApplicationService: realApp,
		logger:                      logger,
		random:                      rand.New(rand.NewSource(seed)),
	}
}

// PopulateTest{Entities} creates test {entity} data using business logic through the application layer
func (m *Mock{Context}Application) PopulateTest{Entities}(ctx context.Context, scenarios []Test{Entity}Scenario) ([]{context}domain.{Entity}, error) {
	m.logger.Info("Populating test {entities} through {context} application", "scenarios", len(scenarios))

	// Create authenticated context for internal operations
	testCtx := m.createTestContext(ctx)

	var {entities} []{context}domain.{Entity}

	for _, scenario := range scenarios {
		// Use the real application service to create {entity}
		{entity}, err := m.{Context}ApplicationService.Create{Entity}(
			testCtx,
			scenario.{Params}...,
		)
		if err != nil {
			m.logger.Error("Failed to create test {entity}", "error", err, "scenario", scenario)
			return nil, err
		}

		{entities} = append({entities}, {entity})
		m.logger.Debug("Created test {entity}", "id", {entity}.Get{EntityId}())
	}

	m.logger.Info("Successfully populated test {entities}", "count", len({entities}))
	return {entities}, nil
}

// Generate{Entity}Scenarios creates realistic {entity} scenarios
func (m *Mock{Context}Application) Generate{Entity}Scenarios(count int) []Test{Entity}Scenario {
	m.logger.Info("Generating {entity} scenarios", "count", count)

	scenarios := make([]Test{Entity}Scenario, 0, count)

	for i := 0; i < count; i++ {
		scenario := Test{Entity}Scenario{
			// Generate realistic random data
			{{range .ScenarioFields}}
			{FieldName}: m.generate{FieldType}(),
			{{end}}
		}

		scenarios = append(scenarios, scenario)
	}

	m.logger.Info("Generated {entity} scenarios", "count", len(scenarios))
	return scenarios
}

// createTestContext creates an authenticated context for test operations
func (m *Mock{Context}Application) createTestContext(ctx context.Context) context.Context {
	// Create test claims with admin permissions
	claims, _ := auth.NewClaims(
		"test-user",
		"test-system",
		"test@example.com",
		[]string{string(auth.RoleAdmin)},
		map[string]string{"test": "true"},
	)

	return context.WithValue(ctx, auth.ClaimsContextKey, claims)
}

// Test{Entity}Scenario represents a test scenario for {entity} creation
type Test{Entity}Scenario struct {
	{{range .ScenarioFields}}
	{FieldName} {FieldType}
	{{end}}
}

// Ensure Mock{Context}Application implements primary ports
var _ {context}primary.{Context}Service = (*Mock{Context}Application)(nil)
```

## Example: Mock Booking Application

```go
package bookingmock

import (
	"context"
	"fmt"
	"log/slog"
	"math/rand"
	"time"

	"myproject/internal/booking/bookingapplication"
	"myproject/internal/booking/bookingdomain"
	"myproject/internal/booking/ports/bookingprimary"
	"myproject/internal/booking/ports/bookingsecondary"
	"myproject/internal/support/auth"
)

type MockBookingApplication struct {
	*bookingapplication.BookingApplicationService
	logger *slog.Logger
	random *rand.Rand
}

func NewMockBookingApplication(
	cargoRepo bookingsecondary.CargoRepository,
	routingService bookingsecondary.RoutingService,
	eventPublisher bookingsecondary.EventPublisher,
	logger *slog.Logger,
	seed int64,
) *MockBookingApplication {
	realApp := bookingapplication.NewBookingApplicationService(cargoRepo, routingService, eventPublisher, logger)

	return &MockBookingApplication{
		BookingApplicationService: realApp,
		logger:                    logger,
		random:                    rand.New(rand.NewSource(seed)),
	}
}

func (m *MockBookingApplication) PopulateTestCargo(ctx context.Context, scenarios []TestCargoScenario) ([]bookingdomain.Cargo, error) {
	m.logger.Info("Populating test cargo through booking application", "scenarios", len(scenarios))

	testCtx := m.createTestContext(ctx)
	var cargos []bookingdomain.Cargo

	for _, scenario := range scenarios {
		// Generate arrival deadline in the future (7-60 days from now)
		daysInFuture := 7 + m.random.Intn(54)
		arrivalDeadline := time.Now().AddDate(0, 0, daysInFuture)

		cargo, err := m.BookingApplicationService.BookNewCargo(
			testCtx,
			scenario.Origin,
			scenario.Destination,
			arrivalDeadline.Format(time.RFC3339),
		)
		if err != nil {
			m.logger.Error("Failed to create test cargo", "error", err)
			return nil, fmt.Errorf("failed to create test cargo: %w", err)
		}

		// Assign itinerary if provided
		if scenario.Itinerary != nil {
			_ = m.BookingApplicationService.AssignRouteToCargo(testCtx, cargo.GetTrackingId(), *scenario.Itinerary)
		}

		cargos = append(cargos, cargo)
	}

	m.logger.Info("Successfully populated test cargo", "count", len(cargos))
	return cargos, nil
}

func (m *MockBookingApplication) GenerateCargoScenarios(locations []string, count int) []TestCargoScenario {
	if len(locations) < 2 {
		return nil
	}

	scenarios := make([]TestCargoScenario, 0, count)

	for i := 0; i < count; i++ {
		originIdx := m.random.Intn(len(locations))
		destIdx := m.random.Intn(len(locations))
		for destIdx == originIdx {
			destIdx = m.random.Intn(len(locations))
		}

		scenarios = append(scenarios, TestCargoScenario{
			Origin:      locations[originIdx],
			Destination: locations[destIdx],
		})
	}

	return scenarios
}

func (m *MockBookingApplication) createTestContext(ctx context.Context) context.Context {
	claims, _ := auth.NewClaims(
		"test-user",
		"test-system",
		"test@example.com",
		[]string{string(auth.RoleAdmin)},
		nil,
	)
	return context.WithValue(ctx, auth.ClaimsContextKey, claims)
}

type TestCargoScenario struct {
	Origin      string
	Destination string
	Itinerary   *bookingdomain.Itinerary
}

var _ bookingprimary.BookingService = (*MockBookingApplication)(nil)
```

## APP_MODE Wiring Pattern

The `cmd/server/main.go` entry point uses the `APP_MODE` environment variable to switch between live and mock implementations.

The mock application **embeds** the real application service and satisfies the same primary port interface. In mock mode, `main.go` creates the mock app (which internally instantiates the real service with in-memory adapters), populates test data through it, and wires handlers to it. Only one service instance exists per context in either mode.

```go
package main

import (
	"context"
	"log/slog"
	"os"

	// ... context imports
)

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	appMode := os.Getenv("APP_MODE") // "mock" or "" (live)

	// Repositories (in-memory for walking skeleton — both modes)
	{entity}Repo := inmemory.NewInMemory{Entity}Repository()
	eventBus := eventbus.NewInMemoryEventBus(logger)

	// Single service instance — declared as the primary port interface
	var {context}Svc {context}primary.{Context}Service

	if appMode == "mock" {
		logger.Info("Running in mock mode — populating test data")
		mockApp := {context}mock.NewMock{Context}Application(
			{entity}Repo, eventBus, logger, 42,
		)
		scenarios := mockApp.Generate{Entity}Scenarios(10)
		if _, err := mockApp.PopulateTest{Entities}(context.Background(), scenarios); err != nil {
			logger.Error("Failed to populate test data", "error", err)
			os.Exit(1)
		}
		{context}Svc = mockApp
	} else {
		{context}Svc = {context}application.New{Context}ApplicationService(
			{entity}Repo, eventBus, logger,
		)
	}

	// Wire handlers to whichever service was created
	handler := httpadapter.NewHandler({context}Svc, logger)

	// Start server
	// ...
}
```

**Key points**:
- Only one service instance exists per context — either the real app or the mock app
- The mock app embeds the real service, so all business logic executes identically in both modes
- Mock mode populates data through the embedded service, then the same instance serves requests
- Handlers accept the primary port interface, so they work with either implementation

## Test Setup Through Application Services

Tests should create their required state by calling application services during setup — not by using static fixture data. This ensures business rules are validated during setup and prevents fixture drift when domain rules change.

### Test Helper Pattern

Tests compose thin helper functions that call application services to build up state:

```go
package booking_test

import (
	"context"
	"testing"

	"myproject/internal/booking/bookingmock"
	"myproject/internal/support/auth"
)

// Helper: create an authenticated test context
func testContext(t *testing.T, roles ...string) context.Context {
	t.Helper()
	claims, _ := auth.NewClaims("test-user", "test-system", "test@example.com", roles, nil)
	return context.WithValue(context.Background(), auth.ClaimsContextKey, claims)
}

// Helper: create a booked cargo and return its tracking ID
func createBookedCargo(t *testing.T, app *bookingmock.MockBookingApplication, origin, dest string) string {
	t.Helper()
	ctx := testContext(t, string(auth.RoleAdmin))
	cargo, err := app.BookNewCargo(ctx, origin, dest, "2026-12-31T00:00:00Z")
	if err != nil {
		t.Fatalf("failed to create test cargo: %v", err)
	}
	return cargo.GetTrackingId()
}

// Helper: create a cargo with an assigned route
func createRoutedCargo(t *testing.T, app *bookingmock.MockBookingApplication, origin, dest string) string {
	t.Helper()
	trackingID := createBookedCargo(t, app, origin, dest)
	ctx := testContext(t, string(auth.RoleAdmin))
	if err := app.AssignRouteToCargo(ctx, trackingID, someItinerary()); err != nil {
		t.Fatalf("failed to assign route: %v", err)
	}
	return trackingID
}

func TestCancelBooking(t *testing.T) {
	app := setupMockApp(t)

	// Setup: create the state this test needs via application services
	trackingID := createBookedCargo(t, app, "USNYC", "JPTYO")

	// Act
	ctx := testContext(t, string(auth.RoleOperator))
	err := app.CancelBooking(ctx, trackingID)

	// Assert
	if err != nil {
		t.Errorf("expected cancellation to succeed: %v", err)
	}
}
```

**Key principles:**
- Helpers call application services, never repositories directly
- Each test creates exactly the state it needs — no shared mutable fixtures
- If setup fails, the test fails fast with a clear message — this validates your domain assumptions
- Helpers compose: `createRoutedCargo` calls `createBookedCargo`

### Mock External Service Pattern

When a bounded context depends on an external service (via secondary port), provide a mock implementation that tests can configure:

```go
package bookingmock

import (
	"myproject/internal/booking/bookingdomain"
	"myproject/internal/booking/ports/bookingsecondary"
)

// MockRoutingService implements the RoutingService secondary port for testing
type MockRoutingService struct {
	routes map[string]bookingdomain.Itinerary
}

func NewMockRoutingService() *MockRoutingService {
	return &MockRoutingService{
		routes: make(map[string]bookingdomain.Itinerary),
	}
}

// ConfigureRoute sets up a route that the mock will return for a given origin-destination pair
func (m *MockRoutingService) ConfigureRoute(origin, destination string, itinerary bookingdomain.Itinerary) {
	m.routes[origin+":"+destination] = itinerary
}

// FindOptimalRoute implements bookingsecondary.RoutingService
func (m *MockRoutingService) FindOptimalRoute(origin, destination string) (bookingdomain.Itinerary, error) {
	key := origin + ":" + destination
	if route, ok := m.routes[key]; ok {
		return route, nil
	}
	return bookingdomain.Itinerary{}, fmt.Errorf("no route configured for %s → %s", origin, destination)
}

var _ bookingsecondary.RoutingService = (*MockRoutingService)(nil)
```

**Key principles:**
- Mock implements the same secondary port interface as the real adapter
- Tests configure the mock's responses before acting — no static data
- Missing configuration produces clear errors, not silent defaults

## Guidelines

1. **Embed real service**: Mock embeds the actual application service
2. **Setup through services**: Tests create state by calling application services, not by populating repositories directly
3. **No static fixtures**: Avoid global test data generators — each test creates what it needs
4. **Composable helpers**: Build thin `t.Helper()` functions that compose service calls
5. **Mock external dependencies**: Implement secondary port interfaces with configurable mocks
6. **Admin context**: Test setup operations use admin permissions
7. **Seeded randomization**: Use seeded random for reproducible scenario generation in mock mode
8. **Port compliance**: Mock must implement same interfaces as real service
