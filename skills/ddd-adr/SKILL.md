---
name: ddd-adr
description: Create and manage DDD-aware Architecture Decision Records
argument-hint: "[new|show|seed|supersede] [title-or-number]"
---

# DDD Architecture Decision Records

Create, list, and manage Architecture Decision Records that are DDD-aware. Designed to capture decisions that matter most in DDD projects: bounded context boundaries, integration patterns, and **deliberate divergences from DDD purity**.

Unlike generic ADRs, these records understand bounded contexts, hexagonal architecture, and the DDD Companion pipeline artifacts.

## ADR Location

- **Workspace mode** — when `ddd-workspace/` exists: `ddd-workspace/adr/`
- **Standalone mode** — no workspace: `docs/adr/`

ADR files are named `NNNN-kebab-case-title.md` (auto-incrementing from the highest existing number).

## Data Sources

| Source | Purpose |
|--------|---------|
| `ddd-workspace/adr/*.md` | Existing ADR documents |
| `ddd-workspace/ddd-model.manifest.json` | Workflow decisions array, context names |
| `ddd-workspace/fqbc/*.md` | Section 9 design decisions, context relationships |
| `ddd-workspace/ddd-implement.manifest.json` | Implementation status per context |
| Eval output | Pragmatic vs. purity divergences (from `/ddd-eval` synthesis) |

## Commands

| Command | Description |
|---------|-------------|
| `/ddd-adr` | Dashboard — list all ADRs with status and classification |
| `/ddd-adr new [title]` | Create a new ADR interactively |
| `/ddd-adr show [number]` | Display a specific ADR with related decisions |
| `/ddd-adr seed` | Generate ADR drafts from pipeline artifacts and eval divergences |
| `/ddd-adr supersede [number]` | Create a new ADR that supersedes an existing one |

## Classifications

Each ADR is assigned one classification from a fixed vocabulary that maps to DDD concepts:

| Classification | When to Use | Example |
|----------------|-------------|---------|
| Boundary | Bounded context boundary decisions — merging, splitting, scope | "Split Stock into Inventory and Fulfillment" |
| Pattern | Choosing a specific DDD tactical pattern | "Use Aggregate Root pattern for Order with OrderLine entities" |
| Integration | How bounded contexts communicate | "ACL pattern for broker-to-quote communication via events" |
| Purity Divergence | Deliberate deviation from strict DDD/hexagonal purity | "Share SecurityRepository across contexts as reference data" |
| Infrastructure | Cross-cutting technical decisions | "Permissions Object pattern for authorization" |

---

## ADR Document Template

Every ADR follows this DDD-aware format:

```markdown
# NNNN. [Title]

**Date**: [YYYY-MM-DD]
**Status**: Proposed | Accepted | Deprecated | Superseded by [NNNN]

## Classification

**Type**: [Boundary | Pattern | Integration | Purity Divergence | Infrastructure]
**Affected Contexts**: [Context A, Context B]
**DDD Patterns Involved**: [Aggregate Root, ACL, Shared Kernel, Published Language, etc.]

## Context

[What is the issue that motivates this decision? What forces are at play?
Include business drivers, technical constraints, and team considerations.]

## Decision

[What is the change that we are proposing and/or doing?
State the decision clearly and concisely.]

## Purity Impact

<!--
  Include this section when the decision deliberately deviates from
  strict DDD or hexagonal architecture purity.
  Remove this section entirely for decisions that are purity-neutral.
-->

**Deviation**: [What DDD/hexagonal rule or pattern is being bent?]
**Purity Cost**: [What structural purity is lost? What becomes harder?]
**Pragmatic Benefit**: [What practical value is gained? Why is the trade-off worth it?]
**Mitigations**: [How do we limit the blast radius? What guardrails are in place?]

## Consequences

### Positive
- [consequence]

### Negative
- [consequence]

## Pipeline References

| Artifact | Reference | Notes |
|----------|-----------|-------|
| PRD | [FR-XX, BR-XX] | [requirement driving this decision] |
| FQBC | [context] Section [N] | [relevant model element] |
| Eval Finding | [divergence description] | [from eval synthesis] |
| Manifest Decision | [decision text] | [from decisions[] array] |
```

### Purity Impact Section

The **Purity Impact** section is what makes this ADR format DDD-specific. It structures the rationale for deliberate deviations with four fields:

- **Deviation** — name the specific rule being bent (e.g., "Cross-context domain import", "Shared kernel for reference data", "Application service bypasses port interface")
- **Purity Cost** — be honest about what is lost (e.g., "Contexts are no longer independently deployable", "Domain layer has infrastructure awareness")
- **Pragmatic Benefit** — explain why it's worth it (e.g., "Eliminates data synchronization complexity for immutable reference data", "Reduces 3 files to 1 for a context with a single entity")
- **Mitigations** — describe guardrails (e.g., "Type alias in consumer context, not direct import", "Lint rule prevents further cross-context imports")

