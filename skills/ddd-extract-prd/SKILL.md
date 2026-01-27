---
name: ddd-extract-prd
description: Extract a lean PRD from source documentation (Notion, HTML, Markdown) for PoC development
argument-hint: "[source-url-or-path]"
---

# PRD Extraction

Extract a lean PRD from project documentation. The extracted PRD follows the schema defined in the [ddd-prd](../ddd-prd/SKILL.md) skill and is structured to inform downstream Bounded Context Review and Domain-Driven Design work.

For PRD structure reference, validation, editing, or templates, use `/ddd-prd`.

## Supported Sources

| Source Type | Input Format | Method |
|-------------|--------------|--------|
| **Notion** | `notion.so` URL | `Notion:notion-fetch` |
| **HTML URL** | `https://...` (non-Notion) | `WebFetch` |
| **Local HTML** | `.html`, `.htm` file path | `Read` |
| **Markdown** | `.md` file path | `Read` |

## Output

- **Format**: Markdown optimized for Obsidian (see [../ddd-prd/output-formats.md](../ddd-prd/output-formats.md))
- **Location**: `ddd-workspace/prd-[project-name]-[scope].md` in the current project
- **Schema**: Follows [../ddd-prd/schema.md](../ddd-prd/schema.md)

## Core Principles

1. **Human-in-the-loop**: Present findings at each phase; wait for user confirmation before proceeding
2. **Minimum viable scope**: Identify the smallest feature set that validates the core hypothesis
3. **Source as guideline, not gospel**: Technical details in source docs are context, not specifications
4. **Output drives design**: The PRD defines what to build; technical design flows from requirements
5. **DDD-ready artifacts**: Extract domain terminology, business rules, and functional cohesion to seed Bounded Context work

---

## Phase 1: Discovery

**Goal**: Understand the project's purpose, goals, and structure.

### Source Detection

Determine the source type from $ARGUMENTS:

1. **Notion**: URL contains `notion.so` → Use `Notion:notion-fetch`
2. **HTML URL**: URL starts with `http://` or `https://` (non-Notion) → Use `WebFetch`
3. **Local HTML**: Path ends with `.html` or `.htm` → Use `Read`
4. **Markdown**: Path ends with `.md` → Use `Read`

If the source type cannot be determined, ask the user to clarify.

### Actions

1. Fetch the source document using the appropriate method:
   - **Notion**: `Notion:notion-fetch` with the URL, then identify and fetch related databases and linked pages
   - **HTML**: `WebFetch` for URLs or `Read` for local files
   - **Markdown**: `Read` the file directly

2. Extract:
   - Project name and ID (if available)
   - High-level goals and objectives
   - Key stakeholders/roles
   - Linked resources (databases, pages, sections)
   - Initial domain terminology (significant nouns and verbs)

### Present to User

```markdown
## Project Discovery Summary

**Source**: [Source type and location]
**Project**: [Name] (ID: [ID if available])
**Status**: [Current status if mentioned]

### Goals
[List the primary goals from the source]

### Key Entities Identified
- [Section/Database 1]: [count if applicable] items — [brief description]
- [Section/Database 2]: [count if applicable] items — [brief description]

### Stakeholders/Roles
- [Role 1]: [responsibility]
- [Role 2]: [responsibility]

### Initial Domain Terms
[List significant nouns/concepts that appear frequently]

**Shall I proceed to identify PoC scope?**
```

Wait for user confirmation before Phase 2.

---

## Phase 2: Scope Definition

**Goal**: Identify the minimum feature set and functional areas for a valid PoC.

### Actions

1. Extract user stories or requirements from the source
2. Identify priority indicators (Priority field, Phase field, Status)
3. Apply PoC scoping criteria (see [../ddd-prd/poc-scoping.md](../ddd-prd/poc-scoping.md))
4. **Group features by functional cohesion** — areas that share terminology, entities, and rules
5. **Extract domain terminology** — candidate glossary terms with working definitions
6. **Surface business rules** — explicit policies and constraints (separate from acceptance criteria)

### Functional Area Grouping

Group features by cohesion, not just UI or workflow similarity. Consider:
- Shared terminology (same words mean same things)
- Shared entities (operate on same concepts)
- Shared rules (governed by same policies)
- Cohesive lifecycle (change together)

These functional areas are **candidates for Bounded Contexts** in downstream DDD work.

### Present to User

```markdown
## Proposed PoC Scope

### Functional Areas (Potential Context Boundaries)

#### 1. [Area Name]
**Cohesion**: [Why these features belong together]
**Key Terms**: [Domain terms specific to this area]

| ID | Feature | Rationale |
|----|---------|-----------|
| US-01 | [Feature name] | [Why essential for PoC] |

#### 2. [Area Name]
...

### Excluded from PoC
| Feature | Reason |
|---------|--------|
| [Feature] | [Why deferred] |

### Candidate Domain Glossary
| Term | Working Definition | Area |
|------|-------------------|------|
| [Term] | [What it means in this domain] | [Functional area] |

**Does this scope and grouping look right? Any features to add, remove, or regroup?**
```

