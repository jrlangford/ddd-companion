---
name: ddd-eval
description: Evaluate DDD project quality — works with or without a DDD workspace
argument-hint: "[pragmatic|purity|prd|model|impl]"
---

# DDD Project Evaluator

Evaluate a DDD project through two lenses:

- **Pragmatic** — Is the DDD delivering value? Are boundaries practical? Do abstractions pay for themselves? Is complexity justified by business needs?
- **Purity** — Is the DDD structurally correct? Do patterns follow the rules? Are layers clean? Are naming conventions consistent?

The default runs **both lenses** and returns a synthesis that highlights where pragmatism and purity agree (real strengths / real problems) and where they diverge (over-engineering vs. justified rigor).

### Data Source Modes

Detection is automatic:

- **Workspace mode** — when `ddd-workspace/` exists, leverages pipeline artifacts (PRD, FQBCs, manifests) for deep scoring with traceability
- **Codebase mode** — when no workspace exists, analyzes project source code directly by scanning for DDD patterns

All reads are non-destructive. This skill never writes or modifies project files.

**Related**: `/ddd-list` — inspect bounded contexts, domain models, and events without evaluation.

## Data Sources

| Source | Workspace Mode | Codebase Mode |
|--------|---------------|---------------|
| `ddd-workspace/prd/*.md` | PRD scoring | — |
| `ddd-workspace/ddd-model.manifest.json` | Status tracking | — |
| `ddd-workspace/fqbc/*.md` | Model scoring | — |
| `ddd-workspace/bcr/coherence-review.md` | Coherence findings | — |
| `ddd-workspace/ddd-implement.manifest.json` | Impl status | — |
| Project source code | Impl scoring | All scoring |
| Language module file (per generator metadata) | Module detection | Module detection |
| `skills/ddd-implement/generators/` | Generator discovery | Generator discovery |

## Commands

| Command | Description |
|---------|-------------|
| `/ddd-eval` | Full evaluation — both lenses, all dimensions, synthesized |
| `/ddd-eval pragmatic` | Pragmatic lens only — all dimensions |
| `/ddd-eval purity` | Purity lens only — all dimensions |
| `/ddd-eval prd` | Both lenses, PRD dimension only (workspace mode only) |
| `/ddd-eval model` | Both lenses, modeling dimension only |
| `/ddd-eval impl` | Both lenses, implementation dimension only |

## Scoring System

Each dimension is scored 0–100 with a letter grade: A (90–100), B (80–89), C (70–79), D (60–69), F (0–59).

**Report formats**: See `eval-report-formats.md` for all output templates and error messages.

---

## Entry Point

### Actions

1. Check `$ARGUMENTS` for a lens (`pragmatic`, `purity`) or dimension (`prd`, `model`, `impl`)
   - No argument → both lenses, all dimensions
   - `pragmatic` or `purity` → that lens only, all dimensions
   - `prd`, `model`, or `impl` → both lenses, that dimension only
