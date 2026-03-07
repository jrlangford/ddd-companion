---
name: ddd-prd
description: PRD schema, validation, and templates for DDD workflow
argument-hint: "[command] [file]"
---

# PRD Schema & Utilities

This skill defines the PRD schema used across the DDD workflow and provides utilities for working with PRD documents.

## Commands

| Command | Description |
|---------|-------------|
| `/ddd-prd` | Show PRD structure overview |
| `/ddd-prd validate [file]` | Validate a PRD against the schema |
| `/ddd-prd template [name]` | Generate an empty PRD template |
| `/ddd-prd section [name]` | Show template for a specific section |
| `/ddd-prd edit [file]` | Interactively refine an existing PRD |

---

## Command: Overview (default)

When invoked without arguments, display the PRD structure summary.

### Actions

1. Present the PRD section overview from [schema.md](schema.md)
2. Explain the purpose and DDD pipeline context
3. Offer next steps (validate existing, generate template, or use extract skill)

### Output

```markdown
## PRD Schema Overview

A lean PRD consists of these sections:

| # | Section | Purpose |
|---|---------|---------|
| 1 | Executive Summary | Quick overview of project and scope |
| 2 | Background & Context | Why this project exists |
| 3 | Scope | What's included and excluded |
| 4 | Functional Areas | Cohesive feature groupings (context candidates) |
| 5 | Functional Requirements | Detailed specs by area |
| 6 | Domain Glossary | Candidate terms for Ubiquitous Language |
| 7 | Business Rules Catalog | Explicit policies and constraints |
| 8 | Conceptual Entity Map | Things and relationships |
| 9 | Integration Touchpoints | External interactions |
| 10 | Role-Capability Matrix | Who can do what |
| 11 | Authorization Pattern *(optional)* | How authz decisions are made |
| 12 | API Design Principles *(optional)* | HTTP API conventions |
| 13 | Non-Functional Requirements | Quality attributes |
| 14 | Success Criteria | How we know it works |
| 15 | Product Team Expectations | Technical context (not specs) |
| 16 | Traceability Index | Requirement IDs for FQBC citation |
| 17 | Appendix | References, links, supplementary material |

### Pipeline Context

```
PRD → Bounded Context Review → FQBC Documents → Implementation
```

The PRD defines **what to build**. It seeds downstream DDD work by capturing:
- Domain terminology → Ubiquitous Language
- Business rules → Domain invariants
- Functional areas → Bounded Context candidates
- Conceptual entities → Domain model seeds

### Next Steps

- **Have source docs?** Use `/ddd-extract-prd [source]` to extract a PRD
- **Have an existing PRD?** Use `/ddd-prd validate [file]` to check it
- **Need to refine a PRD?** Use `/ddd-prd edit [file]` to improve it
- **Starting fresh?** Use `/ddd-prd template [name]` to generate a blank PRD
```

---

## Command: Validate

**Usage**: `/ddd-prd validate [file-path]`

Validate an existing PRD document against the schema.

### Actions

