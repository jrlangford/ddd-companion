---
name: ddd-implement
description: Transform BCR bounded context definitions into a walking skeleton - a runnable Go hexagonal architecture application with validated DDD boundaries. Use after completing BCR workflow to generate implementation code. Also validates existing projects against DDD standards.
disable-model-invocation: true
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
7. **Driving adapters** (HTTP handlers generated from FQBC (Fully Qualified Bounded Context) definitions)
8. **TypeSpec API documentation** (OpenAPI specs and client generation)
9. Main wiring and validated boundaries

## Goals

1. **Walking skeleton for iterative development**: Generate a runnable application with all layers connected (domain → ports → application → adapters → main) but minimal business logic. Developers add flesh to the bones without structural refactoring.
2. **Mock server for frontend teams**: The skeleton can run in mock mode (`APP_MODE=mock`), providing realistic API responses for parallel frontend development.
3. **Spec-first API design**: API contracts (TypeSpec) are the source of truth for the HTTP layer.

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

HTTP handlers are generated directly from FQBC definitions and primary port interfaces. TypeSpec is generated separately as a documentation artifact — it produces OpenAPI specs (for Swagger UI) and can generate client libraries for service consumers.

### Generation Pipeline

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

### Why FQBC drives handlers directly

1. **No intermediary dependency**: Handlers don't wait for TypeSpec compilation — the skeleton is runnable sooner
2. **Single source of truth**: Both handlers and TypeSpec derive from the same FQBC, preventing drift
3. **TypeSpec is optional**: The skeleton compiles and runs without TypeSpec; OpenAPI/clients are additive
4. **Simpler pipeline**: No need to ensure TypeSpec output matches handler expectations

### TypeSpec role

TypeSpec is a **documentation and client generation tool**, not a handler generation dependency:
- Generates OpenAPI specs for Swagger UI visualization
- Can generate typed client libraries for other services to import
- Validates that the public API surface is well-documented

---

## Multi-Session Design

This workflow is designed to span multiple sessions. Context window limits will be reached during generation of complex systems.

### Core Principles

1. **Manifest is the source of truth** - All progress is tracked in `ddd-workspace/ddd-implement.manifest.json`
2. **One context at a time** - Process each bounded context completely before moving to the next
3. **Subagents for isolation** - Use Task tool subagents for each context to manage memory
4. **Checkpoint after each operation** - Update manifest immediately after completing any unit of work
5. **File-level tracking** - Track individual files created, not just phases

### Context Window Management Strategies

**Strategy 1: Subagent per Context (Recommended)**
```
Main Agent:
  1. Read manifest, identify next context to process
  2. Spawn subagent for that context with focused prompt
  3. Subagent generates all layers for ONE context
  4. Subagent updates manifest with files created
  5. Main agent verifies, moves to next context
```

**Strategy 2: Subagent per Phase**
```
Main Agent:
  1. For each phase (domain, ports, application, adapters):
     - Spawn subagent with phase-specific prompt
     - Subagent processes ALL contexts for that phase
     - Subagent updates manifest
```

**Strategy 3: Checkpoint and Clear**
```
After completing each context:
  1. Update manifest with all file paths created
  2. Run `go build ./...` to verify
  3. Summarize progress to user
  4. User can continue in new session if needed
```

### Subagent Prompts

When spawning a subagent for a context, provide:
```
Generate [PHASE] for context [CONTEXT_NAME]:

Manifest location: ./ddd-workspace/ddd-implement.manifest.json
Context definition: [paste relevant context object from manifest]
Generator patterns: [reference pattern files]

Requirements:
1. Generate files for this context only
2. Update manifest.contexts[N].phases.[phase] = "complete"
3. Update manifest.contexts[N].generatedFiles.[phase] = [list of files]
4. Run `go build ./...` after generation
5. Report any errors encountered

Do NOT read other context directories.
Do NOT modify files outside this context.
```

---

## Manifest Structure

The manifest tracks granular progress for reliable session resumption.

### Full Manifest Schema

