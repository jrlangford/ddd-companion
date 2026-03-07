# User Review Protocol

**Important Goal**: The BCR process should help the user develop a deep understanding of what will be built. Each phase produces artifacts that shape the final system — user review ensures alignment before proceeding.

## Response Templates

### Resuming Work

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
  - [ ] Fulfillment <- **Next**
- [ ] Phase 4: Coherence Review

**Ready to generate FQBC for Fulfillment?**
```

### New Workflow

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

**Tip**: Run `/ddd-prd validate [file]` before starting to catch structural issues early.

Once I have the PRD, I'll check for authorization patterns and initialize the workspace.
```

### Authorization Pattern Confirmation

> **Note**: If the PRD specifies an authorization pattern other than Permissions Object Pattern,
> inform the user that this is the only pattern currently supported by the implementation pipeline
> (`/ddd-implement`). Ask whether to proceed with Permissions Object Pattern or pause for discussion.

If the PRD does not explicitly mention authorization, inform the user:

```markdown
## Authorization Pattern

The PRD doesn't specify how authorization will be handled across bounded contexts.

This pipeline uses the **Permissions Object Pattern** for all generated contexts:

- Each service owns its role definitions — roles are not centralized
- Service middleware builds a Permissions object from authenticated identity (JWT claims)
- Handlers receive the object — they don't query roles or external services
- Authorization checks via `permissions.hasAnyRole('Admin', 'Manager')`
- Keeps domain logic clean; authorization is a cross-cutting concern

This pattern will be applied to all bounded contexts. Proceeding with this approach.
```

---

## Phase Review Summaries

### After Phase 1: Context Discovery

Present a summary and **ask the user to review** before proceeding:

```markdown
**Phase 1 Complete: Context Discovery**

I've identified [N] candidate bounded contexts:
- [Context A] — [brief rationale]
- [Context B] — [brief rationale]
- ...

Full details written to `bcr/context-discovery.md`.

**Please review the context boundaries before we proceed.**

Questions to consider:
- Do these boundaries match your mental model of the domain?
- Are any contexts too broad (doing too much) or too narrow (artificial splits)?
- Are the rationales for each context clear and convincing?

Ready to proceed to Phase 2: Context Mapping?
```

### After Phase 2: Context Mapping

Present the context map and **ask the user to review** relationships:

```markdown
**Phase 2 Complete: Context Mapping**

Context relationships defined:
- [Context A] -> [Pattern] -> [Context B]
- ...

Full details and diagram written to `bcr/context-map.md`.

**Please review the context relationships before we proceed.**

Questions to consider:
- Do upstream/downstream relationships feel correct?
- Are integration patterns appropriate? (Default to ACL over Shared Kernel — see context-mapping-patterns.md for criteria)
- Will these relationships scale as the system grows?

Ready to proceed to Phase 3: FQBC Generation?
```

### After Each FQBC (Phase 3)

**Critical**: FQBC API bindings require careful user review. Present a summary and **explicitly ask the user to validate**:

```markdown
**[Context] FQBC Complete** ([N]/[Total])

**API Bindings for [Context]:**
| Operation | Method | Path |
|-----------|--------|------|
| [Op1] | POST | `/api/[context]/v1/[resource]` |
| [Op2] | GET | `/api/[context]/v1/[resource]` |
| ... | ... | ... |

Full specification written to `fqbc/[context-name].md`.

**Please review before proceeding — especially the API bindings:**

1. **Path Alignment**: Do the paths follow your API standards and conventions?
2. **Redundancy Check**: Could any endpoints be consolidated with other contexts?
3. **Functionality Clarity**: Does each endpoint have a clear, single purpose?

[If inconsistencies detected, list them here]

Ready to generate FQBC for **[next context]**? Or would you like to adjust this specification first?
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

Continue, or pause here — good stopping point.
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

## Resuming a Session

When re-invoking `/ddd-model` in a new chat:

1. Read `ddd-workspace/ddd-model.manifest.json`
2. Report current progress (see "Resuming Work" template above)
3. Identify the next incomplete item and offer to continue

The manifest preserves all state — no need to re-read previously processed contexts.
