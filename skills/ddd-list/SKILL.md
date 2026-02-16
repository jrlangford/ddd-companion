---
name: ddd-list
description: Inspect bounded contexts, domain models, and events across the DDD workspace
argument-hint: "[domains|events]"
---

# DDD Workspace Inspector

Read-only inspection of the current DDD workspace state. Shows bounded contexts, domain model elements, and domain event flows.

## Data Sources

All reads are non-destructive. The skill never writes or modifies files.

| Source | Path | Purpose |
|--------|------|---------|
| Model manifest | `ddd-workspace/ddd-model.manifest.json` | Context names, modeling phase/status |
| FQBC files | `ddd-workspace/fqbc/*.md` | Domain models, events, relationships |
| Implement manifest | `ddd-workspace/ddd-implement.manifest.json` | Implementation status (optional enrichment) |

## Commands

| Command | Description |
|---------|-------------|
| `/ddd-list` | Dashboard summary of domains + events |
| `/ddd-list domains` | All bounded contexts with entities, value objects, aggregates |
| `/ddd-list events` | All domain events with publishers and consumers |

---

## Entry Point

### Actions

1. Check $ARGUMENTS for a sub-command (`domains` or `events`)
2. Locate the workspace directory — look for `ddd-workspace/` in the current project root
3. If no `ddd-workspace/` directory exists, show the [No Workspace](#error-no-workspace) error
4. Read `ddd-workspace/ddd-model.manifest.json`
   - If missing, show the [No Manifest](#error-no-manifest) error
5. Determine which FQBC files exist by checking `ddd-workspace/fqbc/*.md`
6. Optionally read `ddd-workspace/ddd-implement.manifest.json` for implementation status
7. Route to the appropriate sub-command (or default dashboard)

---

## Command: Dashboard (default)

When invoked without arguments, display a high-level workspace overview.

### Actions

1. Read `ddd-workspace/ddd-model.manifest.json` for:
   - `project_name`
   - `current_phase` and phase statuses
   - Context names from `phases.fqbc_generation.contexts`
2. For each context with status `complete` in fqbc_generation, read the corresponding FQBC file at `ddd-workspace/fqbc/{context-name}.md`
3. From each FQBC, extract:
   - **Section 4 (Domain Model)**: count of aggregates, entities, value objects
   - **Section 6 (Published Interface) — Outbound Events**: event names and consumer contexts
4. If `ddd-workspace/ddd-implement.manifest.json` exists, read it for:
   - `currentPhase`
   - Per-context `status` from the `contexts` array
   - `validation.build` status

### Output

```markdown
## DDD Workspace Dashboard

**Project**: [project_name]
**Modeling Phase**: [current_phase]
**Implementation**: [currentPhase from implement manifest, or "Not started"]

### Bounded Contexts

| Context | Model Status | Impl Status | Aggregates | Entities | Value Objects | Events |
|---------|-------------|-------------|------------|----------|---------------|--------|
| [name]  | [complete/in_progress/pending] | [status or —] | [count] | [count] | [count] | [count] |
| ...     | ...         | ...         | ...        | ...      | ...           | ...    |

### Domain Events Overview

| Event | Publisher | Consumers |
|-------|----------|-----------|
| [EventName] | [context] | [context-a], [context-b] |
| ...   | ...      | ...       |

### Pipeline Progress

- [x] Context Discovery — [N] contexts identified
- [x/pending] Context Mapping
- [partial/complete] FQBC Generation — [M/N] complete
- [x/pending] Coherence Review
- [status] Implementation — [status summary]

### Quick Commands

- `/ddd-list domains` — detailed domain model per context
- `/ddd-list events` — full event catalog with payloads
```

---

## Command: Domains

**Usage**: `/ddd-list domains`

List all bounded contexts with their full domain model details.

### Actions

1. Read `ddd-workspace/ddd-model.manifest.json` for the context list
2. For each context with a completed FQBC file, read `ddd-workspace/fqbc/{context-name}.md`
3. From each FQBC, extract:
   - **Section 1 (Context Identity)**: name, description
   - **Section 4 (Domain Model)**:
     - Aggregates: root entity, invariants, contained entities and value objects
     - Entities: identity, key attributes, lifecycle
     - Value Objects: attributes, equality semantics
     - Domain Services (if present)
     - Business Rules
   - **Section 8 (Context Relationships)**: upstream/downstream dependencies
4. If `ddd-workspace/ddd-implement.manifest.json` exists, enrich with:
   - Per-context implementation status
   - Per-phase status (`domain`, `ports`, `application`, `drivenAdapters`, `mock`)
   - Generated file counts

### Output

```markdown
## Bounded Contexts — Domain Models

**Project**: [project_name]
**Contexts**: [N] identified, [M] fully modeled

---

### [Context Name]

**Description**: [from Section 1]
**Model Status**: [complete/in_progress/pending]
**Impl Status**: [status or "Not started"]

#### Aggregates

| Aggregate Root | Invariants | Entities | Value Objects | States |
|---------------|------------|----------|---------------|--------|
| [root entity] | [count] | [list] | [list] | [lifecycle states] |

#### Entities

| Entity | Identity | Key Attributes | Lifecycle |
|--------|----------|----------------|-----------|
| [name] | [identity field] | [attributes] | [states] |

#### Value Objects

| Value Object | Attributes | Equality |
|-------------|------------|----------|
| [name]      | [attributes] | [equality semantics] |

#### Business Rules

| ID | Rule | Type | Enforced By |
|----|------|------|-------------|
| [BR-xx] | [statement] | [Invariant/Precondition/...] | [aggregate or service] |

#### Relationships

| Direction | Context | Pattern | Description |
|-----------|---------|---------|-------------|
| Upstream  | [name]  | [pattern] | [what this context consumes] |
| Downstream | [name] | [pattern] | [what this context provides] |

#### Implementation Progress

| Phase | Status |
|-------|--------|
| Domain | [status] |
| Ports | [status] |
| Application | [status] |
| Driven Adapters | [status] |
| Mock | [status] |

---

### [Next Context Name]
...
```

#### When FQBC is not yet generated for a context

If a context appears in the manifest but has no FQBC file or its fqbc_generation status is not `complete`:

```markdown
### [Context Name]

**Model Status**: [status from manifest]
**FQBC**: Not yet generated

_Run `/ddd-model` to continue modeling this context._
```

---

## Command: Events

**Usage**: `/ddd-list events`

List all domain events across the workspace with their publishers, consumers, and payloads.

### Actions

1. Read `ddd-workspace/ddd-model.manifest.json` for the context list
2. For each context with a completed FQBC file, read `ddd-workspace/fqbc/{context-name}.md`
3. From each FQBC, extract **Section 6 (Published Interface) — Outbound Events**:
   - Event name
   - Trigger (what causes the event)
   - Payload fields
   - Consumer contexts
   - Delivery guarantees
4. Compile a cross-context event catalog
5. If `ddd-workspace/ddd-implement.manifest.json` exists, check per-context `domainEvents` arrays for additional correlation

### Output

```markdown
## Domain Events Catalog

**Project**: [project_name]
**Total Events**: [count]
**Publishing Contexts**: [count]
**Subscribing Contexts**: [count]

### Events by Publisher

#### [Context Name] — [N] events

| Event | Trigger | Payload | Consumers | Delivery |
|-------|---------|---------|-----------|----------|
| [EventName] | [what triggers it] | [key fields] | [context-a], [context-b] | [at-least-once/...] |

---

#### [Next Context Name] — [N] events
...

### Event Flow Summary

```
[Context A] ──EventX──▶ [Context B]
[Context A] ──EventY──▶ [Context C]
[Context B] ──EventZ──▶ [Context C]
```

### Contexts With No Events

| Context | Reason |
|---------|--------|
| [name]  | No outbound events defined |

_Note: Contexts without outbound events may still consume events from other contexts._
```

#### When no events are found

```markdown
## Domain Events Catalog

**Project**: [project_name]

No domain events found in the workspace.

Possible reasons:
- FQBC files have not been generated yet — run `/ddd-model`
- Bounded contexts don't define outbound events (unusual for multi-context systems)
```

---

## Error Handling

### Error: No Workspace

When `ddd-workspace/` directory does not exist:

```markdown
## No DDD Workspace Found

No `ddd-workspace/` directory found in the current project.

**To get started with the DDD pipeline:**
1. `/ddd-extract-prd [source]` — extract a PRD from your documentation
2. `/ddd-model` — model bounded contexts from the PRD
3. `/ddd-implement` — generate a walking skeleton

The workspace directory is created automatically by these skills.
```

### Error: No Manifest

When `ddd-workspace/` exists but `ddd-model.manifest.json` is missing:

```markdown
## No Model Manifest Found

The `ddd-workspace/` directory exists but has no `ddd-model.manifest.json`.

This means bounded context modeling hasn't started yet.

**Next step**: Run `/ddd-model` to begin modeling bounded contexts from your PRD.
```

### Error: No FQBCs

When the manifest exists but no FQBC files are found in `ddd-workspace/fqbc/`:

```markdown
## No FQBC Documents Found

The model manifest exists but no FQBC files have been generated yet.

**Modeling Progress**:
- Current Phase: [current_phase from manifest]
- Contexts Identified: [list from context_discovery]

**Next step**: Run `/ddd-model` to continue — it will resume from the current phase.
```