```json
{
  "version": "1.0",
  "project": {
    "name": "my-service",
    "module": "github.com/org/my-service",
    "language": "go",
    "generator": "go-hex",
    "outputDir": "."
  },
  "source": {
    "bcrWorkspace": "./ddd-workspace"
  },
  "currentPhase": "contexts",
  "currentContext": null,
  "infrastructure": {
    "support": {
      "status": "pending",
      "files": []
    },
    "eventBus": {
      "status": "pending",
      "files": []
    },
    "mainWiring": {
      "status": "pending",
      "files": []
    }
  },
  "apiContracts": {
    "status": "pending",
    "files": [],
    "format": "typespec",
    "outputDir": "./api"
  },
  "drivingAdapters": {
    "http": {
      "status": "pending",
      "files": []
    }
  },
  "contexts": [
    {
      "name": "role-management",
      "contextId": "CTX-001",
      "fqbcFile": "fqbc/role-management.md",
      "status": "pending",
      "phases": {
        "domain": "pending",
        "ports": "pending",
        "application": "pending",
        "drivenAdapters": "pending",
        "mock": "pending"
      },
      "generatedFiles": {
        "domain": [],
        "ports": [],
        "application": [],
        "drivenAdapters": [],
        "mock": []
      },
      "entities": ["RoleAssignment", "SurveillanceRole"],
      "valueObjects": ["PersonId", "RoleName", "Scope"],
      "domainEvents": ["RoleAssigned", "RoleRevoked"],
      "integrations": [],
      "errors": []
    }
  ],
  "validation": {
    "build": "pending",
    "tests": "pending",
    "lastBuildOutput": null
  },
  "history": [
    {
      "timestamp": "2024-01-20T10:00:00Z",
      "action": "context_complete",
      "context": "role-management",
      "filesCreated": 12
    }
  ]
}
```

### Key Manifest Fields

| Field | Purpose |
|-------|---------|
| `currentPhase` | Where in the overall workflow: `init`, `support`, `contexts`, `apiContracts`, `drivingAdapters`, `mainWiring`, `validation`, `complete` |
| `currentContext` | Which context is being processed (null if between contexts) |
| `contexts[].status` | `pending`, `in_progress`, `complete`, `error` |
| `contexts[].generatedFiles` | Array of file paths created for each phase |
| `contexts[].errors` | Any errors encountered during generation |
| `apiContracts.status` | Status of TypeSpec contract generation |
| `drivingAdapters.http.status` | Status of HTTP adapter generation |
| `history` | Audit log of completed operations |

### Status Transitions

**Context status** (`contexts[].status`):

```
pending → in_progress → complete
              │
              ▼
            error → in_progress → complete
```

- A context in `error` can be retried by fixing the issue and setting status back to `in_progress`
- Once `complete`, a context is not regenerated unless the user explicitly requests it

**Phase status** (`contexts[].phases.*`):

```
pending → in_progress → complete
```

Phases within a context progress strictly forward. If a phase fails, the context status is set to `error` with details in `contexts[].errors`.

**Overall workflow** (`currentPhase`):

```
init → support → contexts → drivingAdapters → apiContracts → mainWiring → validation → complete
```

---

## Session Resumption Protocol

When starting or resuming work:

### Step 1: Read and Analyze Manifest
```
1. Read ddd-workspace/ddd-implement.manifest.json
2. Check currentPhase and currentContext
3. For each context, check status and phases
4. Identify the FIRST incomplete item
```

### Step 2: Determine Next Action

| State | Action |
|-------|--------|
| No manifest | Create manifest, parse BCR workspace |
| `infrastructure.support.status = pending` | Generate support packages |
| Context with `status = in_progress` | Resume that context from incomplete phase |
| Context with `status = pending` | Start that context |
| All contexts complete, `apiContracts.status = pending` | Generate TypeSpec contracts |
| API contracts complete, `drivingAdapters.http.status = pending` | Generate HTTP adapters |
| Driving adapters complete, `mainWiring.status = pending` | Generate main wiring |
| Main wiring complete, validation pending | Run validation |

### Step 3: Execute with Checkpointing

After EACH file or small group of files:
1. Update `generatedFiles` array in manifest
2. If completing a phase, update phase status
3. If completing a context, update context status and `history`

### Step 4: Verify Before Proceeding
```bash
go build ./...
```
If build fails, record error in manifest and stop.

---

## Session Stop Protocol

