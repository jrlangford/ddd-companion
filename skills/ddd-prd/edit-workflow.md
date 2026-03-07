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
| Executive Summary | [status] | [notes] |
| Background & Context | [status] | [notes] |
| ... | ... | ... |

### Issues Found

| Severity | Issue | Location |
|----------|-------|----------|
| High | [issue] | [where] |
| Medium | [issue] | [where] |
| Low | [issue] | [where] |

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

- **Embedded business rules**: Extract to Business Rules Catalog with proper IDs, update acceptance criteria to reference the rule
- **Missing glossary terms**: Propose definitions based on usage context
- **Missing entities**: Identify from requirement references, ask user for definitions
- **Missing sections**: Generate from existing content where possible

Present all proposed fixes, then ask: **Apply these fixes?** (show changes before writing)

### Option 2: Refine Specific Section

Ask which section, then show current content with specific improvement suggestions and clarifying questions. Wait for user direction.

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

After approval, write the file and confirm with a summary of all changes applied.

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
- **Conflicting Edits**: Warn before overwriting if file changed since loading, offer to reload
