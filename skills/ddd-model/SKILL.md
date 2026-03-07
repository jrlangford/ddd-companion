---
name: ddd-model
description: Decompose a system into well-defined Bounded Contexts using Domain-Driven Design principles. This command manages workflow state through a manifest file, enabling complex BCR work across multiple chat sessions.
argument-hint: "[prd-file-path]"
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

**Prefer Mermaid diagrams over ASCII/text diagrams** in all output files.

## Prerequisites

### PRD Required

Before starting BCR, you need a PRD with these sections:
- **Domain Glossary** — Key terms and definitions
- **Business Rules Catalog** — Explicit policies and constraints
- **Functional Areas** — Grouped features with cohesion rationale
- **Integration Touchpoints** — Where areas/systems interact
- **API Design Principles** (optional but recommended) — URL structure, versioning, response format, auth
- **Authorization Pattern** (optional) — How authorization decisions are made across contexts
- **Traceability Index** — Requirement IDs with Source Refs for end-to-end traceability

**PRD can be in any format** (Markdown, HTML, etc.). The skill reads the content, not the format.

### Authorization Pattern (Built-in)

This skill uses the **Permissions Object Pattern** for all generated contexts. The pattern definition and FQBC template live in `fqbc-template.md` Section 5 (Authorization) — that is the single source of truth.

Key points:
- Each microservice owns its role definitions — roles are not centralized
- Service middleware builds a Permissions object from authenticated identity (e.g., JWT claims)
- Handlers receive the object; they don't resolve roles themselves

This is the only authorization pattern currently supported by the implementation pipeline (`ddd-implement`).

### API Conventions (Built-in)

This skill includes `api-conventions.md` with standard HTTP API conventions. These defaults apply when the PRD doesn't specify API design principles. The conventions cover: URL structure, HTTP methods, query parameters, response envelopes, error handling, pagination, and date formats.

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

The manifest tracks workflow state. See `manifest-schema.md` for full schema and `manifest.schema.json` for validation.

**Reference**: `manifest-schema.md`

---

## Entry Point: First Message Handling

When invoked via `/ddd-model` or `/ddd-model [prd-path]`:

- If a PRD path argument is provided, use that file directly
- If no argument, auto-discover from `manifest.prd.path` (if manifest exists) or prompt the user

### Step 1: Check for Existing Manifest

Look for `ddd-model.manifest.json` in the workspace:
- `./ddd-workspace/ddd-model.manifest.json`

### Step 2: Resume or Start

**If manifest found:**
- Read it and validate against `manifest.schema.json` — report any missing required fields or invalid values before continuing. Examples:
  - Missing required field: `prd.format is required but missing — add "format": "md" or "html"`
  - Invalid enum value: `context status "waiting" is invalid — must be one of: pending, in_progress, complete, needsRevision`
  - If manifest is too corrupted to repair, suggest reconstructing from existing artifact files or starting fresh
- Report status, offer to continue (see `review-protocol.md` § Resuming Work template)

**If no manifest:**
- Check if PRD exists
- If no PRD, direct user to create one first (see `review-protocol.md` § New Workflow template)
- If PRD exists, suggest running `/ddd-prd validate [file]` if user hasn't already, then initialize workspace and start Phase 1
- Check PRD for authorization pattern; if not specified, inform user that Permissions Object Pattern will be used (see `review-protocol.md` § Authorization Pattern Confirmation)

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
4. Update manifest **immediately after confirmation** — never defer manifest writes, as a session may end at any point

### Principle: One FQBC at a Time

Phase 3 is designed for multiple executions. Each FQBC is a natural stopping point.

### Reference Documents

Read these for domain knowledge during generation:
- [fqbc-template.md](fqbc-template.md) — Complete FQBC document structure
- [context-mapping-patterns.md](context-mapping-patterns.md) — DDD integration patterns
- [api-conventions.md](api-conventions.md) — HTTP API design conventions for API bindings
- [review-protocol.md](review-protocol.md) — Response templates and user review summaries

---

## Workspace Initialization

Before Phase 1, set up the workspace:

1. Create `ddd-workspace/` directory with `prd/`, `bcr/`, and `fqbc/` subdirectories
2. Copy PRD to `ddd-workspace/prd/` (preserve original format)
3. **Verify PRD has required sections** — scan for Domain Glossary, Business Rules Catalog, Functional Areas, and Integration Touchpoints. If any are missing, **stop and report** which sections are absent. Suggest running `/ddd-prd validate [file]` and `/ddd-prd edit [file]` to fix the PRD before continuing.
4. **Check PRD for authorization pattern** — if not specified, inform user that Permissions Object Pattern will be used (see `review-protocol.md`)
5. Create `ddd-model.manifest.json` with PRD path, format, and authorization pattern (see `manifest-schema.md` for initial structure)