When context window is approaching capacity or you need to end a session, follow this protocol for a clean handoff.

### When to Stop

Stop at the nearest natural boundary:

| Current Work | Natural Stopping Point |
|-------------|----------------------|
| Phase 3 (Contexts) | After completing any full context (all layers: domain → ports → application → adapters → mock) |
| Phase 4 (HTTP Handlers) | After completing all handlers for one context |
| Phase 5 (TypeSpec) | After completing TypeSpec for one context |
| Phase 6 (Main Wiring) | After `main.go` is written and builds |
| Phase 7 (Validation) | After build/test results are recorded |

**Do not stop mid-layer** (e.g., domain generated but ports not started). Complete the current context's layer set or roll back to the last checkpoint.

### Before Stopping

1. **Update the manifest** — ensure all completed work is reflected in `generatedFiles`, phase statuses, and context statuses
2. **Run `go build ./...`** — verify the codebase compiles; record result in manifest
3. **Set `currentContext` to null** if the current context is fully complete; leave it set if mid-context (the resumption protocol will pick it up)

### What to Report

Provide the user with a handoff summary:

```markdown
**Session Complete**

**Progress**: [N]/[Total] contexts generated | Phase [current] | [files created] files
**Build status**: [pass/fail]
**Next step**: [what the next session should do first]

To resume: re-invoke `/ddd-implement` — the manifest tracks all progress.
```

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

### Phase 2: Generate Support Infrastructure

**Trigger**: `infrastructure.support.status = "pending"`

**Actions**:
1. Generate `internal/support/basedomain/`
2. Generate `internal/support/validation/`
3. Generate `internal/support/auth/`
4. Generate `internal/support/config/`
5. Generate `internal/support/errors/`
6. Generate `internal/support/logging/`
7. Generate `internal/support/eventbus/`
8. Generate `internal/support/middleware/`
9. Generate `internal/support/server/`

**Checkpoint**: Update `infrastructure.support.status = "complete"` and `files` array

**Reference**: `generators/golang/generator.md`

### Phase 3: Generate Contexts (One at a Time)

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

Use a **subagent** to process the entire context:

```
Task: Generate all layers for context "{context.name}"

The subagent should:
1. Set context.status = "in_progress"
2. Generate domain layer → update phases.domain, generatedFiles.domain
3. Generate ports → update phases.ports, generatedFiles.ports
4. Generate application → update phases.application, generatedFiles.application
5. Generate driven adapters (repositories) → update phases.drivenAdapters, generatedFiles.drivenAdapters
6. Generate mock → update phases.mock, generatedFiles.mock
7. Run `go build ./...` to verify
8. Set context.status = "complete"
9. Add entry to history
```

**IMPORTANT**: Complete ONE context fully before starting the next.

**NOTE**: Driving adapters (HTTP handlers) are NOT generated in this phase. They are generated in Phase 4 after all contexts are complete.

#### 3a: Domain Layer
- Entity ID types (scalars wrapping UUID)
- Entities with BaseEntity embedding
- Value objects with validation
- Domain events
- Domain errors

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
- ACL adapters for cross-context integration

**Reference**: `generators/golang/patterns/adapters.md`

#### 3e: Mock Application
- Mock application embedding real service
- Test data population methods

**Reference**: `generators/golang/patterns/mock.md`


### Phase 4: Generate Driving Adapters (HTTP)

**Trigger**: All contexts complete, `drivingAdapters.http.status = "pending"`

Handlers are generated directly from FQBC definitions and primary port interfaces — not from TypeSpec.

**Reference**: `api-conventions.md` in the `ddd-model` skill defines project-wide HTTP conventions (URL structure, response envelope, error codes, pagination). FQBC API Bindings already follow these conventions — handlers must match them exactly.

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

**Generation Prompt Pattern**:
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

**Checkpoint**: Update `drivingAdapters.http.status = "complete"` and `files` array

### Phase 5: Generate API Documentation (TypeSpec)

**Trigger**: Driving adapters complete, `apiContracts.status = "pending"`

TypeSpec is generated as a **documentation artifact** — it produces OpenAPI specs for Swagger UI and can generate client libraries for service consumers. It is not a dependency for handler generation.

