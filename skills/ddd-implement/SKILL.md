---
name: ddd-implement
description: Transform BCR bounded context definitions into a walking skeleton - a runnable Go hexagonal architecture application with validated DDD boundaries. Use after completing BCR workflow to generate implementation code. Also validates existing projects against DDD standards.
---

# ddd-implement Skill

Transform bounded context definitions into a **walking skeleton**: a minimal, runnable application that connects all architectural layers end-to-end with validated boundaries.

## Modes

This skill operates in two modes:

### Generate Mode (default)

Takes BCR workspace definitions and generates a walking skeleton. This is the primary workflow described in this document.

### Validate Mode

Audits an existing project against the DDD standards defined by this skill's generator patterns. Use this to check structural conformance, naming conventions, dependency direction, cross-context isolation, and pattern compliance.

**Trigger**: The user asks to validate, audit, review, or check an existing project against DDD standards.

**Reference**: See `validate.md` for the complete validation workflow, phase-by-phase checklist, and report format.

**Quick summary**:
1. Discovers contexts from the project structure (or manifest if available)
2. Validates each layer (domain, ports, application, adapters, mock) against the rules in `generators/{generator}/patterns/*.md`
3. Checks cross-cutting concerns (dependency direction, cross-context isolation, API contract alignment)
4. Writes a `ddd-validation-report.md` to the project root with findings at error/warning/info severity

Supports partial validation by context name or layer.

---

## Overview

This skill takes BCR (Bounded Context Review) workspace definitions and generates:
1. Support infrastructure (base types, auth, validation)
2. Domain layer with entities, value objects, and events
3. Port interfaces (primary and secondary)
4. Application layer with use case orchestration
5. Driven adapters (repositories, event bus)
6. Mock implementations with test data factories
7. **Driving adapters** (HTTP handlers generated from FQBC definitions)
8. **TypeSpec API documentation** (OpenAPI specs and client generation)
9. Main wiring and validated boundaries

## Goals

1. **Walking skeleton for iterative development**: Generate a runnable application with all layers connected (domain → ports → application → adapters → main) but minimal business logic. Developers add flesh to the bones without structural refactoring.
2. **Mock server for frontend teams**: The skeleton can run in mock mode (`APP_MODE=mock`), providing realistic API responses for parallel frontend development.
3. **API documentation**: TypeSpec generates OpenAPI specs and client libraries from the same FQBC definitions that drive handler generation.

## Prerequisites

Before running this skill, you must have a completed BCR workspace (from `/ddd-model` skill).

### Input Contract

The following artifacts must exist in `ddd-workspace/`:

| Artifact | Path | Required Fields |
|----------|------|-----------------|
| BCR Manifest | `ddd-model.manifest.json` | `currentPhase: "complete"` |
| | | `phases.contextDiscovery.contextsIdentified` — list of context names |
| | | `phases.fqbcGeneration.contexts` — per-context status (all `"complete"`) |
| | | `authorization.pattern` — must be `"permissions-object"` |
| | | `prd.path` — PRD location for traceability |
| Context Map | `bcr/context-map.md` | Upstream/downstream relationships between contexts |
| FQBCs | `fqbc/{context-name}.md` (one per context) | Sections 1–9 per `fqbc-template.md` |

**FQBC sections consumed by each phase**:

| Phase | FQBC Sections Read |
|-------|-------------------|
| Phase 3 (Domain) | §4 Domain Model — entities, value objects, events, business rules |
| Phase 3 (Ports) | §6 Context Contract — commands, queries; §8 Context Relationships — external service deps |
| Phase 3 (Application) | §5 Authorization — permission requirements; §3 Required Behaviors — use cases |
| Phase 4 (HTTP Handlers) | §7 API Binding — routes, methods, request/response schemas; §6 Context Contract — failure scenarios |
| Phase 5 (TypeSpec) | §4 Domain Model — model/enum definitions; §6 Context Contract — endpoints; §7 API Binding — route patterns |

