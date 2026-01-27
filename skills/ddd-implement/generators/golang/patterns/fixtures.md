# Test Data Fixtures Patterns

## Input

From manifest and BCR:
- All contexts and their entities
- Relationships between contexts
- Sample data requirements

## Output Files

- `test/testdata/generator.go` - Main test data generator
- `test/testdata/scenarios.go` - Predefined test scenarios
- `test/mock/test_environment.go` - Mock test environment orchestration

## Patterns

### Test Data Generator Pattern

```go
package testdata

import (
	"context"
	"log/slog"
	"math/rand"
	"time"

	{{range .Contexts}}
	"{module}/internal/{context}/{context}mock"
	{{end}}
)

// TestDataGenerator coordinates test data generation across all contexts
type TestDataGenerator struct {
	{{range .Contexts}}
	{context}App *{context}mock.Mock{Context}Application
	{{end}}
	logger *slog.Logger
	random *rand.Rand
}

// NewTestDataGenerator creates a new test data generator
func NewTestDataGenerator(
	{{range .Contexts}}
	{context}App *{context}mock.Mock{Context}Application,
	{{end}}
	logger *slog.Logger,
	seed int64,
) *TestDataGenerator {
	return &TestDataGenerator{
		{{range .Contexts}}
		{context}App: {context}App,
		{{end}}
		logger: logger,
		random: rand.New(rand.NewSource(seed)),
	}
}

// GenerateCompleteTestData generates a complete set of test data
// maintaining referential integrity across contexts
func (g *TestDataGenerator) GenerateCompleteTestData(ctx context.Context) error {
	g.logger.Info("Generating complete test data set")

	// Phase 1: Generate base reference data (no dependencies)
	{{range .BaseContexts}}
	if err := g.generate{Context}Data(ctx); err != nil {
		return err
	}
	{{end}}

	// Phase 2: Generate dependent data
	{{range .DependentContexts}}
	if err := g.generate{Context}Data(ctx); err != nil {
		return err
	}
	{{end}}

	// Phase 3: Generate integration scenarios
	if err := g.generateIntegrationScenarios(ctx); err != nil {
		return err
	}

	g.logger.Info("Complete test data generation finished")
	return nil
}

{{range .Contexts}}
func (g *TestDataGenerator) generate{Context}Data(ctx context.Context) error {
	g.logger.Info("Generating {context} test data")

	scenarios := g.{context}App.Generate{Entity}Scenarios({scenario_count})
	_, err := g.{context}App.PopulateTest{Entities}(ctx, scenarios)
	if err != nil {
		g.logger.Error("Failed to generate {context} data", "error", err)
		return err
	}

	return nil
}
{{end}}

func (g *TestDataGenerator) generateIntegrationScenarios(ctx context.Context) error {
	g.logger.Info("Generating integration test scenarios")

	// Generate scenarios that exercise cross-context integration
	// Example: Create cargo, find routes, assign route, register handling events

	return nil
}
```

### Test Scenarios Pattern

```go
package testdata

import (
	"time"

	{{range .Contexts}}
	"{module}/internal/{context}/{context}domain"
	{{end}}
)

// PredefinedScenarios contains well-known test scenarios
var PredefinedScenarios = struct {
	{{range .ScenarioCategories}}
	{CategoryName} {CategoryName}Scenarios
	{{end}}
}{
	{{range .ScenarioCategories}}
	{CategoryName}: default{CategoryName}Scenarios(),
	{{end}}
}

{{range .ScenarioCategories}}
type {CategoryName}Scenarios struct {
	{{range .Scenarios}}
	{ScenarioName} {ScenarioType}
	{{end}}
}

func default{CategoryName}Scenarios() {CategoryName}Scenarios {
	return {CategoryName}Scenarios{
		{{range .Scenarios}}
		{ScenarioName}: {scenario_initialization},
		{{end}}
	}
}
{{end}}
```

### Mock Test Environment Pattern

