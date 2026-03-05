# Manifest Schema Reference

The manifest file (`ddd-model.manifest.json`) tracks workflow state and enables resumption across chat sessions.

## Location

`ddd-workspace/ddd-model.manifest.json`

## Schema

```json
{
  "version": "1.0",
  "project_name": "string",
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
  "current_phase": "phase_name | complete",
  "phases": {
    "context_discovery": { 
      "status": "pending|in_progress|complete",
      "contexts_identified": ["ctx1", "ctx2"]
    },
    "context_mapping": { 
      "status": "pending|in_progress|complete" 
    },
    "fqbc_generation": {
      "status": "pending|in_progress|complete",
      "contexts": {
        "context_name": { "status": "pending|in_progress|complete|needs_revision" }
      }
    },
    "coherence_review": { 
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
| 1 | context_discovery | Identify bounded contexts from PRD |
| 2 | context_mapping | Define relationships between contexts |
| 3 | fqbc_generation | Generate FQBCs (one per context) |
| 4 | coherence_review | Verify boundary alignment |

## Status Values

- `pending` — Not yet started
- `in_progress` — Currently active
- `complete` — Finished

For FQBC contexts:
- `needs_revision` — Coherence review found issues

## Example: Fresh Manifest

```json
{
  "version": "1.0",
  "project_name": "E-Commerce Platform",
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
  "current_phase": "context_discovery",
  "phases": {
    "context_discovery": { "status": "pending", "contexts_identified": [] },
    "context_mapping": { "status": "pending" },
    "fqbc_generation": { "status": "pending", "contexts": {} },
    "coherence_review": { "status": "pending" }
  },
  "decisions": []
}
```

## Example: Mid-Workflow (FQBC Phase)

```json
{
  "version": "1.0",
  "project_name": "E-Commerce Platform",
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
  "current_phase": "fqbc_generation",
  "phases": {
    "context_discovery": { 
      "status": "complete",
      "contexts_identified": ["ordering", "inventory", "fulfillment"]
    },
    "context_mapping": { "status": "complete" },
    "fqbc_generation": {
      "status": "in_progress",
      "contexts": {
        "ordering": { "status": "complete" },
        "inventory": { "status": "complete" },
        "fulfillment": { "status": "pending" }
      }
    },
    "coherence_review": { "status": "pending" }
  },
  "decisions": [
    {
      "phase": "context_discovery",
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
  "project_name": "E-Commerce Platform",
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
  "current_phase": "complete",
  "phases": {
    "context_discovery": { 
      "status": "complete",
      "contexts_identified": ["ordering", "inventory", "fulfillment"]
    },
    "context_mapping": { "status": "complete" },
    "fqbc_generation": {
      "status": "complete",
      "contexts": {
        "ordering": { "status": "complete" },
        "inventory": { "status": "complete" },
        "fulfillment": { "status": "complete" }
      }
    },
    "coherence_review": { "status": "complete" }
  },
  "decisions": [
    {
      "phase": "context_discovery",
      "decision": "Split Stock into Inventory and Fulfillment",
      "rationale": "Different consistency requirements",
      "timestamp": "2025-01-18T11:15:00Z"
    },
    {
      "phase": "coherence_review",
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
                     needs_revision → in_progress → complete
```

- `pending`: FQBC not yet generated
- `in_progress`: Currently generating this FQBC
- `complete`: FQBC written and confirmed by user
- `needs_revision`: Coherence review (Phase 4) found issues requiring FQBC updates

When a context enters `needs_revision`, its FQBC must be updated and the status reset to `in_progress` → `complete` before the coherence review can pass.

### Overall Workflow Status (`current_phase`)

```
context_discovery → context_mapping → fqbc_generation → coherence_review → complete
```

Set to `"complete"` when Phase 4 passes with no blocking issues.

---

## Operations

### Finding Next FQBC

```javascript
const fqbcPhase = manifest.phases.fqbc_generation;
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
manifest.phases.context_discovery.status = 'complete';
manifest.phases.context_discovery.contexts_identified = ['ordering', 'inventory'];
manifest.current_phase = 'context_mapping';
manifest.updated = new Date().toISOString();
```

### Recording a Decision

```javascript
manifest.decisions.push({
  phase: 'context_discovery',
  decision: 'Split Stock into Inventory and Fulfillment',
  rationale: 'Different consistency requirements',
  timestamp: new Date().toISOString()
});
```