**Actions**:
1. For each context **that has an API Binding section (FQBC Section 7)**, generate TypeSpec files derived from:
   - FQBC Section 4 (Domain Model) for model/enum/scalar definitions
   - FQBC Section 6 (Context Contract) for endpoint definitions
   - FQBC Section 7 (API Binding) for route patterns (public endpoints only)
2. **Skip contexts without API Binding** — event-driven-only contexts produce no TypeSpec output
3. **Skip internal endpoints** — TypeSpec documents the public API surface only
4. Generate shared types from context-map.md (Published Language)
5. Generate main.tsp entry point
6. Generate TypeSpec project configuration files
7. Compile TypeSpec to generate OpenAPI specs

**Reference**: `bcr-to-typespec.md`

**Output Structure**:
```
api/
├── main.tsp                    # Main entry point
├── package.json                # TypeSpec dependencies
├── tspconfig.yaml              # TypeSpec compiler configuration
├── common/
│   └── types.tsp               # Shared types (PersonId, Permissions)
├── {context-name}/
│   ├── models.tsp              # Domain models for this context
│   └── endpoints.tsp           # Public API endpoints
└── tsp-output/
    └── openapi/
        └── openapi.yaml        # Generated OpenAPI spec
```

#### TypeSpec Project Configuration

**package.json**:
```json
{
  "name": "{project}-api",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "build": "tsp compile .",
    "watch": "tsp compile . --watch",
    "format": "tsp format **/*.tsp"
  },
  "devDependencies": {
    "@typespec/compiler": "latest",
    "@typespec/http": "latest",
    "@typespec/rest": "latest",
    "@typespec/openapi": "latest",
    "@typespec/openapi3": "latest"
  }
}
```

**tspconfig.yaml**:
```yaml
emit:
  - "@typespec/openapi3"

options:
  "@typespec/openapi3":
    output-file: openapi.yaml
    emitter-output-dir: "{output-dir}/openapi"
```

#### Compiling TypeSpec

After generating TypeSpec files, attempt to compile to OpenAPI. This step is **best-effort** — if Node.js/npm is not available, skip compilation and note it in the manifest. The walking skeleton is fully functional without it.

```bash
cd api
npm install        # Install TypeSpec compiler and dependencies
npm run build      # Compile TypeSpec to OpenAPI
```

If `npm` is not found or compilation fails, log a warning and continue to Phase 6. Set `apiContracts.status = "complete"` regardless — the TypeSpec source files are the primary artifact, not the compiled output.

The generated OpenAPI spec (when compiled) will be at `api/tsp-output/openapi/openapi.yaml`.

#### Visualizing the API with Swagger UI

To launch an interactive API viewer for development and testing:

```bash
# Start Swagger UI with Docker (pointing to your OpenAPI spec)
docker run -d \
  --name swagger-ui \
  -p 8081:8080 \
  -e SWAGGER_JSON=/openapi/openapi.yaml \
  -v "$(pwd)/api/tsp-output/openapi:/openapi" \
  swaggerapi/swagger-ui

# Access at http://localhost:8081
```

**Prerequisites**:
- Docker installed and running
- Go server running on port 8080 (for actual API interaction)

**Useful commands**:
```bash
# Stop Swagger UI
docker stop swagger-ui && docker rm swagger-ui

# Restart after updating OpenAPI spec
docker restart swagger-ui

# View logs
docker logs swagger-ui
```

**Checkpoint**: Update `apiContracts.status = "complete"` and `files` array

### Phase 6: Generate Main Wiring

**Trigger**: Driving adapters complete (Phase 4), `infrastructure.mainWiring.status = "pending"`

**Note**: Phase 5 (TypeSpec/OpenAPI) is independent — main wiring depends only on handlers being generated.

**Actions**:
1. Generate `cmd/server/main.go`
2. Wire all repositories, services, handlers
3. Subscribe event handlers to event bus
4. Support APP_MODE env var (default: live, set to "mock" for test data). In mock mode, create the mock application (which embeds the real service), populate test data through it, and wire handlers to it. Only one service instance should exist per context in either mode. See `generators/golang/patterns/mock.md` for the wiring pattern.
5. **Generate `README.md`** with usage instructions (see below)

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

