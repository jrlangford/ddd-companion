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

A lean PRD for PoC development consists of these sections:

| # | Section | Purpose |
|---|---------|---------|
| 1 | Executive Summary | Quick overview of project and scope |
| 2 | Background & Context | Why this project exists |
| 3 | PoC Scope | What's included and excluded |
| 4 | Functional Areas | Cohesive feature groupings (context candidates) |
| 5 | Functional Requirements | Detailed specs by area |
| 6 | Domain Glossary | Term definitions (Ubiquitous Language) |
| 7 | Business Rules Catalog | Explicit policies and constraints |
| 8 | Conceptual Entity Map | Things and relationships |
| 9 | Integration Touchpoints | External interactions |
| 10 | Role-Capability Matrix | Who can do what |
| 11 | Non-Functional Requirements | Quality attributes |
| 12 | Success Criteria | How we know it works |
| 13 | Product Team Expectations | Technical context (not specs) |
| 14 | Traceability Index | Requirement IDs for FQBC citation |

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
2. Check for required sections (see [schema.md](schema.md))
3. Validate content quality:
   - Business rules are in catalog (not embedded in acceptance criteria)
   - Domain terms are defined in glossary
   - Entities have descriptions and relationships
   - Traceability IDs are assigned and consistent
   - Functional areas have cohesion rationale
4. Report findings with severity levels

### Output

```markdown
## PRD Validation: [filename]

### Section Compliance

| Section | Status | Notes |
|---------|--------|-------|
| Executive Summary | ✓ | — |
| Background & Context | ✓ | — |
| PoC Scope | ✓ | — |
| Functional Areas | ⚠ | Missing cohesion rationale for Area 2 |
| Functional Requirements | ✓ | — |
| Domain Glossary | ⚠ | 3 terms used but not defined |
| Business Rules Catalog | ✗ | Missing — rules embedded in acceptance criteria |
| Conceptual Entity Map | ✓ | — |
| Integration Touchpoints | ✓ | — |
| Role-Capability Matrix | ✗ | Missing |
| Non-Functional Requirements | ✓ | — |
| Success Criteria | ✓ | — |
| Product Team Expectations | ✓ | — |
| Traceability Index | ⚠ | Incomplete — missing BR-* entries |

### Issues

| Severity | Count | Examples |
|----------|-------|----------|
| High | 2 | Missing Business Rules Catalog, Missing Role-Capability Matrix |
| Medium | 3 | Undefined terms: "threshold", "workflow", "escalation" |
| Low | 1 | Area 2 missing cohesion rationale |

### Validation Result: **6 issues found**

Use `/ddd-prd edit [file]` to fix these issues interactively.
```

---

## Command: Template

**Usage**: `/ddd-prd template [project-name]`

Generate an empty PRD template with all required sections.

### Actions

1. Generate a complete PRD template following [schema.md](schema.md)
2. Include placeholder text and guidance comments
3. Write to `ddd-workspace/prd-[project-name]-poc.md`
4. If no project name provided, ask for one

### Output Template

Generate the following structure (see [output-formats.md](output-formats.md) for formatting details):

