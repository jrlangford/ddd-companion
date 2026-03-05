# Generator: go-hex

## Metadata

- **Language**: Go (1.21+)
- **Architecture**: Hexagonal (Ports & Adapters) with DDD
- **Version**: 1.0
- **Reference**: go-hex template project

## Features

- Domain-Driven Design with bounded contexts
- Hexagonal architecture (ports and adapters)
- Event-driven integration between contexts
- JWT-based authentication with domain-specific permissions
- In-memory repository implementations (mock-ready)
- Factory functions for test data generation

## Directory Structure

```
{project}/
├── api/                                  # TypeSpec API contracts (spec-first)
│   ├── main.tsp                          # Main entry point
│   ├── tspconfig.yaml                    # TypeSpec compiler config
│   ├── package.json                      # TypeSpec dependencies
│   ├── common/
│   │   └── types.tsp                     # Shared types (PersonId, pagination)
│   ├── {context-name}/
│   │   ├── models.tsp                    # Domain models for this context
│   │   └── endpoints.tsp                 # API endpoints
│   └── tsp-output/
│       └── openapi/
│           └── openapi.yaml              # Generated OpenAPI spec
├── cmd/
│   └── server/
│       └── main.go                       # Dependency wiring & bootstrap
├── internal/
│   ├── {context}/                        # Bounded context
│   │   ├── {context}domain/              # Domain entities, value objects, events
│   │   │   ├── {entity_snake}.go         # Entity with aggregate logic
│   │   │   ├── {value_object_snake}.go   # Value objects
│   │   │   ├── events.go                 # Domain events
│   │   │   └── errors.go                 # Domain-specific errors
│   │   ├── {context}application/         # Application services
│   │   │   ├── {context}_service.go      # Use case orchestration
│   │   │   └── permissions.go            # Domain-specific authorization
│   │   ├── {context}mock/                # Mock implementation
│   │   │   └── mock_{context}_application.go
│   │   └── ports/
│   │       ├── {context}primary/         # Inbound interfaces (use cases)
│   │       │   └── {context}_service.go
│   │       └── {context}secondary/       # Outbound interfaces (repos, services)
│   │           └── repositories.go
│   ├── adapters/
│   │   ├── driving/                      # Inbound adapters
│   │   │   └── httpadapter/
│   │   │       ├── dto.go                # Request/response DTOs (derived from TypeSpec)
│   │   │       ├── handlers.go           # HTTP handlers (implement TypeSpec contract)
│   │   │       ├── routes.go             # Route registration
│   │   │       └── httpmiddleware/
│   │   │           └── auth_middleware.go
│   │   ├── driven/                       # Outbound adapters
│   │   │   ├── in_memory_{entity}_repo/  # In-memory repositories (one per entity)
│   │   │   └── event_bus/                # Event publishing
│   │   └── integration/                  # Cross-context adapters (ACLs)
│   │       └── {context_a}_to_{context_b}_handler.go
│   └── support/                          # Shared infrastructure
│       ├── auth/                         # Authentication & claims
│       ├── basedomain/                   # Base entity, domain events
│       ├── config/                       # Environment configuration
│       ├── errors/                       # Common error types
│       ├── eventbus/                     # Event bus infrastructure
│       ├── logging/                      # Structured logging
│       ├── server/                       # HTTP server setup
│       └── validation/                   # Input validation
├── test/
│   ├── integration/                      # Integration tests
│   └── testdata/                         # Test data generation
├── go.mod
├── go.sum
└── README.md
```

## Naming Conventions

| Concept | Convention | Example |
|---------|------------|---------|
| Context package | lowercase | `booking` |
| Domain package | `{context}domain` | `bookingdomain` |
| Application package | `{context}application` | `bookingapplication` |
| Mock package | `{context}mock` | `bookingmock` |
| Primary ports package | `{context}primary` | `bookingprimary` |
| Secondary ports package | `{context}secondary` | `bookingsecondary` |
| Entity | PascalCase | `Cargo` |
| Entity ID type | `{Entity}Id` or descriptive | `TrackingId`, `VoyageNumber` |
| Value Object | PascalCase | `RouteSpecification` |
| Data container (VO group) | `{Entity}Data` | `CargoData` |
| Domain Event | PascalCase, past tense | `CargoBooked`, `CargoRouted` |
| Repository interface | `{Entity}Repository` | `CargoRepository` |
| Service interface | `{Context}Service` | `BookingService` |
| Application Service | `{Context}ApplicationService` | `BookingApplicationService` |
| Mock Application | `Mock{Context}Application` | `MockBookingApplication` |
| In-memory repo | `InMemory{Entity}Repository` | `InMemoryCargoRepository` |
| ACL adapter | `{Context}ServiceAdapter` | `RoutingServiceAdapter` |
| Event handler | `{Source}To{Target}EventHandler` | `HandlingToBookingEventHandler` |
| HTTP handler | `{Action}{Resource}Handler` | `BookCargoHandler` |
| DTO | `{Action}{Resource}Request/Response` | `BookCargoRequest` |

