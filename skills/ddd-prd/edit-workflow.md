# Edit Command Workflow

Workflow phases for `/ddd-prd edit [file-path]`. Interactively review and refine an existing PRD document.

## Purpose

Use this command when you have an existing PRD that needs:
- Structural validation and fixes
- Content refinement or expansion
- DDD readiness review
- Addition of missing sections

## Input

Provide the path to an existing PRD file (absolute or relative to workspace).

---

## Phase 1: Load & Validate

**Goal**: Understand the current state of the PRD and identify gaps.

### Actions

1. Read the PRD from the provided path
2. Validate structure against [schema.md](schema.md)
3. Check for:
   - Missing required sections
   - Business rules embedded in acceptance criteria (should be extracted)
   - Undefined domain terms (referenced but not in glossary)
   - Entities without relationships
   - Missing traceability IDs
4. Calculate statistics

### Present to User

```markdown
## PRD Review: [Document Name]

**Location**: [File path]
**Last Modified**: [Date if available]

### Structure Compliance

| Section | Status | Notes |
|---------|--------|-------|
| Executive Summary | ✓ Present | — |
| Background & Context | ✓ Present | — |
| Scope | ✓ Present | — |
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

- **Functional Areas**: N
- **Functional Requirements**: N
- **Business Rules**: N (+ ~N embedded)
- **Glossary Terms**: N defined, N undefined
- **Entities**: N
- **Integration Touchpoints**: N

---

**What would you like to do?**

1. **Fix structural issues** — Extract embedded rules, define missing terms, add missing sections
2. **Refine a specific section** — Deep dive into one area
3. **Add new content** — Add requirements, rules, or entities
4. **DDD readiness review** — Evaluate for Bounded Context work
```

Wait for user selection.

---

## Phase 2: Guided Editing

Based on user selection, provide targeted assistance.

### Option 1: Fix Structural Issues

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

### Option 2: Refine Specific Section

Ask which section, then present:

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

### Option 3: Add New Content

Offer guided templates for:
1. New Functional Requirement
2. New Business Rule
3. New Entity
4. New Glossary Term
5. New Integration Touchpoint

Based on selection, present appropriate template and guide completion.

### Option 4: DDD Readiness Review

Evaluate the PRD for downstream Bounded Context work:

```markdown
## DDD Readiness Assessment

### Functional Area Cohesion

| Area | Cohesion Score | Assessment |
|------|----------------|------------|
| [Area] | Strong/Moderate/Weak | [Assessment details] |

### Terminology Consistency

| Term | Usage Consistency | Issue |
|------|-------------------|-------|
| [Term] | [consistent/inconsistent] | [Details — potential context boundary signal] |

### Context Boundary Signals

**Strong Boundaries Detected**: [Areas with different terminology for same concepts]
**Weak Boundaries**: [Areas with heavy entity sharing that may be single context]

### Recommendations

1. [Specific actionable recommendation]
2. [Specific actionable recommendation]

### Readiness Score: N/10

**[Ready / Ready with minor improvements / Needs significant work] for Bounded Context Review.**
```

---

## Phase 3: Apply Changes

**Goal**: Make approved changes to the PRD document.

### Actions

1. Compile all approved changes from Phase 2
2. Present unified summary showing additions and modifications
3. Wait for user approval
4. Write updated PRD to the same location (or new location if specified)

### Present to User

```markdown
## Proposed Changes Summary

### Additions
- [List of new sections/content]

### Modifications
- [List of updated sections]

### Files
- **Updated**: [file path]

**Apply these changes?**
```

After approval, write the file and confirm:

```markdown
## Changes Applied

Updated: `ddd-workspace/prd/prd-project-mvp.md`

### Summary
- Added Business Rules Catalog with 3 rules
- Defined 2 glossary terms
- Added Order entity
- Updated 2 functional requirements
- Updated Traceability Index

**PRD is now compliant with schema. Ready for Bounded Context Review.**
```

---

## Interaction Modes

### Interactive (Default)

Step-by-step review with approval at each change. Best for first-time PRD refinement, complex structural issues, or when user wants to understand each change.

### Batch Mode

User can specify multiple changes upfront as natural language:

```
/ddd-prd edit ddd-workspace/prd/prd-project-mvp.md extract embedded rules, define missing terms, add role-capability matrix
```

Process all requested changes, then present unified review before applying.

---

## Error Handling

- **File Not Found**: Verify path with user, suggest checking `ddd-workspace/`, offer to list available PRD files
- **Invalid PRD Format**: Inform user, offer to analyze structure, suggest `/ddd-extract-prd` if needed
- **Conflicting Edits**: Warn before overwriting if file changed since loading, offer to reload. Consider creating backup before writing