```markdown
# Product Requirements Document
## [Project Name] — PoC

**Version**: 0.1 (Draft)
**Date**: [Current Date]
**Status**: Template

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Background & Context](#2-background--context)
3. [PoC Scope](#3-poc-scope)
4. [Functional Areas](#4-functional-areas)
5. [Functional Requirements](#5-functional-requirements)
6. [Domain Glossary](#6-domain-glossary)
7. [Business Rules Catalog](#7-business-rules-catalog)
8. [Conceptual Entity Map](#8-conceptual-entity-map)
9. [Integration Touchpoints](#9-integration-touchpoints)
10. [Role-Capability Matrix](#10-role-capability-matrix)
11. [Non-Functional Requirements](#11-non-functional-requirements)
12. [Success Criteria](#12-success-criteria)
13. [Product Team Expectations](#13-product-team-expectations)
14. [Traceability Index](#14-traceability-index)

---

## 1. Executive Summary

<!--
Briefly describe:
- What this project is
- What the PoC will validate
- Key functional areas
-->

This PRD defines the scope for a lean PoC of [Project Name], focusing on [scope].
The PoC will validate [hypothesis] before expanding to [future scope].

**Objective**: [One sentence goal]

**Functional Areas**: [N] areas identified as potential Bounded Context boundaries.

---

## 2. Background & Context

<!--
Explain:
- Why this project exists
- Current state problems
- Business drivers
-->

[Background content]

---

## 3. PoC Scope

### 3.1 In Scope

<!--
List capabilities included in PoC with brief rationale.
See poc-scoping.md for inclusion criteria.
-->

- [Capability 1]: [Why included]
- [Capability 2]: [Why included]

### 3.2 Out of Scope

| Feature | Reason | Mitigation |
|---------|--------|------------|
| [Feature] | [Why deferred] | [How PoC handles absence] |

---

## 4. Functional Areas

<!--
Group features by cohesion (shared terminology, entities, rules).
These are candidates for Bounded Contexts.
See ddd-alignment.md for grouping guidance.
-->

### 4.1 [Area Name]

**Cohesion Rationale**: [Why these features belong together]
**Key Terms**: [Domain terms specific to this area]
**Key Entities**: [Entities owned by this area]
**Stakeholder**: [Primary business owner]

| ID | Feature | Description |
|----|---------|-------------|
| FR-[area]-01 | [Name] | [Brief description] |

---

## 5. Functional Requirements

### 5.1 [Area Name]

#### FR-[area]-01: [Feature Name]

**User Story**: As a [role], I want to [action], so that [benefit].

**Acceptance Criteria**:
- [ ] [Criterion 1]
- [ ] [Criterion 2]

**Business Rules**: BR-01, BR-02

**Conceptual Entities**: [Entity references]

**Role-Capability**: [Role] can [capability]

---

## 6. Domain Glossary

<!--
Define domain terms with specific meanings.
These become Ubiquitous Language in FQBC.
-->

| Term | Definition | Area | Notes |
|------|------------|------|-------|
| [Term] | [Domain-specific meaning] | [Area] | [Variants] |

---

## 7. Business Rules Catalog

<!--
Explicit policies and constraints.
Categorize as: Invariant, Precondition, Postcondition, Derivation.
See ddd-alignment.md for guidance.
-->

| ID | Rule | Type | Entities | Area |
|----|------|------|----------|------|
| BR-01 | [Rule statement] | [Type] | [Entities] | [Area] |

---

## 8. Conceptual Entity Map

<!--
What things exist in the domain (not technical data models).
Include identity, attributes, relationships, lifecycle.
-->

| Entity | Description | Key Attributes | Relationships | Area |
|--------|-------------|----------------|---------------|------|
| [Entity] | [What it represents] | [Attributes] | [Related entities] | [Area] |

---

## 9. Integration Touchpoints

<!--
Where functional areas or external systems interact.
These inform Context Mapping in technical design.
-->

| From | To | Trigger | Data Flow | Timing |
|------|-----|---------|-----------|--------|
| [Area] | [Area/System] | [Event] | [Data] | Sync/Async |

---

## 10. Role-Capability Matrix

| Role | Area | Capabilities | Restrictions |
|------|------|--------------|--------------|
| [Role] | [Area] | [What they can do] | [Limitations] |

---

## 11. Non-Functional Requirements

| Category | Requirement | Priority |
|----------|-------------|----------|
| Performance | [Requirement] | P1/P2/P3 |
| Security | [Requirement] | P1/P2/P3 |

---

## 12. Success Criteria

The PoC is successful when:

1. [Measurable outcome]
2. [Measurable outcome]

---

## 13. Product Team Expectations

<!--
Technical concepts from source docs — context for engineering, not specs.
-->

**Assumptions**: [What product team assumed]

**Technical Concepts**: [What they envisioned]

---

## 14. Traceability Index

### Functional Requirements
| ID | Name | Area |
|----|------|------|
| FR-[area]-01 | [Name] | [Area] |

### Business Rules
| ID | Summary |
|----|---------|
| BR-01 | [Brief] |

### Conceptual Entities
| ID | Entity |
|----|--------|
| CE-01 | [Name] |
```

### Confirmation

```markdown
## Template Generated

**File**: `ddd-workspace/prd-[project-name]-poc.md`

The template includes all 14 required sections with placeholder guidance.

**Next steps**:
1. Fill in sections manually, or
2. Use `/ddd-extract-prd [source]` to populate from documentation
3. Use `/ddd-prd edit [file]` to refine iteratively
```

---

## Command: Section

**Usage**: `/ddd-prd section [section-name]`

Show the template and guidance for a specific PRD section.

### Valid Section Names

- `executive-summary`
- `background`
- `scope`
- `functional-areas`
- `requirements`
- `glossary`
- `business-rules`
- `entities`
- `touchpoints`
- `roles`
- `nfr`
- `success-criteria`
- `expectations`
- `traceability`

### Actions

