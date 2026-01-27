---
name: ddd-model
description: Decompose a system into well-defined Bounded Contexts using Domain-Driven Design principles. This command manages workflow state through a manifest file, enabling complex BCR work across multiple chat sessions.
disable-model-invocation: true
---

# Bounded Context Review (Multi-Session)

Decompose a system into well-defined Bounded Contexts using Domain-Driven Design principles. This command manages workflow state through a manifest file, enabling complex BCR work across multiple chat sessions without context window exhaustion.

**The manifest file is the shared state, not chat history.**

Each phase produces concrete artifact files. Any new chat can read the manifest, see what exists, and continue work. The project workspace persists between chats.

## Output Format

All generated artifacts are **Markdown documents** optimized for rendering in Obsidian or similar tools that natively support:
- Mermaid diagrams (rendered inline) — use for context maps, entity relationships, state diagrams, and workflows
- Tables (formatted and sortable) — use for glossaries, rule catalogs, interface definitions
- Checkbox lists (interactive) — use for progress tracking and verification checklists

**Prefer Mermaid diagrams over ASCII/text diagrams** in all output files. Mermaid renders properly in modern editors while ASCII art does not.

## Prerequisites

### PRD Required

Before starting BCR, you need a PRD with these sections:
- **Domain Glossary** — Key terms and definitions
- **Business Rules Catalog** — Explicit policies and constraints
- **Functional Areas** — Grouped features with cohesion rationale
- **Integration Touchpoints** — Where areas/systems interact
- **API Design Principles** (optional but recommended) — If the system exposes HTTP APIs, include:
  - URL structure preferences
  - Versioning strategy
  - Response format conventions
  - Authentication approach
- **Authorization Pattern** (optional) — How authorization decisions are made across contexts

**PRD can be in any format** (Markdown, HTML, etc.). The skill reads the content, not the format.

### Authorization Pattern (Built-in Default)

If the PRD does not specify an authorization pattern, **ask the user** before proceeding. Suggest the **Permissions Object Pattern** (also called Authorization Context Pattern) as the default.

**Permissions Object Pattern characteristics:**
- Each microservice owns its role definitions — roles are not centralized
- Middleware within the service builds a Permissions object from authenticated identity (e.g., JWT claims)
- The Permissions object encapsulates identity + resolved permissions for this service's domain
- Handlers/domain logic receive the object — they don't resolve roles themselves
- Authorization decisions use the object's methods (e.g., `hasAnyRole()`, `canAccess()`)

