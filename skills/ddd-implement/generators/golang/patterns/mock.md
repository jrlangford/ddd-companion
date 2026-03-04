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

// Mock{Context}Application embeds the real application service but provides test data population capabilities
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

The `cmd/server/main.go` entry point uses the `APP_MODE` environment variable to switch between live and mock implementations. Both modes use the same repositories and real application services — mock mode additionally populates test data at startup.

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

	// Repositories are the same in both modes (in-memory for walking skeleton)
	{entity}Repo := inmemory.NewInMemory{Entity}Repository()
	eventBus := eventbus.NewInMemoryEventBus(logger)

	// Application service is always the real one
	{context}Svc := {context}application.New{Context}ApplicationService(
		{entity}Repo, eventBus, logger,
	)

	// In mock mode, populate test data through the application layer
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
	}

	// Wire handlers — same service reference regardless of mode
	handler := httpadapter.NewHandler({context}Svc, logger)

	// Start server
	// ...
}
```

**Key points**:
- Both modes use the same application service and repositories
- Mock mode only adds test data population at startup — it does not swap implementations
- The `Mock{Context}Application` embeds the real service, so populated data flows through real business logic

## Guidelines

1. **Embed real service**: Mock embeds the actual application service
2. **Seeded randomization**: Use seeded random for reproducibility
3. **Admin context**: Test operations use admin permissions
4. **Factory functions**: Generate realistic scenarios programmatically
5. **Port compliance**: Mock must implement same interfaces as real service