---

## API Design: FQBC-Driven Handlers + TypeSpec Documentation

HTTP handlers are generated directly from FQBC definitions and primary port interfaces. TypeSpec is generated separately as a documentation artifact.

Both handlers and TypeSpec derive from the same FQBC, preventing drift. Handlers don't wait for TypeSpec compilation — the skeleton is runnable sooner. TypeSpec is optional; the skeleton compiles and runs without it.

**TypeSpec role**: Generates OpenAPI specs for Swagger UI visualization, can generate typed client libraries, and validates the public API surface.

---

## Multi-Session Design

This workflow spans multiple sessions. Context window limits will be reached during generation of complex systems.

**Reference**: See `session-management.md` for subagent strategies, prompt templates, session resumption/stop protocols, and error recovery procedures.

**Key principles**: Manifest is the source of truth. Process one context at a time. Use subagents for context isolation. Checkpoint after each operation.

---

## Manifest Structure

The manifest (`ddd-workspace/ddd-implement.manifest.json`) tracks granular progress for reliable session resumption.

**Reference**: See `manifest-guide.md` for the full manifest example, field descriptions, and status transition diagrams. For JSON Schema validation, see `manifest.schema.json`.

**Phase progression**: `support → contexts → drivingAdapters → apiContracts → mainWiring → validation → complete`

---

## Session Resumption Protocol

**Reference**: See `session-management.md` § Session Resumption Protocol for the full step-by-step procedure.

**Quick summary**: Read manifest → check `currentPhase` and `currentContext` → identify first incomplete item → execute with checkpointing → verify build before proceeding.

---

## Session Stop Protocol

**Reference**: See `session-management.md` § Session Stop Protocol for when to stop, pre-stop checklist, and handoff report format.

**Key rule**: Do not stop mid-layer. Complete the current context's layer set or roll back to the last checkpoint.

---

## Execution Phases

### Phase 1: Initialize Manifest

**Trigger**: No `ddd-workspace/ddd-implement.manifest.json` exists

**Actions**:
1. Read BCR workspace manifest (`ddd-workspace/ddd-model.manifest.json`). Required fields:
   - `currentPhase` — must be `"complete"`
   - `phases.contextDiscovery.contextsIdentified` — list of context names
   - `phases.fqbcGeneration.contexts` — per-context status and file paths
   - `authorization.pattern` — authorization pattern (currently only `"permissions-object"`)
   - `prd.path` — PRD location for traceability
2. Parse each FQBC document (paths from `phases.fqbcGeneration.contexts`)
3. **Prompt user for Go module path** (do NOT default to directory name)
   - Use `AskUserQuestion` tool to ask: "What Go module path should be used for this project?"
   - Example options: `github.com/org/project-name`, `company.com/team/service`
4. Initialize Go module with `go mod init {user-provided-path}`
5. Create manifest with all contexts in `pending` status
6. Set `currentPhase = "support"`

**Checkpoint**: Write manifest immediately

### Phase 2: Generate Support Infrastructure (`support`)

**Trigger**: `infrastructure.support.status = "pending"`

**Actions**:
1. Generate `internal/support/basedomain/`
2. Generate `internal/support/validation/`
3. Generate `internal/support/auth/`
4. Generate `internal/support/config/`
5. Generate `internal/support/errors/`
6. Generate `internal/support/logging/`
7. Generate `internal/support/eventbus/`
8. Generate `internal/support/server/`

**Checkpoint**: Run `go build ./...` to verify. Update `infrastructure.support.status = "complete"` and `infrastructure.eventBus.status = "complete"` with their respective `files` arrays.

**Reference**: `generators/golang/generator.md`

### Phase 3: Generate Contexts (`contexts`)

#### Prerequisite: Determine Context Order

Before starting Phase 3, determine the order in which contexts should be generated:

1. Read `bcr/context-map.md` and identify all upstream/downstream relationships
2. Build a dependency graph: contexts that consume from other contexts are downstream
3. **Generate upstream contexts before their downstream consumers** so that domain types and port interfaces exist when downstream ACL adapters need to reference them
4. Contexts with no dependencies (or only external dependencies) can be generated in any order
5. For Partnership or Shared Kernel relationships: generate both contexts in the same session when possible, starting with the one that defines the shared types

**Example ordering**:
| Context | Dependencies | Order |
|---------|-------------|-------|
| Identity (upstream) | None | 1 |
| Ordering (downstream of Identity) | Identity | 2 |
| Fulfillment (downstream of Ordering) | Ordering | 3 |

If the manifest already has some contexts complete, skip them and continue with the next incomplete context in dependency order.

**For each context where `status != "complete"`** (in dependency order):

Use a **subagent** to process the entire context (see `session-management.md` for prompt template):

1. Set context.status = "in_progress"
2. Generate domain layer → update phases.domain, generatedFiles.domain
3. Generate ports → update phases.ports, generatedFiles.ports
4. Generate application → update phases.application, generatedFiles.application
5. Generate driven adapters (repositories, event publisher, ACL/integration adapters per §3d) → update phases.drivenAdapters, generatedFiles.drivenAdapters
6. Generate mock → update phases.mock, generatedFiles.mock
7. Run `go build ./...` to verify
8. Set context.status = "complete"
9. Add entry to history

**IMPORTANT**: Complete ONE context fully before starting the next.

**NOTE**: Driving adapters (HTTP handlers) are NOT generated in this phase. They are generated in Phase 4 after all contexts are complete.

#### 3a: Domain Layer
- Entity ID types (scalars wrapping UUID)
- Entities with BaseEntity embedding
- Value objects with validation
- Domain events
- Domain errors
- **Preserve traceability**: When generating application services that implement behaviors, include a comment linking to the FQBC behavior ID, PRD functional requirement, and source document reference (from FQBC Section 9). Use `—` when no source ref exists. Example: `// Implements: BH-01 | FR: FR-ordering-01 | Source: US-789`

**Reference**: `generators/golang/patterns/domain.md`

#### 3b: Ports (interfaces only — no domain type definitions)
- Primary port interfaces (derived from Commands/Queries in the BCR; all parameter/return types must be domain types imported from `{context}domain`)
- Secondary port interfaces (repositories)
- External service interfaces (for integrations)

**Reference**: `generators/golang/patterns/ports.md`

#### 3c: Application Layer
- Application service implementing primary ports
- Permission checks from FQBC authorization rules
- TODO markers for business logic

**Reference**: `generators/golang/patterns/application.md`

#### 3d: Driven Adapters
- In-memory repositories for this context
- Event publisher adapter for this context
- ACL adapters for cross-context integration:
  1. Read this context's FQBC Section 8 (Context Relationships) → Upstream Dependencies table
  2. For each upstream dependency: the secondary port interface was already generated in Phase 3b (External Service Interface Pattern). Now generate the ACL adapter that implements it using the ACL Service Adapter Pattern from `adapters.md`
  3. The adapter imports the upstream context's primary port and domain types, translates between the two contexts' domain languages, and satisfies the downstream context's secondary port
  4. Place integration adapters in `internal/adapters/integration/`
  5. If the upstream context has not been generated yet (status != "complete"), generate the ACL adapter as a stub with TODO markers — it will be completed when both contexts exist
- Event handlers for asynchronous integration:
  1. Read FQBC Section 8 → check for event-based upstream dependencies (pattern column mentions events or Pub/Sub)
  2. For each: generate an event handler using the Event Handler Pattern from `adapters.md`
  3. Event handlers are instantiated and subscribed in Phase 6 (main wiring), not here

**Reference**: `generators/golang/patterns/adapters.md`

#### 3e: Mock Application
- Mock application embedding real service
- Test data population methods