1. Read the PRD file from the provided path
2. Apply the validation checklist from [schema.md](schema.md#validation-checklist) as the baseline for structural checks
3. Check for required sections (see [schema.md](schema.md))
4. Validate content quality:
   - Business rules are in catalog (not embedded in acceptance criteria)
   - Domain terms are defined in glossary
   - Entities have descriptions and relationships
   - Traceability IDs are assigned and consistent
   - Functional areas have cohesion rationale
5. Report findings with severity levels

### Output

```markdown
## PRD Validation: [filename]

**Status symbols**: `pass` = present and complete | `warn` = present but has issues | `fail` = missing or invalid | `skip` = optional, not included

### Section Compliance

| Section | Status | Notes |
|---------|--------|-------|
| 1. Executive Summary | [status] | [notes] |
| ... | ... | ... |

### Issues

| Severity | Count | Examples |
|----------|-------|----------|
| High | N | [examples] |
| Medium | N | [examples] |
| Low | N | [examples] |

### Validation Result: **N issues found**

Use `/ddd-prd edit [file]` to fix these issues interactively.
```

---

## Command: Template

**Usage**: `/ddd-prd template [project-name]`

Generate an empty PRD template with all required sections.

### Actions

1. Generate a complete PRD template following [schema.md](schema.md)
2. Include placeholder text and guidance comments
3. Write to `ddd-workspace/prd/prd-[project-name]-[scope].md`
4. If no project name provided, ask for one

**Reference**: See `prd-template.md` for the full template content and post-generation guidance.

---

## Command: Section

**Usage**: `/ddd-prd section [section-name]`

Show the template and guidance for a specific PRD section.

### Valid Section Names

`executive-summary`, `background`, `scope`, `functional-areas`, `requirements`, `glossary`, `business-rules`, `entities`, `touchpoints`, `roles`, `nfr`, `success-criteria`, `expectations`, `traceability`, `authorization` *(optional)*, `api` *(optional)*, `appendix`

### Actions

1. Look up the section in [schema.md](schema.md)
2. Present the template with detailed guidance
3. Include examples where helpful
4. Reference related guidance docs ([ddd-alignment.md](ddd-alignment.md), [scoping-criteria.md](scoping-criteria.md))

### Example Output (for `business-rules`)

```markdown
## Section: Business Rules Catalog

### Purpose
Capture explicit policies and constraints that govern the domain. Business rules are first-class artifacts that must be respected by any implementation.

### Template

| ID | Rule | Type | Entities | Area |
|----|------|------|----------|------|
| BR-01 | [Clear, testable statement] | [Type] | [Governed entities] | [Area] |

### Rule Types

| Type | Description | Example |
|------|-------------|---------|
| Invariant | Must always be true | "An order must have at least one line item" |
| Precondition | Must be true before action | "Only managers can approve expenses over $1000" |
| Postcondition | Must be true after action | "Approval must generate audit entry" |
| Derivation | How values are calculated | "Total = sum of items - discounts + tax" |

### What IS a Business Rule
- Explicit domain policy
- Testable constraint
- Independent of UI/implementation

### What is NOT a Business Rule
- UI validation (implementation detail)
- Acceptance criteria (verifies behavior, doesn't define policy)
- Database constraints (technical design)

### Common Mistake
Rules embedded in acceptance criteria:
> Bad: "System rejects if total > $10,000"

Should be extracted:
> Good: BR-01: Submissions exceeding $10,000 require manager approval (Precondition)

See [ddd-alignment.md](ddd-alignment.md) for full guidance.
```

---

## Command: Edit

**Usage**: `/ddd-prd edit [file-path]`

Interactively review and refine an existing PRD document through a three-phase workflow: Load & Validate → Guided Editing → Apply Changes.

**Reference**: See `edit-workflow.md` for the complete phase-by-phase workflow, output templates, interaction modes, and error handling.

**Quick summary**:
1. **Phase 1**: Load PRD, validate against schema, present compliance report with issues and statistics
2. **Phase 2**: Based on user choice — fix structural issues, refine a section, add new content, or run DDD readiness review
3. **Phase 3**: Compile approved changes, present summary, write updated PRD after approval

Supports interactive (step-by-step) and batch modes.

---

## Reference Documents

This skill includes these reference documents:

| Document | Purpose |
|----------|---------|
| [schema.md](schema.md) | Complete PRD structure and section templates |
| [ddd-alignment.md](ddd-alignment.md) | Guidance for extracting DDD artifacts |
| [output-formats.md](output-formats.md) | Markdown and Mermaid formatting |
| [scoping-criteria.md](scoping-criteria.md) | Criteria for minimum viable scope feature selection |
| [prd-template.md](prd-template.md) | Full PRD template for `/ddd-prd template` |
| [edit-workflow.md](edit-workflow.md) | Edit command phases and interaction modes |

Related skills:
- `/ddd-extract-prd` — extract PRD from source documentation (Notion, HTML, Markdown)