## Dependencies

### Required

```go
require (
    github.com/google/uuid v1.6.0
    github.com/go-playground/validator/v10 v10.22.0
)
```

### Optional (included by default)

```go
require (
    github.com/golang-jwt/jwt/v5 v5.2.1      // JWT authentication
    github.com/stretchr/testify v1.9.0       // Testing assertions
)
```

## Import Path Conventions

```go
// Domain layer - no external dependencies except support
import (
    "{module}/internal/support/basedomain"
    "{module}/internal/support/validation"
)

// Application layer - depends on domain and ports
import (
    "{module}/internal/{context}/{context}domain"
    "{module}/internal/{context}/ports/{context}primary"
    "{module}/internal/{context}/ports/{context}secondary"
    "{module}/internal/support/auth"
)

// Adapters - depend on ports and domain types
import (
    "{module}/internal/{context}/{context}domain"
    "{module}/internal/{context}/ports/{context}secondary"
)

// NEVER allowed:
// - Domain importing from application
// - Domain importing from adapters
// - Domain importing from another context's domain
// - Application importing from adapters
```

## Validation Rules

1. **Dependency direction**: Domain ← Application ← Adapters
2. **No cross-context domain imports**: Use ACL adapters
3. **Interface compliance**: Services must implement their port interfaces
4. **Event naming**: Past tense, describes what happened
5. **Constructor validation**: All entities/VOs validate in constructors
6. **Thread safety**: In-memory repos use sync.RWMutex

## FQBC-Driven API Design

HTTP handlers are generated directly from FQBC definitions and primary port interfaces. TypeSpec is generated separately as a documentation artifact — it produces OpenAPI specs and can generate client libraries.

```
                    ┌─────────────────┐
              ┌────►│  HTTP Adapters  │  Phase 4: Runnable handlers
              │     │  (Go handlers)  │
┌──────────┐  │     └─────────────────┘
│   FQBC   │──┤
│ + Ports  │  │     ┌─────────────────┐
└──────────┘  └────►│    TypeSpec     │  Phase 5: API documentation
                    │  (OpenAPI spec) │
                    └─────────────────┘
```

### Benefits

1. **No intermediary dependency**: Handlers don't wait for TypeSpec compilation — the skeleton is runnable sooner
2. **Single source of truth**: Both handlers and TypeSpec derive from the same FQBC, preventing drift
3. **TypeSpec is optional**: The skeleton compiles and runs without TypeSpec; OpenAPI/clients are additive
4. **Clear separation**: Domain logic (ports) vs API design (FQBC) vs documentation (TypeSpec)

### TypeSpec Location

TypeSpec files live at the project root level in the `api/` directory and serve as documentation artifacts (not handler generation dependencies):
- `api/main.tsp` - Main entry point importing all contexts
- `api/common/types.tsp` - Shared types (PersonId, pagination, errors)
- `api/{context-name}/models.tsp` - Domain models for each context
- `api/{context-name}/endpoints.tsp` - API endpoints for each context
- `api/tsp-output/openapi/openapi.yaml` - Generated OpenAPI spec

## Phase Execution Order

These steps map to SKILL.md execution phases as shown:

| # | Generator Step | SKILL.md Phase |
|---|---------------|----------------|
| 1 | `support` - Generate support packages | Phase 2 |
| 2 | `domain` - Generate domain layer for each context | Phase 3a |
| 3 | `ports` - Generate port interfaces | Phase 3b |
| 4 | `application` - Generate application services | Phase 3c |
| 5 | `adapters/driven` - Generate repositories and event bus | Phase 3d |
| 6 | `adapters/integration` - Generate ACL adapters | Phase 3d |
| 7 | `mock` - Generate mock applications | Phase 3e |
| 8 | `adapters/driving` - Generate HTTP handlers from FQBC + primary ports | Phase 4 |
| 9 | `api-contracts` - Generate TypeSpec definitions (documentation only) | Phase 5 |
| 10 | `main` - Wire dependencies in main.go | Phase 6 |

Steps 2–7 are executed per context (complete one context before starting the next). Steps 8–10 run after all contexts are complete.