**Reference**: `generators/golang/patterns/mock.md`


### Phase 4: Generate Driving Adapters (`drivingAdapters`)

**Trigger**: All contexts complete, `drivingAdapters.http.status = "pending"`

Handlers are generated directly from FQBC definitions and primary port interfaces — not from TypeSpec.

**Reference**: Read `../ddd-model/api-conventions.md` for project-wide HTTP conventions (URL structure, response envelope, error codes, pagination). FQBC API Bindings already follow these conventions — handlers must match them exactly. (This file is a cross-skill dependency shared with `/ddd-model` — see its header for edit guidelines.)

**Actions**:

#### 4a: Public HTTP Handlers

For contexts with API Binding (FQBC Section 7) — skip event-driven-only contexts:

1. Read FQBC Section 7 (API Binding) for route definitions, HTTP methods, request/response schemas
2. Read FQBC Section 6 (Context Contract) for command/query details and failure scenarios
3. Read primary port interfaces for operation signatures
4. Generate HTTP handlers that:
   - Match FQBC API Binding route patterns exactly
   - Call primary port methods
   - Transform request DTOs to domain types
   - Transform domain results to response DTOs
   - Handle errors according to FQBC failure scenarios
5. Generate routes file with all endpoint registrations
6. Generate DTO types matching FQBC request/response schemas

**Generation Prompt Pattern** (for subagent delegation):
```
Generate HTTP handlers for context "{context.name}":

Primary Port Interface:
[Go interface definition]

FQBC API Binding:
[API Binding table from FQBC Section 7]

FQBC Context Contract:
[Command/Query details from FQBC Section 6]

Requirements:
1. Routes must match FQBC API Binding paths exactly
2. Request/Response types must match FQBC schemas
3. Call primary port methods for business logic
4. Handle errors according to FQBC failure scenarios
```

#### 4b: Internal HTTP Handlers

For contexts with Internal Endpoints defined in FQBC Section 7:

1. Read FQBC Section 7 (Internal Endpoints table) for route definitions
2. Read primary port interfaces for operation signatures
3. Generate internal HTTP handlers that:
   - Follow the path patterns from FQBC (e.g., `/internal/{context}/...`)
   - Call primary port methods
   - Are **not** included in TypeSpec or OpenAPI specs
4. Register internal routes alongside public routes

**Output**:
- `internal/adapters/driving/httpadapter/dto.go`
- `internal/adapters/driving/httpadapter/handlers.go`
- `internal/adapters/driving/httpadapter/internal_handlers.go` (if internal endpoints exist)
- `internal/adapters/driving/httpadapter/routes.go`

**Reference**: `generators/golang/patterns/adapters-driving.md`

**Checkpoint**: Update `drivingAdapters.http.status = "complete"` and `files` array

### Phase 5: Generate API Contracts (`apiContracts`)

**Trigger**: Driving adapters complete, `apiContracts.status = "pending"`

TypeSpec is generated as a **documentation artifact** — it produces OpenAPI specs for Swagger UI and can generate client libraries. It is not a dependency for handler generation.

**Actions**:
1. For each context **that has an API Binding section (FQBC Section 7)**, generate TypeSpec files derived from FQBC Sections 4, 6, and 7
2. **Skip contexts without API Binding** — event-driven-only contexts produce no TypeSpec output
3. **Skip internal endpoints** — TypeSpec documents the public API surface only
4. Generate shared types from context-map.md (Published Language)
5. Generate main.tsp entry point
6. Generate TypeSpec project configuration files
7. Compile TypeSpec to generate OpenAPI specs (best-effort — see reference)

**Reference**: `bcr-to-typespec.md` for mapping rules, output structure, project configuration, compilation, and Swagger UI setup.

**Checkpoint**: Update `apiContracts.status = "complete"` and `files` array

### Phase 6: Generate Main Wiring (`mainWiring`)