Include this section only for Purity Divergence classifications or any other decision that bends a DDD/hexagonal rule. Remove it entirely for purity-neutral decisions.

---

## Entry Point

### Actions

1. Check `$ARGUMENTS` for a sub-command (`new`, `show`, `seed`, `supersede`)
2. Determine ADR location:
   - Look for `ddd-workspace/` in the project root
   - If found → `ddd-workspace/adr/`
   - If not found → `docs/adr/`
3. If ADR directory does not exist:
   - For `new`, `seed`, or `supersede` → create it
   - For dashboard or `show` → show the [No ADRs](#error-no-adrs) error
4. Route to the appropriate sub-command (or default dashboard)

---

## Command: Dashboard (default)

When invoked without arguments, show all ADRs and surface unrecorded decisions from the pipeline.

### Actions

1. Scan ADR directory for `*.md` files
2. For each file, extract: number, title, status, classification, affected contexts, date
3. If `ddd-workspace/ddd-model.manifest.json` exists, read its `decisions[]` array and identify entries that have no matching ADR (by title similarity)
4. If FQBC files exist, read Section 9 Design Decisions tables and identify rows without matching ADRs

### Output

```markdown
## Architecture Decision Records

**Project**: [project name]
**ADR Location**: [ddd-workspace/adr/ | docs/adr/]
**Total ADRs**: [count]

### Active Decisions

| # | Title | Classification | Contexts | Date | Status |
|---|-------|---------------|----------|------|--------|
| [NNNN] | [title] | [classification] | [contexts] | [date] | [status] |

### By Classification

| Classification | Count | ADRs |
|----------------|-------|------|
| Purity Divergence | [N] | #NNNN, #NNNN |
| Boundary | [N] | #NNNN |
| Integration | [N] | #NNNN |
| Pattern | [N] | #NNNN |
| Infrastructure | [N] | #NNNN |

### Unrecorded Decisions

Decisions found in pipeline artifacts without a formal ADR:

| Source | Decision | Suggestion |
|--------|----------|------------|
| manifest.decisions | [decision text] | `/ddd-adr new "[title]"` |
| FQBC [context] Section 9 | [decision text] | `/ddd-adr new "[title]"` |

_Run `/ddd-adr seed` to generate drafts for unrecorded decisions._

### Quick Commands

- `/ddd-adr new [title]` — record a new decision
- `/ddd-adr show [number]` — view a specific ADR
- `/ddd-adr seed` — generate ADR drafts from pipeline artifacts
```

---

## Command: New

**Usage**: `/ddd-adr new [title]`

Create a new ADR interactively.

### Actions

1. If no title provided, ask the user for one
2. Determine the next ADR number by scanning existing files for the highest `NNNN` prefix
3. Detect available pipeline context:
   - Read `ddd-model.manifest.json` for context names (if exists)
   - Check FQBC files for context relationship data
4. Ask the user for:
   - **Classification** — present the five options with descriptions
   - **Affected contexts** — if contexts are known from the manifest, offer them as choices
   - **Context** (the problem/motivation) — what drove this decision
   - **Decision** — what was decided
   - **Purity Impact** — if classification is "Purity Divergence" or the user indicates a deviation, fill in the four Purity Impact fields
   - **Consequences** — positive and negative
   - **Pipeline references** — if workspace exists, help link to PRD IDs, FQBC sections
5. Generate the ADR file from the template
6. Present the draft for user review
7. Write the file to `[adr-location]/NNNN-kebab-case-title.md`
8. Confirm creation

### Output

After writing, confirm:

```markdown
## ADR Created

**File**: [adr-location]/NNNN-kebab-case-title.md
**Classification**: [type]
**Affected Contexts**: [contexts]
**Status**: Accepted

View it with `/ddd-adr show NNNN`.
```

---

## Command: Show

**Usage**: `/ddd-adr show [number]`

Display a specific ADR with context.

### Actions

1. Look up the ADR file matching the number (`NNNN-*.md`)
2. If not found, show the [ADR Not Found](#error-adr-not-found) error
3. Read and display the full content
4. If the ADR has status `Superseded by [NNNN]`, also show the successor ADR summary
5. Search for related ADRs — same classification or overlapping affected contexts — and list them

### Output

```markdown
## ADR NNNN: [Title]

[Full ADR content]

---

### Related ADRs

| # | Title | Relationship |
|---|-------|-------------|
| [NNNN] | [title] | Same classification: [type] |
| [NNNN] | [title] | Shared context: [context name] |
```

---

## Command: Seed

**Usage**: `/ddd-adr seed`

Generate ADR drafts from pipeline artifacts and eval findings. This is the key integration point — it bridges ephemeral findings into durable records.

### Actions

1. Check available data sources:
   - `ddd-workspace/ddd-model.manifest.json` → `decisions[]` array
   - `ddd-workspace/fqbc/*.md` → Section 9 Design Decisions tables
   - Eval synthesis → divergences (pragmatic high / purity low, and vice versa)
2. If no data sources exist, show the [No Pipeline Data](#error-no-pipeline-data) error
3. Scan existing ADR files to avoid duplicates (match by title similarity)
4. Extract candidates from each source:
   - **From manifest decisions**: Each `decisions[]` entry without a matching ADR
   - **From FQBC Section 9**: Each Design Decisions row without a matching ADR
   - **From eval divergences**: Each "Pragmatic high, Purity low" finding → Purity Divergence candidate. Each "Purity high, Pragmatic low" finding → candidate for simplification ADR
5. Present candidates to the user grouped by source

### Candidate Presentation

```markdown
## ADR Seed Candidates

Found [N] decisions without formal ADRs:

### From Model Manifest

| # | Decision | Phase | Date |
|---|----------|-------|------|
| 1 | [decision text] | [phase] | [timestamp] |

### From FQBC Design Decisions

| # | Context | Decision | Rationale |
|---|---------|----------|-----------|
| 2 | [context] | [decision] | [rationale] |

### From Eval Divergences

| # | Finding | Lens Gap | Suggested Classification |
|---|---------|----------|------------------------|
| 3 | [finding] | Pragmatic > Purity | Purity Divergence |
| 4 | [finding] | Purity > Pragmatic | Pattern |

**Which candidates should I create ADR drafts for?** (e.g., "1, 3" or "all")
```

### After User Selection

For each selected candidate:

1. Generate an ADR draft pre-populated from the source data
   - Title derived from the decision text
   - Classification inferred from the source (manifest decisions → Boundary; FQBC → varies; eval divergences → Purity Divergence or Pattern)
   - Context section filled from available rationale
   - Pipeline References pre-populated with the source artifact
   - Purity Impact section included for Purity Divergence classifications
2. Present each draft for user review and editing
3. Write approved drafts to files
4. Summarize what was created

### Output

```markdown
## ADRs Seeded

Created [N] ADR(s):

| # | Title | Classification | Source |
|---|-------|---------------|--------|
| [NNNN] | [title] | [type] | [manifest / FQBC / eval] |

View with `/ddd-adr show [number]` or list all with `/ddd-adr`.
```

---

## Command: Supersede

**Usage**: `/ddd-adr supersede [number]`

Create a new ADR that supersedes an existing one. Used when a previous decision is being revised.

### Actions

1. Read the existing ADR by number
2. If not found, show the [ADR Not Found](#error-adr-not-found) error
3. Determine the next ADR number
4. Create a new ADR draft pre-populated with:
   - Context section from the original, plus "This supersedes ADR NNNN because [user explains why]"
   - Same classification and affected contexts as the original (user can change)
   - Pipeline References from the original
5. Guide the user through:
   - Why is the original decision being revised?
   - What is the new decision?
   - Updated consequences
6. Write the new ADR file
7. Update the original ADR's status line from `Accepted` to `Superseded by [new-number]`
8. Confirm both changes

### Output

```markdown
## ADR Superseded

**Original**: NNNN — [original title] → Status: Superseded by [new-number]
**New**: [new-number] — [new title] → Status: Accepted

The original ADR has been updated to reference its successor.
```

---

## Error Handling

### Error: No ADRs

When the ADR directory does not exist and the command is read-only (dashboard or show):

```markdown
## No Architecture Decision Records Found

No ADR directory found at `[expected-location]`.

**To start recording decisions:**
- `/ddd-adr new [title]` — create your first ADR
- `/ddd-adr seed` — generate ADR drafts from pipeline artifacts

Architecture Decision Records capture the *why* behind significant design choices,
especially deliberate divergences from DDD purity.
```

### Error: ADR Not Found

When `show` or `supersede` references a number that doesn't exist:

```markdown
## ADR [number] Not Found

No ADR file matching number [number] found in `[adr-location]`.

**Available ADRs**: [list numbers and titles, or "none"]

Use `/ddd-adr` to see the full dashboard.
```

### Error: No Pipeline Data

When `seed` is run but no manifest, FQBCs, or eval output exist:

```markdown
## No Pipeline Data for Seeding

Could not find any pipeline artifacts to seed ADRs from:

- No `ddd-model.manifest.json` (model decisions)
- No FQBC files (design decisions)
- No eval report (divergences)

**Options:**
- `/ddd-adr new [title]` — create an ADR manually
- `/ddd-model` — run the modeling pipeline first
- `/ddd-eval` — run the evaluation to surface divergences
```