---

## Phase 1: Context Discovery

**Goal**: Identify candidate Bounded Contexts from PRD.

### Input
Read from PRD (path in `manifest.prd.path`):
- Domain Glossary
- Functional Areas
- Business Rules

### Actions

1. Analyze each functional area from the PRD for context boundaries using these heuristics:

   **Accept as its own context when:**
   - The area has its own ubiquitous language — terms mean something specific here that differs from other areas
   - It has a clear aggregate root with an independent lifecycle
   - It could be owned by a single team without heavy cross-team coordination
   - Its data has its own consistency boundary

   **Split a functional area into multiple contexts when:**
   - It contains terms that mean different things depending on sub-area
   - Parts of the area change at very different rates
   - It has distinct subdomain types — a core domain concern mixed with a generic/supporting concern

   **Merge functional areas into one context when:**
   - They share the same aggregate root and lifecycle
   - Splitting them would require constant synchronous communication between the two
   - The combined area is still small enough to reason about as a unit

2. Propose candidate contexts with rationale
3. Write `bcr/context-discovery.md`
4. **Present summary and request user review** (see `review-protocol.md` § After Phase 1)
5. Update manifest with contextsIdentified

**Note:** All contexts are deployed in a single service for POC. If contexts need to be split into independent microservices, each microservice should follow the full DDD pipeline independently.

---

## Phase 2: Context Mapping

**Goal**: Define relationships between contexts.

### Input
- `bcr/context-discovery.md`
- PRD → Integration Touchpoints section

### Actions

1. Determine relationships and patterns
2. **Shared Kernel decision gate**: For any proposed Shared Kernel relationship, explicitly justify why ACL is insufficient. Document the justification in `bcr/context-map.md`. If the shared concepts are still evolving, teams deploy independently, or the model is trivially duplicated — use ACL instead (see `context-mapping-patterns.md` for criteria).
3. Create context map with diagram
4. Write `bcr/context-map.md`
5. **Present summary and request user review** (see `review-protocol.md` § After Phase 2). **Flag any Shared Kernel relationships with their justification** for explicit user approval.
6. Update manifest

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

1. Check manifest for next pending context (status = `pending`)
   - If the context's status is already `complete`, prompt the user for confirmation before regenerating
2. Set that context's status to `in_progress` in the manifest
3. Read minimal required sections
4. Generate FQBC following fqbc-template.md
5. **Propagate Source Refs**: When populating FQBC Section 9 (Traceability), carry forward Source Ref IDs from the PRD Traceability Index into the PRD References table.
6. **Apply authorization pattern from manifest:**
   - For each Command and Query, specify required permissions
   - Document how the Permissions object is used
   - Specify authorization failure responses (403 Forbidden)
7. **If context exposes HTTP API** (skip if purely event-driven):
   - Read api-conventions.md for project-wide HTTP standards
   - Generate "API Binding" section (Section 7) with concrete paths
   - Map Commands/Queries to appropriate HTTP methods per conventions
   - Specify request/response schemas matching the response envelope
   - Document error codes for each failure scenario (including 403)
8. **Detect and highlight inconsistencies:**
   - Compare with previously generated FQBCs for path collisions
   - Check for queries that traverse the same relationship (consolidation candidates)
   - Flag any deviations from api-conventions.md
9. Write `fqbc/[context-name].md`
10. **Present summary and request user review** (see `review-protocol.md` § After Each FQBC)
11. Update manifest

### API Binding Guidance

| Domain Concept | HTTP Binding |
|----------------|--------------|
| Command (create) | POST to collection |
| Command (update) | PATCH to resource |
| Command (action) | PATCH to resource sub-path |
| Query (list) | GET collection with filters |
| Query (single) | GET resource by ID |

**Context slug**: Derive from context name using kebab-case (see `api-conventions.md` § Context Slug Derivation)

**Base path**: `/api/{context-slug}/v1/` (version is per-context, enabling independent evolution)

### Endpoint Consolidation Opportunities

Multiple interfaces may bind to the same underlying endpoint. When you detect this pattern, **highlight it for user review** and suggest consolidation.

**Example**: Consider "listing users assigned to a role" and "listing roles assigned to a user":
- Naive approach: Two separate endpoints
  - `GET /api/users/v1/users/{userId}/roles`
  - `GET /api/roles/v1/roles/{roleId}/users`
- Consolidated approach: One assignments endpoint with query params
  - `GET /api/role-assignments/v1/assignments?userId={userId}`
  - `GET /api/role-assignments/v1/assignments?roleId={roleId}`

**When to suggest consolidation**:
- Queries that traverse the same relationship in different directions
- Operations that share 80%+ of their data model
- CRUD operations on junction/association tables

