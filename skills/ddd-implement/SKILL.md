---
name: ddd-implement
description: Transform BCR bounded context definitions into a walking skeleton - a runnable Go hexagonal architecture application with validated DDD boundaries. Use after completing BCR workflow to generate implementation code.
disable-model-invocation: true
---

# ddd-implement Skill

Transform bounded context definitions into a **walking skeleton**: a minimal, runnable application that connects all architectural layers end-to-end with validated boundaries.

## Overview

This skill takes BCR (Bounded Context Registry) workspace definitions and generates:
1. Support infrastructure (base types, auth, validation)
2. Domain layer with entities, value objects, and events
3. Port interfaces (primary and secondary)
4. Application layer with use case orchestration
5. Driven adapters (repositories, event bus)
6. Mock implementations with test data factories
7. **TypeSpec API contracts** (derived from primary ports)
8. **Driving adapters** (HTTP handlers generated from TypeSpec)
9. Main wiring and validated boundaries

## Goals

1. **Walking skeleton for iterative development**: Generate a runnable application with all layers connected (domain → ports → application → adapters → main) but minimal business logic. Developers add flesh to the bones without structural refactoring.
2. **Mock server for frontend teams**: The skeleton runs immediately in mock mode, providing realistic API responses for parallel frontend development.
3. **Spec-first API design**: API contracts (TypeSpec) are the source of truth for the HTTP layer.

## Prerequisites

Before running this skill, you must have:
- A completed BCR workspace (from `/ddd-model` skill) with:
  - `ddd-model.manifest.json` showing `current_phase: "complete"`
  - FQBC documents for all contexts in `fqbc/` directory
  - Context map in `bcr/context-map.md`

---

## Spec-First API Design

This skill follows a **spec-first** approach where API contracts drive HTTP adapter generation.

### Transformation Pipeline

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Primary Ports  │ ──► │  TypeSpec Spec  │ ──► │  HTTP Adapters  │
│  (Go interfaces)│     │  (API contract) │     │  (Go handlers)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
     WHAT the              HOW the API           HOW the code
   system can do          exposes it            implements it
```

### Layer Responsibilities

| Layer | Artifact | Language | Purpose |
|-------|----------|----------|---------|
| **Domain** | Primary Ports | Go interfaces | What the system CAN do (use cases) |
| **Contract** | TypeSpec | TypeSpec/OpenAPI | How the API EXPOSES it (HTTP contract) |
| **Implementation** | HTTP Adapters | Go code | How the code IMPLEMENTS the contract |

### Benefits

1. **Single Source of Truth**: TypeSpec is authoritative for all API-related artifacts
2. **Consistency Guarantee**: Handlers, clients, OpenAPI all derived from same spec
3. **Decoupled Evolution**: Domain can evolve independently of API surface
4. **Generator-Ready**: When TypeSpec-to-Go generators mature, drop-in replacement
5. **LLM Guidance**: Spec constrains LLM generation, reducing drift and hallucination

### Generation Flow

When generating HTTP adapters, the LLM receives:
1. The primary port interface (what operations exist)
2. The TypeSpec API contract (how they're exposed via HTTP)
3. Instructions to generate handlers that match the contract exactly

This ensures generated code matches the spec, even without formal code generators.

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
      "fqbcFile": "fqbc/fqbc-role-management.md",
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

## Execution Phases

### Phase 1: Initialize Manifest

**Trigger**: No `ddd-workspace/ddd-implement.manifest.json` exists

**Actions**:
1. Read BCR workspace manifest (`ddd-workspace/ddd-model.manifest.json`)
2. Parse each FQBC document
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

**For each context where `status != "complete"`:**

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

**NOTE**: Driving adapters (HTTP handlers) are NOT generated in this phase. They come after TypeSpec contracts.

#### 3a: Domain Layer
- Entity ID types (scalars wrapping UUID)
- Entities with BaseEntity embedding
- Value objects with validation
- Domain events
- Domain errors

**Reference**: `generators/golang/patterns/domain.md`

#### 3b: Ports
- Primary port interfaces (from Commands/Queries)
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

### Phase 4: Generate API Contracts (TypeSpec)

**Trigger**: All contexts complete, `apiContracts.status = "pending"`

**Actions**:
1. For each context, generate TypeSpec files derived from:
   - Primary port interfaces (operations)
   - FQBC Section 5 (Published Interface - commands, queries, events)
   - FQBC Section 6 (Context Relationships - internal APIs)
2. Generate shared types from context-map.md (Published Language)
3. Generate main.tsp entry point
4. Generate TypeSpec project configuration files
5. Compile TypeSpec to generate OpenAPI specs

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

After generating TypeSpec files, compile to OpenAPI:

```bash
cd api
npm install        # Install TypeSpec compiler and dependencies
npm run build      # Compile TypeSpec to OpenAPI
```

The generated OpenAPI spec will be at `api/tsp-output/openapi/openapi.yaml`.

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

**Reference**: `bcr-to-typespec.md`

**Checkpoint**: Update `apiContracts.status = "complete"` and `files` array

### Phase 5: Generate Driving Adapters (HTTP)

**Trigger**: API contracts complete, `drivingAdapters.http.status = "pending"`

**Actions**:
1. Read TypeSpec contracts for route definitions
2. Read primary port interfaces for operation signatures
3. Generate HTTP handlers that:
   - Match TypeSpec route patterns exactly
   - Call primary port methods
   - Transform request DTOs to domain types
   - Transform domain results to response DTOs
4. Generate routes file with all endpoint registrations
5. Generate DTO types matching TypeSpec models

**Generation Prompt Pattern**:
```
Generate HTTP handlers for context "{context.name}":

Primary Port Interface:
[Go interface definition]

TypeSpec API Contract:
[TypeSpec endpoint definitions]

Requirements:
1. Routes must match TypeSpec @route decorators exactly
2. Request/Response types must match TypeSpec models
3. Call primary port methods for business logic
4. Handle errors according to TypeSpec error responses
```

**Output**:
- `internal/adapters/driving/httpadapter/dto.go`
- `internal/adapters/driving/httpadapter/handlers.go`
- `internal/adapters/driving/httpadapter/routes.go`

**Checkpoint**: Update `drivingAdapters.http.status = "complete"` and `files` array

### Phase 6: Generate Main Wiring

**Trigger**: Driving adapters complete, `infrastructure.mainWiring.status = "pending"`

**Actions**:
1. Generate `cmd/server/main.go`
2. Wire all repositories, services, handlers
3. Subscribe event handlers to event bus
4. Support APP_MODE env var for mock/live switching
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
# Run in mock mode (default, uses in-memory repositories with test data)
go run ./cmd/server

# Run in live mode (requires actual repository implementations)
APP_MODE=live go run ./cmd/server
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

When invoked:

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

---

## Generator Selection

The skill uses the generator specified in `project.generator`:

- Read generator specification from `generators/{generator}/generator.md`
- Use patterns from `generators/{generator}/patterns/`
- Apply naming conventions and directory structure from generator

Currently supported: `go-hex`