```bash
# Run in live mode (default)
go run ./cmd/server

# Run in mock mode (uses in-memory repositories with test data)
APP_MODE=mock go run ./cmd/server
```

The server starts on `http://localhost:8080` by default.

### API Endpoints

{List key endpoints per context}

## Project Structure

```
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
```

## Development

### Adding Business Logic

Look for `// TODO:` markers in application services to implement actual business logic.

### Running Tests

```bash
go test ./...
```

### Building

```bash
go build ./cmd/server
```
```

### Phase 7: Validation

**Trigger**: Main wiring complete

**Actions**:
1. Run `go build ./...`
2. Run `go test ./...`
3. Record results in `validation`

**Checkpoint**: Update `validation.build` and `validation.tests`

---

## Error Recovery

### Build Failure During Context Generation

```json
{
  "contexts": [{
    "name": "role-management",
    "status": "error",
    "errors": [
      {
        "phase": "application",
        "file": "internal/rolemanagement/rolemanagementapplication/service.go",
        "error": "undefined: PersonId",
        "timestamp": "2024-01-20T10:30:00Z"
      }
    ]
  }]
}
```

**Recovery**:
1. Read the error from manifest
2. Fix the specific file
3. Re-run build
4. If successful, clear error and continue

### Session Interrupted Mid-Context

The manifest shows exactly where we stopped:
- `currentContext` indicates which context
- `phases` shows which phases are complete
- `generatedFiles` shows exactly what files exist

Resume by checking which phase is incomplete and continuing from there.

---

## Output Structure

Generated files are placed in the project root directory.

```
./
├── api/                                # TypeSpec API contracts
│   ├── main.tsp
│   ├── common/
│   │   └── types.tsp
│   ├── {context}/
│   │   ├── models.tsp
│   │   ├── endpoints.tsp
│   │   └── events.tsp
│   └── openapi/
│       └── {context}.yaml
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── {context}/
│   │   ├── {context}domain/
│   │   ├── {context}application/
│   │   ├── {context}mock/
│   │   └── ports/
│   │       ├── {context}primary/
│   │       └── {context}secondary/
│   ├── adapters/
│   │   ├── driving/
│   │   │   └── httpadapter/
│   │   │       ├── dto.go
│   │   │       ├── handlers.go
│   │   │       ├── routes.go
│   │   │       └── middleware/
│   │   ├── driven/
│   │   │   ├── inmemory/
│   │   │   └── eventbus/
│   │   └── integration/
│   └── support/
│       ├── auth/
│       ├── basedomain/
│       ├── config/
│       ├── errors/
│       ├── eventbus/
│       ├── logging/
│       ├── middleware/
│       ├── server/
│       └── validation/
├── test/
│   ├── integration/
│   └── testdata/
├── go.mod
├── go.sum
├── README.md                           # Usage instructions
└── ddd-workspace/
    ├── ddd-model.manifest.json         # BCR workflow state (from /ddd-model)
    └── ddd-implement.manifest.json     # Implementation workflow state
```

---

## Code Generation Guidelines

1. **Use patterns as reference, not templates**: Adapt patterns to specific context
2. **Maintain consistency**: Follow naming conventions strictly
3. **Add TODO markers**: Mark where business logic should be added
4. **Include validation**: All entities/VOs validate in constructors
5. **Document interfaces**: Add doc comments to all exported types
6. **Thread safety**: Use mutex in in-memory implementations
7. **Valid test data**: Use valid UUID formats (hex only: 0-9, a-f)
8. **Spec compliance**: HTTP handlers must match TypeSpec contracts exactly

---

## Usage

### Generate Mode

When invoked for generation:

1. Check for existing `ddd-workspace/ddd-implement.manifest.json`
2. If exists: analyze state, report current progress, identify next action
3. If not exists: look for BCR workspace, create initial manifest
4. Execute ONE bounded context at a time using subagents
5. After all contexts: generate TypeSpec contracts
6. After contracts: generate HTTP adapters from contracts
7. Generate main wiring
8. Verify build after each major phase
9. Report progress clearly for session handoff

**Key principle**: Always leave the manifest in a state where the next session can pick up cleanly.

### Validate Mode

When invoked for validation:

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