**Trigger**: API contracts complete (Phase 5), `infrastructure.mainWiring.status = "pending"`

**Actions**:
1. Generate `cmd/server/main.go`
2. Wire all repositories, services, handlers
3. Subscribe event handlers to event bus:
   1. Read `bcr/context-map.md` — identify all relationships with integration pattern "Pub/Sub" or "Domain Events"
   2. For each such relationship, read the publishing context's FQBC Section 6 (Context Contract → Outbound Events) for the event name and payload
   3. In the subscribing context, create an integration event handler per `adapters.md` Event Handler Pattern
   4. Wire the subscription: `eventBus.Subscribe("{EventName}", handler)`
4. Support APP_MODE env var (default: live, set to "mock" for test data). In mock mode, create the mock application (which embeds the real service), populate test data through it, and wire handlers to it. Only one service instance should exist per context in either mode. See `generators/golang/patterns/mock.md` for the wiring pattern.
5. **Generate `README.md`** with usage instructions (see README template below)

**Checkpoint**: Update `infrastructure.mainWiring`

#### README Generation

Generate a `README.md` file with the following sections:

```markdown
# {Project Name}

{Brief description from BCR context-map}

## Quick Start

### Prerequisites
- Go 1.21+

### Running the Server

\`\`\`bash
# Run in live mode (default)
go run ./cmd/server

# Run in mock mode (uses in-memory repositories with test data)
APP_MODE=mock go run ./cmd/server
\`\`\`

The server starts on `http://localhost:8080` by default.

### API Endpoints

{For each context with an API binding, list key endpoints from FQBC Section 7, e.g.:}
{**Context Name**}
{- `POST /api/{context-slug}/v1/{resource}` — Create resource}
{- `GET /api/{context-slug}/v1/{resource}/{id}` — Get resource by ID}

## Project Structure

\`\`\`
cmd/server/       - Application entry point
internal/
  {context}/      - Bounded context implementation
    domain/       - Domain entities, value objects, events
    application/  - Use case orchestration
    ports/        - Primary (inbound) and secondary (outbound) interfaces
    mock/         - Mock implementation with test data
  adapters/       - Infrastructure adapters
  support/        - Shared infrastructure (auth, logging, etc.)
api/              - TypeSpec API contracts
\`\`\`

## Development

### Adding Business Logic

Look for `// TODO:` markers in application services to implement actual business logic.

### Running Tests

\`\`\`bash
go test ./...
\`\`\`

### Building

\`\`\`bash
go build ./cmd/server
\`\`\`
```

### Phase 7: Validation (`validation`)

> **Note**: This phase validates that generated code compiles and tests pass. For DDD pattern conformance auditing, use `/ddd-eval` (which consults `validate.md` rubrics) as a separate post-generation step.

**Trigger**: Main wiring complete

**Actions**:
1. Run `go build ./...`
2. Run `go test ./...`
3. **Token round-trip validation**: Verify that `gentoken` produces tokens the running server accepts and that roles are interpreted correctly:
   1. Start the server in mock mode: `APP_MODE=mock go run ./cmd/server &`
   2. **Authentication check** — admin token is accepted:
      - Generate a token: `TOKEN=$(go run cmd/gentoken/main.go -roles "admin")`
      - Hit a protected endpoint (use an actual endpoint from the FQBC, e.g., a GET list): `curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/{context-slug}/v1/{resource}`
      - Verify the HTTP status is `200`. A `401` means the token was rejected (secret mismatch or timestamp loss). A `403` means Claims were parsed but roles were not mapped correctly.
   3. **Role enforcement check** — restricted role is denied operations it lacks:
      - Generate a non-admin token with a role that should lack write access (e.g., `readonly`): `TOKEN=$(go run cmd/gentoken/main.go -roles "readonly")`
      - Hit a write endpoint (e.g., POST create): `curl -s -w "\n%{http_code}" -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}' http://localhost:8080/api/{context-slug}/v1/{resource}`
      - Verify the HTTP status is `403` (forbidden), confirming the permission check distinguished this role from admin.
      - If the response is `200`, the role-to-permission mapping in `Require{Context}Permission` is too permissive or is not being called.
   4. Stop the server
   5. If any check fails, verify: (a) `gentoken` and `config.Load()` use the same default JWT secret, (b) `ParseToken` preserves the JWT's timestamps and `Roles` slice in the returned `Claims`, (c) `Require{Context}Permission` is called in the application service before executing business logic.