```go
package mock

import (
	"context"
	"log/slog"

	"{module}/internal/adapters/driven/event_bus"
	{{range .Contexts}}
	"{module}/internal/adapters/driven/in_memory_{entity}_repo"
	"{module}/internal/{context}/{context}mock"
	{{end}}
	"{module}/internal/adapters/integration"
	"{module}/internal/support/logging"
	"{module}/test/testdata"
)

// TestEnvironment provides a fully wired mock environment for testing
type TestEnvironment struct {
	// Repositories
	{{range .Repositories}}
	{RepoName} *in_memory_{entity}_repo.InMemory{Entity}Repository
	{{end}}

	// Event infrastructure
	EventBus *event_bus.InMemoryEventBus

	// Application services (mock)
	{{range .Contexts}}
	{Context}App *{context}mock.Mock{Context}Application
	{{end}}

	// Integration handlers
	{{range .IntegrationHandlers}}
	{HandlerName} *integration.{HandlerType}
	{{end}}

	// Test data generator
	DataGenerator *testdata.TestDataGenerator

	Logger *slog.Logger
}

// NewTestEnvironment creates a new fully-wired test environment
func NewTestEnvironment(seed int64) *TestEnvironment {
	logger := logging.NewLogger("debug")

	// Create repositories
	{{range .Repositories}}
	{repoVar} := in_memory_{entity}_repo.NewInMemory{Entity}Repository()
	{{end}}

	// Create event bus
	eventBus := event_bus.NewInMemoryEventBus(logger)

	// Create application services (will be wired below)
	{{range .Contexts}}
	var {context}App *{context}mock.Mock{Context}Application
	{{end}}

	// Wire dependencies in correct order
	{{range .WiringOrder}}
	{wiring_code}
	{{end}}

	// Create integration handlers and subscribe to events
	{{range .IntegrationHandlers}}
	{handler_var} := integration.New{HandlerType}({handler_dependencies})
	eventBus.Subscribe("{event_type}", {handler_var})
	{{end}}

	// Create test data generator
	dataGenerator := testdata.NewTestDataGenerator(
		{{range .Contexts}}
		{context}App,
		{{end}}
		logger,
		seed,
	)

	return &TestEnvironment{
		{{range .Repositories}}
		{RepoName}: {repoVar},
		{{end}}
		EventBus: eventBus,
		{{range .Contexts}}
		{Context}App: {context}App,
		{{end}}
		{{range .IntegrationHandlers}}
		{HandlerName}: {handler_var},
		{{end}}
		DataGenerator: dataGenerator,
		Logger:        logger,
	}
}

// Setup populates the test environment with test data
func (e *TestEnvironment) Setup(ctx context.Context) error {
	return e.DataGenerator.GenerateCompleteTestData(ctx)
}

// Reset clears all data from the test environment
func (e *TestEnvironment) Reset() {
	// Recreate repositories to clear data
	{{range .Repositories}}
	e.{RepoName} = in_memory_{entity}_repo.NewInMemory{Entity}Repository()
	{{end}}
}
```

## Example: Cargo Shipping Test Environment

```go
package mock

import (
	"context"
	"log/slog"

	"myproject/internal/adapters/driven/event_bus"
	"myproject/internal/adapters/driven/in_memory_cargo_repo"
	"myproject/internal/adapters/driven/in_memory_voyage_repo"
	"myproject/internal/adapters/driven/in_memory_location_repo"
	"myproject/internal/adapters/driven/in_memory_handling_repo"
	"myproject/internal/adapters/integration"
	"myproject/internal/booking/bookingmock"
	"myproject/internal/routing/routingmock"
	"myproject/internal/handling/handlingmock"
	"myproject/internal/support/logging"
	"myproject/test/testdata"
)

type TestEnvironment struct {
	CargoRepo      *in_memory_cargo_repo.InMemoryCargoRepository
	VoyageRepo     *in_memory_voyage_repo.InMemoryVoyageRepository
	LocationRepo   *in_memory_location_repo.InMemoryLocationRepository
	HandlingRepo   *in_memory_handling_repo.InMemoryHandlingEventRepository
	EventBus       *event_bus.InMemoryEventBus
	BookingApp     *bookingmock.MockBookingApplication
	RoutingApp     *routingmock.MockRoutingApplication
	HandlingApp    *handlingmock.MockHandlingApplication
	DataGenerator  *testdata.TestDataGenerator
	Logger         *slog.Logger
}

func NewTestEnvironment(seed int64) *TestEnvironment {
	logger := logging.NewLogger("debug")

	// Repositories
	cargoRepo := in_memory_cargo_repo.NewInMemoryCargoRepository()
	voyageRepo := in_memory_voyage_repo.NewInMemoryVoyageRepository()
	locationRepo := in_memory_location_repo.NewInMemoryLocationRepository()
	handlingRepo := in_memory_handling_repo.NewInMemoryHandlingEventRepository()

	// Event bus
	eventBus := event_bus.NewInMemoryEventBus(logger)

	// Routing app (no dependencies on other contexts)
	routingApp := routingmock.NewMockRoutingApplication(voyageRepo, locationRepo, eventBus, logger, seed)

	// Routing service adapter for booking context
	routingServiceAdapter := integration.NewRoutingServiceAdapter(routingApp)

	// Booking app (depends on routing via adapter)
	bookingApp := bookingmock.NewMockBookingApplication(cargoRepo, routingServiceAdapter, eventBus, logger, seed)

	// Handling app
	handlingApp := handlingmock.NewMockHandlingApplication(handlingRepo, eventBus, logger, seed)

	// Integration: Handling → Booking event handler
	handlingToBookingHandler := integration.NewHandlingToBookingEventHandler(bookingApp, logger)
	eventBus.Subscribe("handling.event_registered", handlingToBookingHandler)

	// Test data generator
	dataGenerator := testdata.NewTestDataGenerator(bookingApp, routingApp, handlingApp, logger, seed)

	return &TestEnvironment{
		CargoRepo:     cargoRepo,
		VoyageRepo:    voyageRepo,
		LocationRepo:  locationRepo,
		HandlingRepo:  handlingRepo,
		EventBus:      eventBus,
		BookingApp:    bookingApp,
		RoutingApp:    routingApp,
		HandlingApp:   handlingApp,
		DataGenerator: dataGenerator,
		Logger:        logger,
	}
}

func (e *TestEnvironment) Setup(ctx context.Context) error {
	return e.DataGenerator.GenerateCompleteTestData(ctx)
}
```

## Guidelines

1. **Factory functions over static data**: Generate data dynamically
2. **Seeded randomization**: Reproducible test runs
3. **Respect dependencies**: Generate base data before dependent data
4. **Integration scenarios**: Exercise cross-context flows
5. **Easy reset**: Support clearing data between tests