1. Look up the section in [schema.md](schema.md)
2. Present the template with detailed guidance
3. Include examples where helpful
4. Reference related guidance docs ([ddd-alignment.md](ddd-alignment.md), [poc-scoping.md](poc-scoping.md))

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
> ❌ "System rejects if total > $10,000"

Should be extracted:
> ✓ BR-01: Submissions exceeding $10,000 require manager approval (Precondition)

See [ddd-alignment.md](ddd-alignment.md) for full guidance.
```

---

## Command: Edit

**Usage**: `/ddd-prd edit [file-path]`

Interactively review and refine an existing PRD document.

### Purpose

Use this command when you have an existing PRD that needs:
- Structural validation and fixes
- Content refinement or expansion
- DDD readiness review
- Addition of missing sections

### Input

Provide the path to an existing PRD file:
- Absolute path: `/path/to/prd-project-poc.md`
- Relative path: `ddd-workspace/prd-project-poc.md`

---

### Phase 1: Load & Validate

**Goal**: Understand the current state of the PRD and identify gaps.

#### Actions

1. Read the PRD from the provided path
2. Validate structure against [schema.md](schema.md)
3. Check for:
   - Missing required sections
   - Business rules embedded in acceptance criteria (should be extracted)
   - Undefined domain terms (referenced but not in glossary)
   - Entities without relationships
   - Missing traceability IDs
4. Calculate statistics

#### Present to User

```markdown
## PRD Review: [Document Name]

**Location**: [File path]
**Last Modified**: [Date if available]

### Structure Compliance

| Section | Status | Notes |
|---------|--------|-------|
| Executive Summary | ✓ Present | — |
| Background & Context | ✓ Present | — |
| PoC Scope | ✓ Present | — |
| Functional Areas | ✓ Present | — |
| Functional Requirements | ✓ Present | — |
| Domain Glossary | ⚠ Incomplete | 3 terms undefined |
| Business Rules Catalog | ✗ Missing | Rules embedded in acceptance criteria |
| Conceptual Entity Map | ✓ Present | — |
| Integration Touchpoints | ✓ Present | — |
| Role-Capability Matrix | ✗ Missing | — |
| Non-Functional Requirements | ✓ Present | — |
| Success Criteria | ✓ Present | — |
| Product Team Expectations | ✓ Present | — |
| Traceability Index | ⚠ Incomplete | Missing BR-* IDs |

### Issues Found

| Severity | Issue | Location |
|----------|-------|----------|
| High | Entity "Order" referenced but not defined | FR-02, FR-05 |
| Medium | Business rules embedded in acceptance criteria | FR-03, FR-07 |
| Medium | Term "threshold" used but not in glossary | FR-04 |
| Low | Missing cohesion rationale | Functional Area 2 |

### Statistics

- **Functional Areas**: 3
- **Functional Requirements**: 12
- **Business Rules**: 5 (+ ~3 embedded)
- **Glossary Terms**: 8 defined, 3 undefined
- **Entities**: 6
- **Integration Touchpoints**: 4

---

**What would you like to do?**

1. **Fix structural issues** — Extract embedded rules, define missing terms, add missing sections
2. **Refine a specific section** — Deep dive into one area
3. **Add new content** — Add requirements, rules, or entities
4. **DDD readiness review** — Evaluate for Bounded Context work
```

Wait for user selection.

---

### Phase 2: Guided Editing

Based on user selection, provide targeted assistance.

#### Option 1: Fix Structural Issues

For each issue found, propose a fix:

```markdown
## Proposed Fixes

### 1. Extract Embedded Business Rules

**From FR-03 Acceptance Criteria**:
> "System rejects submission if total exceeds $10,000"

**Proposed Rule**:
| ID | Rule | Type | Entities | Area |
|----|------|------|----------|------|
| BR-06 | Submissions with total exceeding $10,000 must be rejected | Precondition | Submission | Approval |

**Updated Acceptance Criterion**:
- [ ] System enforces BR-06 (submission total limit)

---

### 2. Define Missing Glossary Terms

| Term | Proposed Definition | Area |
|------|---------------------|------|
| Threshold | A configurable limit value that triggers system behavior when exceeded | Monitoring |

---

### 3. Add Missing Entity

**Entity**: Order
**Description**: [Need input — what does Order represent in this domain?]
**Proposed Attributes**: [Based on usage in FR-02, FR-05]
**Relationships**: [To be determined]

**Please provide a definition for "Order" or confirm the proposed attributes.**

---

