# Implement Manifest Guide

This document describes the structure and semantics of the `ddd-implement.manifest.json` file used to track generation progress across sessions.

For JSON Schema validation, see `manifest.schema.json`.

## Phase Progression

Phases progress strictly forward:

```
support → contexts → drivingAdapters → apiContracts → mainWiring → validation → complete
```

Each phase requires the previous phase to be `complete` before starting. The `currentPhase` field in the manifest reflects the active phase.

## Full Manifest Example

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

## Key Manifest Fields

| Field | Purpose |
|-------|---------|
| `currentPhase` | Where in the overall workflow: `init`, `support`, `contexts`, `drivingAdapters`, `apiContracts`, `mainWiring`, `validation`, `complete` |
| `currentContext` | Which context is being processed (null if between contexts) |
| `contexts[].status` | `pending`, `in_progress`, `complete`, `error` |
| `contexts[].generatedFiles` | Array of file paths created for each phase |
| `contexts[].errors` | Any errors encountered during generation |
| `apiContracts.status` | Status of TypeSpec contract generation |
| `drivingAdapters.http.status` | Status of HTTP adapter generation |
| `history` | Audit log of completed operations |

## Status Transitions

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
support → contexts → drivingAdapters → apiContracts → mainWiring → validation → complete
```