Wait for user confirmation before Phase 3.

---

## Phase 3: Functional Requirements

**Goal**: Define detailed requirements with DDD-ready artifacts for each in-scope feature.

### Actions

1. For each scoped feature, extract:
   - User story statement (As a [role], I want [action], so that [benefit])
   - Acceptance criteria (specific, testable conditions)
   - **Business rules** (explicit policies, constraints — first-class artifacts)
   - **Conceptual entities** (what things exist and their relationships)
   - **Role-capability mapping** (who can do what)

2. Identify cross-cutting concerns:
   - Authorization rules (role-based access)
   - Audit/logging requirements
   - Error handling expectations

3. Identify integration touchpoints:
   - External systems
   - Other functional areas (potential context interactions)
   - Data flows between areas

4. Capture product team expectations:
   - Review technical details in source docs
   - Summarize as context, not specifications
   - Note assumptions and constraints

See [../ddd-prd/ddd-alignment.md](../ddd-prd/ddd-alignment.md) for extraction guidance.

### Present to User

```markdown
## Functional Requirements

### [Functional Area 1]

#### FR-01: [Feature Name]

**User Story**: As a [role], I want to [action], so that [benefit].

**Acceptance Criteria**:
- [ ] [Criterion 1]
- [ ] [Criterion 2]

**Business Rules**:
- BR-01: [Explicit policy or constraint]
- BR-02: [Explicit policy or constraint]

**Conceptual Entities**:
- [Entity]: [What it represents, key attributes]

**Role-Capability**:
- [Role] can: [capabilities]

---

### Business Rules Catalog

| ID | Rule | Area | Entities Involved |
|----|------|------|-------------------|
| BR-01 | [Rule statement] | [Area] | [Entities] |

### Conceptual Entity Map

| Entity | Description | Related Entities | Area |
|--------|-------------|------------------|------|
| [Entity] | [What it is] | [Relationships] | [Area] |

### Integration Touchpoints

| Touchpoint | Direction | Description |
|------------|-----------|-------------|
| [System/Area] | Inbound/Outbound | [What interaction occurs] |

### Cross-Cutting Requirements
- **Authorization**: [Rules by role]
- **Audit Trail**: [What to log]

### Product Team Expectations
Technical concepts from source docs (context for engineering, not specifications):
- [Concept]: [What product team envisioned]

**Are these requirements accurate and complete?**
```

Wait for user confirmation before Phase 4.

---

## Phase 4: Document Generation

**Goal**: Produce the final PRD document in Markdown format.

### Actions

1. Compile all approved content from previous phases
2. Structure according to [../ddd-prd/schema.md](../ddd-prd/schema.md)
3. Generate Markdown document with:
   - Mermaid diagrams for entity relationships and lifecycles
   - Tables for structured data (glossary, rules, touchpoints)
   - Checkbox lists for acceptance criteria
4. Create `ddd-workspace/` directory if it doesn't exist
5. Write the document to `ddd-workspace/prd-[project-name]-[scope].md`

### Output Location

```
[project-root]/
└── ddd-workspace/
    └── prd-[project-name]-[scope].md
```

---

## Error Handling

### Source Access Issues

**Notion**:
- Inform user of the specific access issue
- Ask if they can share the content directly or adjust permissions
- Offer to proceed with an HTML export or Markdown copy if available

**HTML URL**:
- If fetch fails, inform user of the error (404, timeout, etc.)
- Ask if they can provide a local copy or alternative URL
- Check if authentication is required

**Local Files**:
- If file not found, verify the path with the user
- If file is empty or unreadable, ask for an alternative

### Incomplete Source Data
- Note gaps explicitly
- Ask user to provide missing information
- Mark sections as "TBD - requires input"

### Conflicting Information
- Present both versions to user
- Ask for clarification before proceeding

---

## Example Interaction Flows

### From Notion
```
User: /ddd-extract-prd https://notion.so/project/12345

Claude: [Detects Notion source, fetches page, presents Phase 1 summary]
        "Shall I proceed to identify PoC scope?"

User: Yes, looks good.

Claude: [Groups by functional area, extracts terms, presents Phase 2]
        "Does this scope and grouping look right?"
...
```

### From HTML
```
User: /ddd-extract-prd https://docs.example.com/project-spec.html

Claude: [Detects HTML URL, fetches content, presents Phase 1 summary]
        "Shall I proceed to identify PoC scope?"
...
```

### From Markdown
```
User: /ddd-extract-prd /path/to/project-requirements.md

Claude: [Detects Markdown file, reads content, presents Phase 1 summary]
        "Shall I proceed to identify PoC scope?"
...
```