**Apply these fixes?** (I'll show you the changes before writing)
```

#### Option 2: Refine Specific Section

Ask which section, then:

```markdown
## Section Review: [Section Name]

### Current Content
[Show current section content]

### Suggestions
1. [Specific improvement suggestion]
2. [Specific improvement suggestion]

### Questions
- [Clarifying question about ambiguous content]

**What changes would you like to make?**
```

#### Option 3: Add New Content

```markdown
## Add New Content

**What would you like to add?**

1. **New Functional Requirement** — I'll guide you through the template
2. **New Business Rule** — Define a policy or constraint
3. **New Entity** — Add to the conceptual model
4. **New Glossary Term** — Define domain terminology
5. **New Integration Touchpoint** — Document an external interaction

[Based on selection, present appropriate template and guide completion]
```

#### Option 4: DDD Readiness Review

Evaluate the PRD for downstream Bounded Context work:

```markdown
## DDD Readiness Assessment

### Functional Area Cohesion

| Area | Cohesion Score | Assessment |
|------|----------------|------------|
| [Area 1] | Strong | Clear terminology, shared entities, well-defined rules |
| [Area 2] | Weak | Mixed terminology, entities shared with Area 3 |
| [Area 3] | Moderate | Good rule isolation, but lifecycle unclear |

### Terminology Consistency

| Term | Usage Consistency | Issue |
|------|-------------------|-------|
| Customer | ⚠ Inconsistent | Different meaning in Area 1 vs Area 2 — potential context boundary |
| Order | ✓ Consistent | Same meaning across all areas |

### Context Boundary Signals

**Strong Boundaries Detected**:
- Area 1 ↔ Area 2: Different terminology for same concepts suggests natural split

**Weak Boundaries**:
- Area 2 ↔ Area 3: Heavy entity sharing, may be single context

### Recommendations

1. **Clarify "Customer" terminology** — Consider splitting into "Sales Customer" and "Support Customer" or document that these are the same
2. **Review Area 2/3 boundary** — May benefit from merging or clearer interface definition
3. **Add lifecycle diagrams** — [Entity] state transitions are unclear

### Readiness Score: 7/10

**Ready for Bounded Context Review with minor improvements.**
```

---

### Phase 3: Apply Changes

**Goal**: Make approved changes to the PRD document.

#### Actions

1. Compile all approved changes from Phase 2
2. Present unified diff showing all modifications
3. Wait for user approval
4. Write updated PRD to the same location (or new location if specified)

#### Present to User

```markdown
## Proposed Changes Summary

### Additions
- Business Rules Catalog section (new)
- 3 business rules extracted from acceptance criteria
- 2 glossary terms defined
- 1 entity added to Conceptual Entity Map

### Modifications
- FR-03: Updated acceptance criteria to reference BR-06
- FR-07: Updated acceptance criteria to reference BR-07
- Traceability Index: Added BR-06, BR-07, BR-08

### Files
- **Updated**: ddd-workspace/prd-project-poc.md

**Apply these changes?**
```

After approval, write the file and confirm:

```markdown
## Changes Applied

Updated: `ddd-workspace/prd-project-poc.md`

### Summary
- Added Business Rules Catalog with 3 rules
- Defined 2 glossary terms
- Added Order entity
- Updated 2 functional requirements
- Updated Traceability Index

**PRD is now compliant with schema. Ready for Bounded Context Review.**
```

---

### Edit Interaction Modes

#### Interactive (Default)

Step-by-step review with approval at each change. Best for:
- First-time PRD refinement
- Complex structural issues
- When user wants to understand each change

#### Batch Mode

User can specify multiple changes upfront:

```
/ddd-prd edit ddd-workspace/prd-project-poc.md --batch "extract embedded rules, define missing terms, add role-capability matrix"
```

Process all requested changes, then present unified review before applying.

---

### Edit Error Handling

#### File Not Found
- Verify the path with the user
- Suggest checking `ddd-workspace/` directory
- Offer to list available PRD files

#### Invalid PRD Format
- If file exists but isn't recognizable as a PRD, inform user
- Offer to analyze structure and suggest how to proceed
- May need extraction from source instead (`/ddd-extract-prd`)

#### Conflicting Edits
- If user has made changes since loading, warn before overwriting
- Offer to reload and re-apply changes
- Consider creating backup before writing

---

## Reference Documents

This skill includes these reference documents:

| Document | Purpose |
|----------|---------|
| [schema.md](schema.md) | Complete PRD structure and section templates |
| [ddd-alignment.md](ddd-alignment.md) | Guidance for extracting DDD artifacts |
| [output-formats.md](output-formats.md) | Markdown and Mermaid formatting |
| [poc-scoping.md](poc-scoping.md) | Criteria for PoC feature selection |

Related skills:
- `/ddd-extract-prd` — extract PRD from source documentation (Notion, HTML, Markdown)