**Where permissions are built:**
- NOT at API Gateway (that's authentication, not authorization)
- AT the service's middleware layer, before request reaches handlers
- Each service resolves its own roles from the authenticated identity

**Why this pattern?**
- Separates authentication (who you are) from authorization (what you can do)
- Each service owns its authorization rules — no central authorization service
- Permissions resolved once at service middleware, not scattered through handlers
- Domain logic stays clean — receives Permissions object, doesn't build it
- Easy to test — inject a mock Permissions object

**Alternative patterns to offer if user prefers:**
- **Role-Based Access Control (RBAC)** — Contexts query a central role service
- **Attribute-Based Access Control (ABAC)** — Policies evaluate user/resource attributes
- **Context-Specific Authorization** — Each context owns its own authorization rules

### API Conventions (Built-in)

This skill includes `api-conventions.md` with standard HTTP API conventions. These defaults apply when:
- The PRD doesn't specify API design principles
- You need consistent API bindings across bounded contexts

The conventions cover: URL structure, HTTP methods, query parameters, response envelopes, error handling, pagination, and date formats.

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     BOUNDED CONTEXT REVIEW WORKFLOW                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [PRD] ─────────────────────────────────────────────────────────────────┐   │
│    │   Prerequisite: Must exist before BCR starts.                      │   │
│    │   Required sections: Glossary, Business Rules, Functional Areas    │   │
│  ──┴────────────────────────────────────────────────────────────────────┘   │
│        │                                                                    │
│        ▼                                                                    │
│  ┌──────────────┐     Produces:                                             │
│  │   Phase 1    │ ──► • bcr/context-discovery.md                            │
│  │   Context    │     • Candidate contexts with rationale                   │
│  │   Discovery  │                                                           │
│  └──────────────┘                                                           │
│        │                                                                    │
│        ▼                                                                    │
│  ┌──────────────┐     Produces:                                             │
│  │   Phase 2    │ ──► • bcr/context-map.md                                  │
│  │   Context    │     • Relationships and patterns                          │
│  │   Mapping    │                                                           │
│  └──────────────┘                                                           │
│        │                                                                    │
│        ▼                                                                    │
│  ┌──────────────┐     Produces (one per context):                           │
│  │   Phase 3    │ ──► • fqbc/[context-name].md                              │
│  │   FQBC Gen   │     • One sub-phase per context                           │
│  └──────────────┘                                                           │
│        │                                                                    │
│        ▼                                                                    │
│  ┌──────────────┐     Produces:                                             │
│  │   Phase 4    │ ──► • bcr/coherence-review.md                             │
│  │   Coherence  │     • Boundary alignment verification                     │
│  └──────────────┘     • Marks workflow complete                             │
│        │                                                                    │
│        ▼                                                                    │
│  [Complete: All artifacts ready for Claude Code]                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Directory Structure

All artifacts live in the project workspace:

```
ddd-workspace/
├── ddd-model.manifest.json    # Workflow state (READ THIS FIRST)
├── prd/                       # PRD location (any format)
│   └── [prd.md or prd.html]   # User's PRD document
├── bcr/
│   ├── context-discovery.md   # Phase 1 output
│   ├── context-map.md         # Phase 2 output
│   └── coherence-review.md    # Phase 4 output
└── fqbc/
    ├── [context-a].md         # Phase 3 outputs
    ├── [context-b].md
    └── ...
```

## Manifest Structure

The manifest tracks workflow state and PRD location:

```json
{
  "version": "1.0",
  "project_name": "Project Name",
  "created": "2025-01-18T10:00:00Z",
  "updated": "2025-01-18T14:30:00Z",
  "prd": {
    "ready": true,
    "path": "prd/prd.html",
    "format": "html"
  },
  "authorization": {
    "pattern": "permissions-object",
    "source": "user-selected",
    "notes": "Service middleware builds Permissions object from JWT claims"
  },
  "deployment": {
    "topology": "single-service | microservices",
    "services": {
      "order-service": ["ordering", "fulfillment"],
      "inventory-service": ["inventory"]
    },
    "notes": "For single-service, services field is omitted"
  },
  "current_phase": "fqbc_generation",
  "phases": {
    "context_discovery": {
      "status": "complete",
      "contexts_identified": ["ordering", "inventory", "fulfillment"],
      "deployment_topology": "single-service"
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
  "decisions": []
}
```

---

## Entry Point: First Message Handling

When invoked via `/ddd-model`:

### Step 1: Check for Existing Manifest

Look for `ddd-model.manifest.json` in the workspace:
- `./ddd-workspace/ddd-model.manifest.json`

### Step 2: Resume or Start

**If manifest found:**
- Read it, report status, offer to continue

**If no manifest:**
- Check if PRD exists
- If no PRD, direct user to create one first
- If PRD exists, initialize workspace and start Phase 1

### Response Template: Resuming Work

```markdown
## BCR Workflow Status

**Project**: [name]
**PRD**: [manifest.prd.path] ([format])
**Current Phase**: [phase name]
**Last Updated**: [timestamp]

### Progress
- [x] PRD Ready
- [x] Phase 1: Context Discovery (3 contexts)
- [x] Phase 2: Context Mapping
- [ ] Phase 3: FQBC Generation (2/3 complete)
  - [x] Ordering
  - [x] Inventory
  - [ ] Fulfillment ← **Next**
- [ ] Phase 4: Coherence Review

**Ready to generate FQBC for Fulfillment?**
```

### Response Template: New Workflow

```markdown
## Starting Bounded Context Review

To begin, I need a PRD with these sections:
- **Domain Glossary** — Key terms and definitions
- **Business Rules** — Explicit policies and constraints
- **Functional Areas** — Grouped features with cohesion rationale
- **Integration Touchpoints** — Where areas/systems interact

The PRD can be Markdown (.md) or HTML (.html).

Do you have a PRD ready?
- **Yes** — Share it or point me to the file
- **No** — Create one first before running /ddd-model

Once I have the PRD, I'll check for authorization patterns and initialize the workspace.
```

### Response Template: Authorization Pattern Required

If the PRD does not explicitly specify an authorization pattern, ask the user:

```markdown
## Authorization Pattern

The PRD doesn't specify how authorization will be handled across bounded contexts.

**Recommended: Permissions Object Pattern**

This pattern works well with DDD because:
- Middleware builds a Permissions object at the system boundary
- Contexts receive the object — they don't query roles themselves
- Authorization decisions use methods like `hasAnyRole()`, `canAccess()`
- Keeps domain logic clean; authorization is a cross-cutting concern

**How should we handle authorization?**

1. **Permissions Object Pattern** (Recommended)
   - Each microservice owns its role definitions
   - Service middleware builds Permissions object from authenticated identity (JWT claims)
   - Handlers receive the object — they don't query roles or external services
   - Authorization checks via `permissions.hasAnyRole('Admin', 'Manager')`

2. **Role-Based Access Control (RBAC)**
   - Contexts query a central authorization service
   - More coupling, but familiar pattern

3. **Attribute-Based Access Control (ABAC)**
   - Policy engine evaluates user + resource attributes
   - Most flexible, highest complexity

4. **Context-Specific Authorization**
   - Each context owns its authorization rules
   - Most autonomy, risk of inconsistency

Which pattern should we use? (Default: Permissions Object Pattern)
```

---

## Phase Execution Guidelines

### Principle: Minimal Context Loading

Each phase reads **only what it needs**:

| Phase | Reads | Produces |
|-------|-------|----------|
| 1: Context Discovery | PRD (from manifest.prd.path): glossary, rules, areas | bcr/context-discovery.md |
| 2: Context Mapping | context-discovery.md | bcr/context-map.md |
| 3: FQBC (per context) | context-discovery (this context), context-map (this context's relations) | fqbc/[name].md |
| 4: Coherence | context-map + all FQBC interfaces (summary only) | bcr/coherence-review.md |

### Principle: Write Files Immediately

Don't accumulate output in conversation:
1. Present summary to user in chat
2. Write full detail to file
3. User confirms
4. Update manifest

### Principle: One FQBC at a Time

Phase 3 is designed for multiple executions. Each FQBC is a natural stopping point.

### Reference Documents

Read these for domain knowledge during generation:
- [fqbc-template.md](fqbc-template.md) — Complete FQBC document structure
- [context-mapping-patterns.md](context-mapping-patterns.md) — DDD integration patterns
- [api-conventions.md](api-conventions.md) — HTTP API design conventions for API bindings

---

## Workspace Initialization

Before Phase 1, set up the workspace:

### Actions

1. Create `ddd-workspace/` directory
2. Create `prd/`, `bcr/`, and `fqbc/` subdirectories
3. Copy PRD to `ddd-workspace/prd/` (preserve original format)
4. **Check PRD for authorization pattern** — if not specified, ask user (see Response Template: Authorization Pattern Required)
5. Create `ddd-model.manifest.json` with PRD path, format, and authorization pattern

### Initial Manifest

```json
{
  "version": "1.0",
  "project_name": "[from PRD]",
  "created": "[timestamp]",
  "updated": "[timestamp]",
  "prd": {
    "ready": true,
    "path": "prd/prd.html",
    "format": "html"
  },
  "authorization": {
    "pattern": "[permissions-object|rbac|abac|context-specific]",
    "source": "[prd-specified|user-selected]",
    "notes": "[How/where permissions are resolved]"
  },
  "deployment": {
    "topology": "[single-service|microservices]",
    "services": {},
    "notes": "[Deployment model rationale — services field populated if microservices]"
  },
  "current_phase": "context_discovery",
  "phases": {
    "context_discovery": { "status": "pending", "contexts_identified": [], "deployment_topology": null },
    "context_mapping": { "status": "pending" },
    "fqbc_generation": { "status": "pending", "contexts": {} },
    "coherence_review": { "status": "pending" }
  },
  "decisions": []
}
```

---

## Phase 1: Context Discovery

**Goal**: Identify candidate Bounded Contexts from PRD.

### Input
Read from PRD (path in `manifest.prd.path`):
- Domain Glossary
- Functional Areas
- Business Rules

### Actions

1. Analyze for context boundaries using heuristics (see context-mapping-patterns.md)
2. Propose candidate contexts with rationale
3. **Ask about deployment topology** — will these contexts be deployed as a single service or multiple microservices? (see Response Template: Deployment Topology)
4. Write `bcr/context-discovery.md`
5. Update manifest with contexts_identified and deployment topology

### Response Template: Deployment Topology

After presenting discovered contexts, ask:

```markdown
## Deployment Topology

I've identified [N] bounded contexts. How will these be deployed?

1. **Single Service** (Recommended for most projects)
   - All contexts run in one deployable unit
   - Contexts communicate via in-process calls
   - Shared middleware builds Permissions object once per request
   - Simpler ops, lower latency, easier debugging

2. **Multiple Microservices**
   - Contexts grouped into separate deployables
   - Contexts communicate via HTTP/messaging
   - Each service has its own middleware layer
   - Independent scaling and deployment

Most projects start with a single service. Choose microservices only if you have specific scaling, team autonomy, or deployment requirements.

Which deployment model? (Default: Single Service)
```

### Response Template: Microservices Grouping

If user chooses "Multiple Microservices", ask for the grouping:

```markdown
## Microservices Grouping

How should the [N] bounded contexts be grouped into microservices?

**Discovered contexts:**
- Context A
- Context B
- Context C
- Context D

Please specify the grouping. Example format:

```
service-name-1: Context A, Context B
service-name-2: Context C
service-name-3: Context D
```

Each service will:
- Have its own middleware layer
- Build its own Permissions object from JWT claims
- Own the role definitions for its contexts
- Communicate with other services via HTTP/messaging
```

**Store in manifest:**
```json
"deployment": {
  "topology": "microservices",
  "services": {
    "service-name-1": ["context-a", "context-b"],
    "service-name-2": ["context-c"],
    "service-name-3": ["context-d"]
  },
  "notes": "User-defined grouping"
}
```

**Why this matters:**
- Single service: Contexts share middleware, Permissions object built once
- Multiple services: Each service builds its own Permissions object from JWT
- Affects how context relationships are implemented (method calls vs network calls)
- Contexts within same service use in-process calls; across services use HTTP

---

## Phase 2: Context Mapping

**Goal**: Define relationships between contexts.

### Input
- `bcr/context-discovery.md`
- PRD → Integration Touchpoints section

### Actions

1. Determine relationships and patterns
2. Create context map with diagram
3. Write `bcr/context-map.md`
4. Update manifest

---

## Phase 3: FQBC Generation (Per Context)

**Goal**: Generate FQBC for ONE context.

### Critical: One Context Per Execution

This is where context window savings are realized. Each FQBC is a separate file and a natural stopping point.

### Input (Minimal)
- `bcr/context-discovery.md` → only THIS context's section
- `bcr/context-map.md` → only THIS context's relationships
- PRD (from manifest) → only relevant glossary terms and business rules
- `api-conventions.md` → for HTTP API binding conventions (when context exposes API)
- `manifest.authorization` → authorization pattern for the project

### Actions

1. Check manifest for next pending context
2. Read minimal required sections
3. Generate FQBC following fqbc-template.md
4. **Apply authorization pattern from manifest:**
   - For each Command, specify required permissions
   - Document how the Permissions object is used (if Permissions Object Pattern)
   - Specify authorization failure responses (403 Forbidden)
5. **If context exposes HTTP API:**
   - Read api-conventions.md for project-wide HTTP standards
   - Generate "API Binding" section (Section 6) with concrete paths
   - Map Commands to appropriate HTTP methods per conventions
   - Map Queries to GET endpoints with standard parameter names
   - Specify request/response schemas matching the response envelope
   - Document error codes for each failure scenario (including 403 for authorization)
6. Write `fqbc/[context-name].md`
7. Update manifest

### API Binding Guidance

When generating API bindings:

| Domain Concept | HTTP Binding |
|----------------|--------------|
| Command (create) | POST to collection |
| Command (update) | PATCH to resource |
| Command (action) | PATCH to resource sub-path |
| Query (list) | GET collection with filters |
| Query (single) | GET resource by ID |

**Context slug**: Derive from context name using kebab-case (e.g., "Surveillance Items" → `surveillance-items`)

**Base path**: `/api/{context-slug}/v1/` (version is per-context, enabling independent evolution)

---

## Phase 4: Coherence Review

**Goal**: Verify all context boundaries align and API surface is consistent.

### Input (Summaries Only)
- `bcr/context-map.md` (full file)
- Each `fqbc/*.md` → "Published Interface" and "API Binding" sections
- `api-conventions.md` → for validation against standards

### Checks

1. **Interface Compatibility**: Events/commands match between producers and consumers?
2. **Terminology Consistency**: Shared terms compatible?
3. **Coverage**: Every PRD requirement covered?
4. **Relationship Validation**: Upstream/downstream match?
5. **Authorization Consistency**:
   - Pattern applied uniformly: All contexts use the same authorization pattern from manifest
   - Permission naming: Similar operations use consistent permission names
   - Permissions object usage: All contexts expect permissions passed the same way
   - Failure responses: All contexts return 403 with consistent error structure
6. **API Surface Validation**:
   - Path uniqueness: No collisions across contexts
   - Method consistency: Similar operations use same HTTP methods
   - Parameter naming: All contexts use standard names (page, pageSize, etc.)
   - Response envelope: All contexts use consistent envelope structure
   - Error codes: Consistent error code usage across contexts

### Output: API Path Inventory

In `bcr/coherence-review.md`, include an API Surface Inventory section:

```markdown
## API Surface Inventory

### All Endpoints

| Context | Operation | Method | Full Path |
|---------|-----------|--------|-----------|
| role-management | ListRoles | GET | `/api/role-management/v1/roles` |
| role-management | AssignRole | POST | `/api/role-management/v1/assignments` |
| surveillance-items | ListItems | GET | `/api/surveillance-items/v1/items` |
| surveillance-items | UpdateStatus | PATCH | `/api/surveillance-items/v1/items/{id}/status` |
| ... | ... | ... | ... |

### Validation Results

- [ ] No path collisions detected
- [ ] HTTP methods consistent across similar operations
- [ ] Query parameter names follow conventions
- [ ] Response envelopes consistent
- [ ] Error codes standardized

## Authorization Consistency

### Pattern Applied

**Authorization Pattern**: [From manifest — e.g., Permissions Object Pattern]

### Permission Inventory

| Context | Operation | Required Permission |
|---------|-----------|---------------------|
| ordering | CreateOrder | `permissions.hasAnyRole('Customer', 'Admin')` |
| ordering | CancelOrder | `permissions.hasAnyRole('Admin')` |
| inventory | UpdateStock | `permissions.hasAnyRole('WarehouseStaff', 'Admin')` |
| ... | ... | ... |

### Authorization Validation

- [ ] All contexts use the same authorization pattern
- [ ] Permission checks use consistent method names
- [ ] 403 responses use consistent error structure
- [ ] No context queries external role services (Permissions Object Pattern)
```

### Coherence Issues

If API binding issues are found, document them:

```markdown
### API Binding Issues

| Issue | Context | Details | Recommendation |
|-------|---------|---------|----------------|
| Path collision | A, B | Both use `/api/v1/items` | Prefix with context slug |
| Method inconsistency | A | Uses PUT for partial update | Change to PATCH |
| Non-standard param | C | Uses `limit` instead of `pageSize` | Rename to `pageSize` |
```

---

## Chat Transition Guidance

### After Each Phase

```markdown
**Phase [N] complete.**

Next: Phase [N+1] — [name]

Continue now, or pause and resume later with `/ddd-model`
```

### After FQBC (Mid-Phase 3)

```markdown
**[Context] FQBC complete.** ([N]/[Total])

Next: Generate FQBC for **[next context]**

Continue, or pause here—good stopping point.
```

### Workflow Complete

```markdown
## BCR Workflow Complete!

### Deliverables

All artifacts in `ddd-workspace/`:

**Bounded Context Review:**
- bcr/context-discovery.md
- bcr/context-map.md
- bcr/coherence-review.md

**FQBCs:**
- fqbc/[context-name].md (one per context)

These are ready to feed into Claude Code for implementation.
```

---

## Error Recovery

### Manifest Missing or Corrupted

1. Scan workspace for existing artifacts
2. Reconstruct manifest from what exists
3. Confirm with user

### PRD Missing or Incomplete

If PRD lacks required sections (Glossary, Business Rules, Functional Areas):
- List what's missing
- Direct user to complete PRD first
- Cannot proceed without PRD

---

## Remember

1. **PRD is prerequisite** — must exist before starting
2. **Authorization pattern required** — if not in PRD, ask user (suggest Permissions Object Pattern)
3. **Deployment topology required** — ask after context discovery (suggest Single Service)
4. **Read manifest first** — always check current state
5. **Minimal context loading** — only read what current phase needs
6. **Write files immediately** — don't accumulate in conversation
7. **One FQBC at a time** — Phase 3 is naturally chunked
8. **Clear transition guidance** — tell user how to resume with `/ddd-model`