4. Record results in `validation`

**Checkpoint**: Update `validation.build` and `validation.tests`

---

## Error Recovery

**Reference**: See `session-management.md` § Error Recovery for manifest error format and recovery procedures.

**Quick summary**: Read error from manifest → fix the specific file → re-run build → if successful, clear error and continue. For interrupted sessions, the manifest tracks `currentContext`, phase statuses, and `generatedFiles` for precise resumption.

---

## Output Structure

**Reference**: See `generators/golang/generator.md` for the complete directory layout and naming conventions.

**Top-level structure**:
- `cmd/server/` — Application entry point (`main.go`)
- `internal/{context}/` — Per-context domain, application, ports, and mock layers
- `internal/adapters/` — Driving (HTTP), driven (in-memory, event bus), and integration adapters
- `internal/support/` — Shared infrastructure (auth, logging, validation, etc.)
- `api/` — TypeSpec API contracts and generated OpenAPI specs
- `ddd-workspace/` — BCR and implementation manifests

---

## Code Generation Guidelines

1. **Use patterns as reference, not templates**: Adapt patterns to specific context
2. **Maintain consistency**: Follow naming conventions strictly
3. **Add TODO markers**: Mark where business logic should be added
4. **Include validation**: All entities/VOs validate in constructors
5. **Document interfaces**: Add doc comments to all exported types
6. **Thread safety**: Use mutex in in-memory implementations
7. **Valid test data**: Use valid UUID formats (hex only: 0-9, a-f)
8. **FQBC compliance**: HTTP handlers and TypeSpec contracts must both derive from the same FQBC definitions

---

## Usage

### Generate Mode

1. Check for existing `ddd-workspace/ddd-implement.manifest.json`
2. If exists: validate against `manifest.schema.json`, analyze state, report progress, identify next action
3. If not exists: look for BCR workspace, create initial manifest
4. Execute ONE bounded context at a time using subagents
5. After all contexts: generate HTTP adapters, TypeSpec docs, main wiring
6. Verify build after each major phase
7. Report progress clearly for session handoff

**Key principle**: Always leave the manifest in a state where the next session can pick up cleanly.

### Validate Mode

1. Run Phase 0 (discovery) to identify contexts and project structure
2. Execute validation phases 1–8 as defined in `validate.md`
3. Write findings to `ddd-validation-report.md` in the project root
4. Present a summary with finding counts and critical issues

Supports partial validation — the user can request validation of a specific context or layer only. See `validate.md` for details.

---

## Future Patterns (Not Yet Implemented)

The following patterns are recognized as important for production systems but are outside the scope of the walking skeleton:

- **Outbox Pattern**: Ensures atomicity between data persistence and event publishing. Currently, events are published synchronously after persistence — if the process crashes after saving but before publishing, events are lost. The outbox pattern writes events to a persistent outbox table within the same transaction, with a separate process reading and publishing them.

- **Unit of Work**: Manages transaction boundaries across multiple aggregate updates within a single use case. Currently, each repository operation is independent. A Unit of Work would batch changes and commit them atomically.

These patterns should be added as developers move from walking skeleton to production readiness.

---

## Generator Selection

The skill uses the generator specified in `project.generator`:

- Read generator specification from `generators/{generator}/generator.md`
- Use patterns from `generators/{generator}/patterns/`
- Apply naming conventions and directory structure from generator

Currently supported: `go-hex`