**Action**: When you detect potential consolidation opportunities:
1. Flag the overlap in the FQBC summary
2. Present both the context-specific and consolidated options
3. **Ask the user to decide** which approach aligns with their service design
4. Suggest reviewing the service boundaries if many consolidation opportunities arise — this may indicate the contexts need restructuring into a more coherent design

---

## Phase 4: Coherence Review

**Goal**: Verify all context boundaries align and API surface is consistent.

### Input (Summaries Only)
- `bcr/context-map.md` (full file)
- Each `fqbc/*.md` → "Context Contract" and "API Binding" sections
- `api-conventions.md` → for validation against standards

### Checks

1. **Interface Compatibility**: Events/commands match between producers and consumers?
2. **Terminology Consistency**: Shared terms compatible?
3. **Coverage**: Every PRD requirement covered?
4. **Relationship Validation**: Upstream/downstream match?
5. **Authorization Consistency**: Pattern applied uniformly, permission naming consistent, 403 responses uniform
6. **API Surface Validation**: Path uniqueness, method consistency, parameter naming, response envelope, error codes

### Output: `bcr/coherence-review.md`

The coherence review document uses this structure:

1. **Cross-Context Consistency** — Interface compatibility, terminology, coverage checks
2. **API Surface Inventory** — All endpoints table + validation checklist
3. **Authorization Consistency** — Pattern, permission inventory, validation checklist
4. **API Binding Issues** — Table of issues found (if any)
5. **Consolidation Opportunities** — Overlapping queries across contexts (if any)
6. **Recommendations** — Summary of actions needed

Include an API Surface Inventory section:

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
| Non-standard param | C | Uses `page` instead of `offset` | Rename to `offset` |
```

### Endpoint Consolidation Review

In Phase 4, scan all FQBC API bindings for consolidation opportunities across contexts:

```markdown
### Consolidation Opportunities

| Contexts | Overlapping Queries | Suggested Consolidation |
|----------|---------------------|------------------------|
| A, B | A.ListXByY, B.ListYByX | Single `xy-assignments` resource with filters |
| C, D | C.GetStatus, D.GetStatus | Shared status endpoint or shared service |

**Recommendation**: If 3+ consolidation opportunities are detected, consider whether the bounded context boundaries need revision.
```

**Action when consolidation opportunities found:**
1. Document each opportunity with affected contexts
2. Present to user with clear recommendation
3. **Explicitly ask**: "Should we restructure these contexts, or accept the duplication?"
4. If restructuring chosen, mark affected FQBCs for regeneration

### Phase 4b: Revision Handling

If any contexts are flagged as `needsRevision` in the coherence review:

1. Check manifest for contexts with `status: "needsRevision"`
2. Present the specific coherence findings for that context to the user
3. Ask user whether to: **Revise** (update FQBC), **Accept as-is** (set to complete), or **Defer** (leave as needsRevision)
4. For revisions: re-read the FQBC, apply changes, update manifest
5. After all `needsRevision` contexts are resolved, set `currentPhase` to `complete`

---

## User Review Protocol

**Reference**: See `review-protocol.md` for all response templates, phase review summaries, chat transition guidance, and session resumption procedures.

**Key rule**: Pause and ask user to validate after every phase. The goal is user understanding of what will be built. API binding review is especially critical — explicitly ask user to verify paths and functionality.

---

## Error Recovery

### Mid-Phase Failure

If a phase fails partway through (e.g., context window exhaustion during FQBC generation):
1. The manifest reflects the last completed unit of work
2. Partially written files may exist — check the workspace
3. If the FQBC file is incomplete (truncated, missing sections, or status is `in_progress`), delete it and regenerate
4. Re-invoke `/ddd-model` — the skill reads the manifest and identifies the incomplete context

### Manifest Missing or Corrupted

Scan workspace for existing artifacts, reconstruct manifest from what exists, and confirm with user.

### PRD Missing or Incomplete

List what's missing, direct user to complete PRD first. Cannot proceed without required sections.

---

## Remember

1. **PRD is prerequisite** — must exist before starting
2. **Authorization pattern** — Permissions Object Pattern is the only supported pattern; inform user if PRD doesn't specify one
3. **Single service deployment** — all contexts deploy in one service for POC
4. **Read manifest first** — always check current state
5. **Minimal context loading** — only read what current phase needs
6. **Write files immediately** — don't accumulate in conversation
7. **One FQBC at a time** — Phase 3 is naturally chunked
8. **Clear transition guidance** — tell user how to resume with `/ddd-model`
9. **User review after each phase** — pause and ask user to validate before proceeding
10. **API binding review is critical** — explicitly ask user to verify paths
11. **Highlight inconsistencies** — proactively flag path collisions, naming issues, consolidation opportunities
12. **Suggest service review for consolidation** — if multiple interfaces bind to the same data, suggest restructuring into a more coherent design
