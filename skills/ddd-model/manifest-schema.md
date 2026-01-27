# Manifest Schema Reference

The manifest file (`manifest.json`) tracks workflow state and enables resumption across chat sessions.

## Location

`ddd-workspace/manifest.json`

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