2. Detect data source mode: look for `ddd-workspace/` in the project root
3. Detect project language and resolve generator:
   - Scan `skills/ddd-implement/generators/` for available generators
   - Read each `generator.md` Metadata section to build a map of language → generator
   - For each generator, read its `generator.md` to identify the expected module file (e.g., `go.mod` for Go generators)
   - Check the project root for any of those module files
   - If a matching generator exists → use its patterns, naming conventions, and validation rules for scoring
   - If no matching generator exists but a recognizable project structure is found → use [generic analysis](#generic-analysis-fallback) (language-agnostic DDD heuristics)
   - If no project detected → show error (see `eval-report-formats.md`)
4. If codebase mode, scan for DDD signals using the resolved generator's conventions (or generic patterns):
   - **With generator**: Use directory structure, file patterns, and naming conventions from `generator.md`
   - **Generic fallback**: Scan for common DDD patterns across languages:
     - Directory patterns: `domain/`, `application/`, `ports/`, `adapters/`, `internal/{context}/`, `src/{context}/`
     - File patterns: `*entity*`, `*repository*`, `*service*`, `*event*`, `*aggregate*`, `*value_object*`
     - Code patterns: aggregate roots, value objects, domain events, port interfaces
   - If no DDD patterns found → show error (see `eval-report-formats.md`)
5. Route to the selected lens/dimension combination

---

## The Two Lenses

### Pragmatic Lens

Answers: **"Is this DDD helping the project?"**

- A well-placed shortcut that simplifies the codebase is a strength, not a violation
- Over-abstracted domains with unnecessary files score poorly
- Unused layers or empty interfaces score poorly — ceremony without value
- Good naming that communicates intent scores well even if it bends conventions
- Business logic living in the domain where it belongs scores well

### Purity Lens

Answers: **"Is this DDD structurally correct?"**

- Every pattern deviation is a deduction, regardless of justification
- Missing template sections, wrong naming conventions, absent interface assertions — all count
- Import direction violations are hard failures
- Completeness matters — partial adoption scores lower than full adoption

---

## Full Evaluation (default)

1. Run each dimension through **both lenses** (PRD and Traceability are workspace-mode only)
2. Compute per-lens overall scores as weighted averages:
   - Workspace mode: PRD 15%, Modeling 30%, Implementation 40%, Traceability 15%
   - Codebase mode: Modeling 40%, Implementation 60%
3. Synthesize agreements and divergences between lenses

---

## Dimension: PRD

**Workspace mode only.** In codebase mode, show message suggesting `/ddd-extract-prd`.

### Actions

1. If codebase mode (no `ddd-workspace/`), show message suggesting `/ddd-extract-prd`
2. Look for PRD files in `ddd-workspace/prd/*.md`
   - If none found, score 0 with note suggesting `/ddd-extract-prd`
3. Read the PRD file and score against both rubrics below

### PRD Pragmatic Rubric

| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| Requirements actionability | 25% | Can a developer read a requirement and know what to build? Are acceptance criteria specific enough to test? Deduct for vague stories or untestable criteria. |
| Business rule usefulness | 25% | Are business rules stated in domain language a developer can translate to code? Do they capture real constraints, not obvious validations? Deduct for trivial rules (e.g., "field is required") or rules that restate the requirement. |
| Scope realism | 20% | Is the scope achievable? Are out-of-scope items handled with mitigations? Deduct for scope that tries to cover too much or defers critical dependencies without mitigation. |
| Domain language clarity | 15% | Does the glossary capture terms that actually disambiguate? Would a new team member understand the domain faster? Deduct for glossary padding (obvious terms) or missing terms that caused real confusion. |
| Downstream readiness | 15% | Can `/ddd-model` consume this PRD productively? Are functional areas cohesive enough to suggest bounded contexts? Deduct if areas are too coarse or too fine to map to contexts. |

### PRD Purity Rubric

| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| Section completeness | 25% | All 17 sections from [schema.md](../ddd-prd/schema.md) present (15 required, 2 optional: sections 11 and 12). Deduct proportionally per missing required section. |
| Business rule explicitness | 20% | Rules in catalog (Section 7), not embedded in acceptance criteria. Score 100 if all rules are in catalog; deduct per embedded rule found in Section 5. |
| Glossary coverage | 15% | Domain terms in glossary (Section 6) match terms used throughout. Score based on ratio of defined vs. referenced terms. |
| Functional area cohesion | 15% | Each area (Section 4) has cohesion rationale, key terms, key entities. Deduct per area missing rationale. |
| Traceability IDs | 15% | FR-\*, BR-\*, CE-\*, IT-\* IDs assigned and referenced in index (Section 16). Score based on ratio of ID'd items vs. total. |
| Entity clarity | 10% | Entities (Section 8) have descriptions, attributes, relationships. Deduct per entity missing key fields. |

---

## Dimension: Model

Works in both data source modes.

### Workspace Mode Actions

1. Read `ddd-workspace/ddd-model.manifest.json` for context list and phase status
2. Read each FQBC file in `ddd-workspace/fqbc/*.md`
3. Optionally read `ddd-workspace/bcr/coherence-review.md` for coherence findings
4. Score against both rubrics

### Codebase Mode Actions

1. Scan for bounded context directories using resolved generator's structure or generic patterns (`domain/`, `*domain/`, `ports/`, `application/`)
2. For each context, scan domain layer for entities, value objects, aggregate roots, domain events, domain services
3. Scan for port interfaces and bounded context separation signals
4. Score against both rubrics

### Model Pragmatic Rubric (Workspace)

| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| Context boundary fitness | 30% | Do the bounded contexts align with real business capabilities? Could a team own one context independently? Deduct for contexts that are too granular (one entity) or too coarse (a monolith behind a label). |
| Ubiquitous language value | 20% | Glossary captures terms that actually vary across contexts? Not just PRD copy? |
| Aggregate sizing | 20% | Sized for real transactional boundaries? Not entire context or every entity? |
| Event usefulness | 15% | Events represent real business moments others care about? Not just CRUD? |
| Context relationship clarity | 15% | Upstream/downstream clear about data flow and ownership? |

### Model Pragmatic Rubric (Codebase)

| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| Context boundary fitness | 30% | Directory boundaries match business capabilities? Domain package focused? |
| Domain model expressiveness | 25% | Names and methods read like business language? Not anemic models? |
| Aggregate transaction scope | 20% | Aggregates protect meaningful invariants? Not just data containers? |
| Event business alignment | 15% | Events represent real business moments? Not persistence hooks? |
| Port contract clarity | 10% | Ports communicate what context needs? Not overly generic or leaking impl? |

### Model Purity Rubric (Workspace)

| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| FQBC completeness | 25% | All 9 sections per [fqbc-template.md](../ddd-model/fqbc-template.md) present. Average section completeness across all FQBCs. |
| Ubiquitous language coverage | 20% | Each FQBC has a populated glossary (Section 2) with terms used consistently. Deduct for empty glossaries or undefined terms in behaviors. |
| Domain model richness | 20% | Aggregates, entities, VOs defined (Section 4) with invariants and rules. Deduct for aggregates without invariants, entities without lifecycle. |
| Event contracts | 15% | Outbound events (Section 6) have triggers, payloads, consumers. Deduct per event missing fields. |
| Context relationships | 10% | Section 8 defines upstream/downstream with integration patterns. Deduct per context missing relationship definitions. |
| Coherence review | 10% | Coherence review exists and has no unresolved critical findings. Score 100 if review passed; deduct per unresolved finding. |

### Model Purity Rubric (Codebase)

Derived from validate findings (phases 1–3 and 8b):

| Category | Weight | Source |
|----------|--------|--------|
| Domain layer structure | 30% | Phase 1 + Phase 2 findings |
| Entity/VO/Aggregate patterns | 30% | Phase 2 findings |
| Bounded context separation | 20% | Phase 8b findings |
| Event & port definitions | 20% | Phase 2 + Phase 3 findings |

---

## Dimension: Impl

Works in both data source modes.

### Actions

1. **Run validate** (from `ddd-implement/validate.md`) against the project. If a recent `ddd-validation-report.md` exists, read it instead.
2. Score **pragmatic lens** by reading source code directly — requires understanding intent.
3. Score **purity lens** by categorizing and counting validate findings.

### Impl Pragmatic Rubric

| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| Abstraction payoff | 25% | Are layers earning their cost? Deduct for: ports with only one impl and no testing benefit, services that just delegate, adapters that add a layer without value. |
| Domain logic placement | 25% | Business logic in domain layer? Deduct for: rules in HTTP handlers, validation in adapters, anemic entities. |
| Developer experience | 20% | Can a new developer navigate? Predictable structure? Deduct for: deep nesting without payoff, inconsistent organization. |
| Error handling value | 15% | Error types communicate in domain terms? Deduct for: generic strings, swallowed errors, lost domain context across layers. |
| Cross-context communication | 15% | Contexts communicate through defined boundaries? Deduct for: reaching into internals, missing event wiring. |

### Impl Purity Rubric

Derived from validate findings (`ddd-implement/validate.md`). Validate is the single source of truth for structural checks.

**Scoring formula per category**: Start at 100. Deduct 10 per error, 3 per warning. Floor at 0. Overall = weighted average.

| Category | Weight | Source (validate phases) |
|----------|--------|--------------------------|
| Directory structure | 15% | Phase 0–1 findings |
| Domain layer correctness | 20% | Phase 2 findings |
| Port/adapter contracts | 20% | Phase 3–6 findings |
| Mock layer | 10% | Phase 7 findings |
| Dependency direction & isolation | 25% | Phase 8a–8b findings |
| API contract alignment | 10% | Phase 8c findings |

---

## Traceability (Workspace Mode Only)

Fourth dimension in full evaluation. In codebase mode, traceability is skipped with the note: "Traceability requires a DDD workspace with PRD and FQBC documents."

### Traceability Pragmatic Rubric

| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| Requirement coverage | 50% | Can you trace from PRD business need to implementing context? |
| Decision rationale value | 50% | Design decisions explain *why* in a way that helps future developers? |

### Traceability Purity Rubric

| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| PRD→FQBC references | 40% | FQBCs reference FR-\* and BR-\* IDs in Section 9. |
| Design decisions documented | 30% | FQBCs include decisions with rationale and alternatives. |
| Coherence review coverage | 30% | Coherence review exists and addresses all contexts. |

---

## Generic Analysis Fallback

When a project language is detected but no matching generator exists.

| Aspect | With Generator | Generic Fallback |
|--------|---------------|-----------------|
| Directory scanning | Generator's defined structure | Common DDD directories (`domain/`, `application/`, `ports/`, `adapters/`) |
| File patterns | Generator's naming conventions | Files containing `entity`, `repository`, `service`, `event`, `aggregate`, `value_object` |
| Dependency direction | Generator's import rules | Language-native import statements against detected layer boundaries |
| Naming conventions | Checks against convention table | Skipped — "N/A (no generator)" |
| Pattern compliance | Validates against pattern files | Structural presence only (layers exist, interfaces defined) |

### Generic mode scoring adjustments

- **Purity lens**: Criteria that require generator-specific rules (naming conventions, exact pattern compliance) are scored as "N/A" and excluded from the weighted average. The purity score reflects only what can be validated generically (layer separation, dependency direction, bounded context isolation).
- **Pragmatic lens**: Fully applicable — pragmatic criteria are inherently language-agnostic.
- A note is included in the report: "Partial purity scoring — no generator available for [language]. Install a generator for full purity analysis."
