# Manifest Schema Reference

The manifest file (`ddd-model.manifest.json`) tracks workflow state and enables resumption across chat sessions.

## Location

`ddd-workspace/ddd-model.manifest.json`

## Schema

```json
{
  "version": "1.0",
  "projectName": "string",
  "created": "ISO-8601 datetime",
  "updated": "ISO-8601 datetime",
  "prd": {
    "ready": true,
    "path": "prd/filename.ext",
    "format": "md|html"
  },
  "authorization": {
    "pattern": "permissions-object",
    "source": "prd-specified|default",
    "notes": "string"
  },
  "deployment": {
    "topology": "single-service",
    "notes": "string"
  },
  "currentPhase": "phase_name | complete",
  "phases": {
    "contextDiscovery": { 
      "status": "pending|in_progress|complete",
      "contextsIdentified": ["ctx1", "ctx2"]
    },
    "contextMapping": { 
      "status": "pending|in_progress|complete" 
    },
    "fqbcGeneration": {
      "status": "pending|in_progress|complete",
      "contexts": {
        "context_name": { "status": "pending|in_progress|complete|needsRevision" }
      }
    },
    "coherenceReview": { 
      "status": "pending|in_progress|complete" 
    }
  },
  "decisions": []
}
```

## PRD Object

The `prd` field tracks the prerequisite PRD document:

| Field | Type | Description |
|-------|------|-------------|
| ready | boolean | Whether PRD is available |
| path | string | Relative path to PRD file |
| format | string | File format: `md` or `html` |

## Authorization Object

The `authorization` field records the authorization pattern used across all bounded contexts:

| Field | Type | Description |
|-------|------|-------------|
| pattern | string | Authorization pattern: `permissions-object` (only supported value) |
| source | string | How the pattern was determined: `prd-specified` or `default` |
| notes | string | How/where permissions are resolved |

## Deployment Object

The `deployment` field records the deployment topology for the PoC:

| Field | Type | Description |
|-------|------|-------------|
| topology | string | Deployment model: `single-service` for PoC |
| notes | string | Additional deployment context |

## Phases

| Phase | Name in Manifest | Description |
|-------|------------------|-------------|
| 1 | contextDiscovery | Identify bounded contexts from PRD |
| 2 | contextMapping | Define relationships between contexts |
| 3 | fqbcGeneration | Generate FQBCs (one per context) |
| 4 | coherenceReview | Verify boundary alignment |

## Status Values

- `pending` — Not yet started
- `in_progress` — Currently active
- `complete` — Finished

For FQBC contexts:
- `needsRevision` — Coherence review found issues

## Example: Fresh Manifest

```json
{
  "version": "1.0",
  "projectName": "E-Commerce Platform",
  "created": "2025-01-18T10:00:00Z",
  "updated": "2025-01-18T10:00:00Z",
  "prd": {
    "ready": true,
    "path": "prd/prd.html",
    "format": "html"
  },
  "authorization": {
    "pattern": "permissions-object",
    "source": "default",
    "notes": "Permissions resolved from JWT claims"
  },
  "deployment": {
    "topology": "single-service",
    "notes": "All contexts deployed as one service for PoC"
  },
  "currentPhase": "contextDiscovery",
  "phases": {
    "contextDiscovery": { "status": "pending", "contextsIdentified": [] },
    "contextMapping": { "status": "pending" },
    "fqbcGeneration": { "status": "pending", "contexts": {} },
    "coherenceReview": { "status": "pending" }
  },
  "decisions": []
}
```

## Example: Mid-Workflow (FQBC Phase)

