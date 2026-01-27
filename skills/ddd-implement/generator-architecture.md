# Generator Architecture

This document defines the pluggable generator architecture for ddd-implement, enabling support for multiple languages and frameworks while maintaining consistent DDD patterns.

## Overview

Generators are responsible for transforming BCR workspace definitions into implementation code. The architecture separates:

1. **Core logic** - Language-agnostic manifest management, BCR parsing, contract generation
2. **Generators** - Language/framework-specific code generation patterns

## Generator Interface

Each generator must implement the following phases:

```
Generator
├── init()           → Initialize project structure
├── domain()         → Generate domain layer
├── ports()          → Generate port interfaces
├── application()    → Generate application services
├── adapters()       → Generate infrastructure adapters
├── mock()           → Generate mock implementations
├── fixtures()       → Generate test data factories
├── integration()    → Generate cross-context adapters
└── validate()       → Validate generated code
```

## Generator Selection

Generators are selected via the `project.generator` field in the manifest:

```json
{
  "project": {
    "language": "go",
    "generator": "go-hex"
  }
}
```

### Available Generators

| Generator | Language | Architecture | Status |
|-----------|----------|--------------|--------|
| `go-hex` | Go | Hexagonal (Ports & Adapters) | Active |
| `go-clean` | Go | Clean Architecture | Planned |
| `ts-hex` | TypeScript | Hexagonal | Planned |

## Generator Registration

To add a new generator, create a directory under `generators/` with:

```
generators/
└── {generator-name}/
    ├── generator.md      # Generator specification
    ├── patterns/         # Code patterns for each phase
    │   ├── domain.md
    │   ├── ports.md
    │   ├── application.md
    │   ├── adapters.md
    │   ├── mock.md
    │   └── fixtures.md
    └── templates/        # Optional: reusable code snippets
```

## Generator Specification Format

Each `generator.md` must define:

### 1. Metadata

```markdown
# Generator: go-hex

## Metadata
- Language: Go
- Architecture: Hexagonal (Ports & Adapters)
- Version: 1.0
- Maintainer: team@example.com
```

### 2. Directory Structure

Define the output directory structure:

```markdown
## Directory Structure

\`\`\`
{project}/
├── cmd/
│   └── main.go
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
│   │   ├── driven/
│   │   └── integration/
│   └── support/
├── test/
└── go.mod
\`\`\`
```

### 3. Naming Conventions

```markdown
## Naming Conventions

| Concept | Convention | Example |
|---------|------------|---------|
| Context package | lowercase | `booking` |
| Domain package | {context}domain | `bookingdomain` |
| Entity | PascalCase | `Cargo` |
| Entity ID | {Entity}Id | `TrackingId` |
| Value Object | PascalCase | `RouteSpecification` |
| Domain Event | PascalCase, past tense | `CargoBooked` |
| Repository | {Entity}Repository | `CargoRepository` |
| Service Interface | {Context}Service | `BookingService` |
| Application Service | {Context}ApplicationService | `BookingApplicationService` |
```

### 4. Dependencies

```markdown
## Dependencies

### Required
- github.com/google/uuid
- github.com/go-playground/validator/v10

### Optional
- github.com/golang-jwt/jwt/v5 (if auth enabled)
```

## Phase Specifications

Each phase pattern file (`patterns/*.md`) defines:

### Input

What information from the manifest/BCR the phase needs:

```markdown
## Input

- Context name
- Entities (name, properties, isAggregateRoot)
- Value objects (name, properties)
- Domain events (name, payload)
```

### Output

What files/code the phase produces:

```markdown
## Output

For each entity:
- `internal/{context}/{context}domain/{entity_snake}.go`

For each value object:
- `internal/{context}/{context}domain/{vo_snake}.go`
```

### Patterns

Code patterns with placeholders:

```markdown
## Patterns

### Entity Pattern

\`\`\`go
package {context}domain

import (
    "{{module}}/internal/support/basedomain"
    "{{module}}/internal/support/validation"
)

// {EntityId} is the unique identifier for {Entity}
type {EntityId} struct {
    uuid.UUID
}

func New{EntityId}() {EntityId} {
    return {EntityId}{UUID: uuid.New()}
}

// {Entity} represents {entity_description}
// This is {{#if isAggregateRoot}}an aggregate root{{else}}an entity{{/if}}
type {Entity} struct {
    basedomain.BaseEntity[{EntityId}] `json:",inline"`
    Data {Entity}Data `json:"data"`
}

// {Entity}Data contains the business data for {Entity}
type {Entity}Data struct {
    {{#each properties}}
    {PropertyName} {PropertyType} `json:"{property_json}" validate:"{validation_tags}"`
    {{/each}}
}

// New{Entity} creates a new {Entity} with validation
func New{Entity}({{constructor_params}}) ({Entity}, error) {
    id := New{EntityId}()

    data := {Entity}Data{
        {{#each properties}}
        {PropertyName}: {paramName},
        {{/each}}
    }

    if err := validation.Validate(data); err != nil {
        return {Entity}{}, NewDomainValidationError("{entity} validation failed", err)
    }

    entity := {Entity}{
        BaseEntity: basedomain.NewBaseEntity(id),
        Data:       data,
    }

    {{#if isAggregateRoot}}
    // Raise domain event
    entity.AddEvent(New{Entity}CreatedEvent(id, data))
    {{/if}}

    return entity, nil
}
\`\`\`
```

## Placeholder Reference

Standard placeholders available to all generators:

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{module}` | Go module path | `github.com/org/project` |
| `{project}` | Project name | `my-service` |
| `{context}` | Context name (lowercase) | `booking` |
| `{Context}` | Context name (PascalCase) | `Booking` |
| `{entity}` | Entity name (lowercase) | `cargo` |
| `{Entity}` | Entity name (PascalCase) | `Cargo` |
| `{entity_snake}` | Entity name (snake_case) | `cargo` |
| `{EntityId}` | Entity ID type | `TrackingId` |

## Validation Rules

Generators must ensure:

1. **No cross-context domain imports** - Domain packages must not import from other contexts
2. **Dependency direction** - All dependencies point inward (adapters → application → domain)
3. **Interface compliance** - Application services implement primary ports
4. **Event consistency** - Published events match declared domain events

## Adding a New Generator

1. Create directory: `generators/{generator-name}/`
2. Create `generator.md` with metadata and structure
3. Create `patterns/` directory with phase patterns
4. Register generator name in manifest schema
5. Test with sample BCR workspace

## Generator Testing

Each generator should include test cases:

```
generators/{generator-name}/
└── tests/
    ├── sample-bcr/           # Sample BCR input
    ├── expected-output/      # Expected generated code
    └── validation-rules.md   # What to validate
```