```json
{
  "version": "1.0",
  "projectName": "E-Commerce Platform",
  "created": "2025-01-18T10:00:00Z",
  "updated": "2025-01-18T14:30:00Z",
  "prd": {
    "ready": true,
    "path": "prd/prd.html",
    "format": "html"
  },
  "authorization": {
    "pattern": "permissions-object",
    "source": "prd-specified",
    "notes": "Role-based permissions from Role-Capability Matrix (PRD §10)"
  },
  "deployment": {
    "topology": "single-service",
    "notes": "All contexts deployed as one service for PoC"
  },
  "currentPhase": "fqbcGeneration",
  "phases": {
    "contextDiscovery": { 
      "status": "complete",
      "contextsIdentified": ["ordering", "inventory", "fulfillment"]
    },
    "contextMapping": { "status": "complete" },
    "fqbcGeneration": {
      "status": "in_progress",
      "contexts": {
        "ordering": { "status": "complete" },
        "inventory": { "status": "complete" },
        "fulfillment": { "status": "pending" }
      }
    },
    "coherenceReview": { "status": "pending" }
  },
  "decisions": [
    {
      "phase": "contextDiscovery",
      "decision": "Split Stock into Inventory and Fulfillment",
      "rationale": "Different consistency requirements",
      "timestamp": "2025-01-18T11:15:00Z"
    }
  ]
}
```

## Example: Complete Workflow

```json
{
  "version": "1.0",
  "projectName": "E-Commerce Platform",
  "created": "2025-01-18T10:00:00Z",
  "updated": "2025-01-18T16:00:00Z",
  "prd": {
    "ready": true,
    "path": "prd/prd.html",
    "format": "html"
  },
  "authorization": {
    "pattern": "permissions-object",
    "source": "prd-specified",
    "notes": "Role-based permissions from Role-Capability Matrix (PRD §10)"
  },
  "deployment": {
    "topology": "single-service",
    "notes": "All contexts deployed as one service for PoC"
  },
  "currentPhase": "complete",
  "phases": {
    "contextDiscovery": { 
      "status": "complete",
      "contextsIdentified": ["ordering", "inventory", "fulfillment"]
    },
    "contextMapping": { "status": "complete" },
    "fqbcGeneration": {
      "status": "complete",
      "contexts": {
        "ordering": { "status": "complete" },
        "inventory": { "status": "complete" },
        "fulfillment": { "status": "complete" }
      }
    },
    "coherenceReview": { "status": "complete" }
  },
  "decisions": [
    {
      "phase": "contextDiscovery",
      "decision": "Split Stock into Inventory and Fulfillment",
      "rationale": "Different consistency requirements",
      "timestamp": "2025-01-18T11:15:00Z"
    },
    {
      "phase": "coherenceReview",
      "decision": "Added currency to OrderPlaced event",
      "rationale": "Fulfillment needs currency for international shipping",
      "timestamp": "2025-01-18T15:50:00Z"
    }
  ]
}
```

## Status Transitions

### Phase Status

```
pending → in_progress → complete
```

- `pending`: Not yet started
- `in_progress`: Currently active (only one phase at a time)
- `complete`: Finished and artifacts written

Phases progress strictly forward. A completed phase does not revert to `in_progress` unless the coherence review flags issues (see FQBC context status below).

### FQBC Context Status

```
pending → in_progress → complete
                           │
                           ▼
                     needsRevision → in_progress → complete
```

- `pending`: FQBC not yet generated
- `in_progress`: Currently generating this FQBC
- `complete`: FQBC written and confirmed by user
- `needsRevision`: Coherence review (Phase 4) found issues requiring FQBC updates

When a context enters `needsRevision`, its FQBC must be updated and the status reset to `in_progress` → `complete` before the coherence review can pass.

### Overall Workflow Status (`currentPhase`)

```
contextDiscovery → contextMapping → fqbcGeneration → coherenceReview → complete
```

Set to `"complete"` when Phase 4 passes with no blocking issues.

---

## Operations

### Finding Next FQBC

```javascript
const fqbcPhase = manifest.phases.fqbcGeneration;
const nextContext = Object.entries(fqbcPhase.contexts)
  .find(([name, ctx]) => ctx.status === 'pending');

if (nextContext) {
  return nextContext[0];  // context name
} else {
  return null;  // all complete
}
```

### Updating After Phase Completion

```javascript
manifest.phases.contextDiscovery.status = 'complete';
manifest.phases.contextDiscovery.contextsIdentified = ['ordering', 'inventory'];
manifest.currentPhase = 'contextMapping';
manifest.updated = new Date().toISOString();
```

### Recording a Decision

```javascript
manifest.decisions.push({
  phase: 'contextDiscovery',
  decision: 'Split Stock into Inventory and Fulfillment',
  rationale: 'Different consistency requirements',
  timestamp: new Date().toISOString()
});
```
