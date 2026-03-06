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
| Project source code (structure per generator or generic scan) | Impl scoring | All scoring |
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

Each dimension is scored 0–100 with a letter grade, per lens:

| Score | Grade |
|-------|-------|
| 90–100 | A |
| 80–89 | B |
| 70–79 | C |
| 60–69 | D |
| 0–59 | F |

---

## Entry Point

### Actions

1. Check `$ARGUMENTS` for a lens (`pragmatic`, `purity`) or dimension (`prd`, `model`, `impl`)
   - No argument → both lenses, all dimensions
   - `pragmatic` or `purity` → that lens only, all dimensions
   - `prd`, `model`, or `impl` → both lenses, that dimension only
2. Detect data source mode:
   - Look for `ddd-workspace/` in the project root
   - If found → **workspace mode**
   - If not found → **codebase mode**
3. Detect project language and resolve generator:
   - Scan `skills/ddd-implement/generators/` (relative to the companion repo) for available generators
   - Read each `generator.md` Metadata section to build a map of language → generator
   - For each generator, read its `generator.md` to identify the expected module file (e.g., `go.mod` for Go generators)
   - Check the project root for any of those module files
   - If a matching generator exists → use its patterns, naming conventions, and validation rules for scoring
   - If no matching generator exists but a recognizable project structure is found → use [generic analysis](#generic-analysis-fallback) (language-agnostic DDD heuristics)
   - If no project detected → show [No Project Found](#error-no-project-found) error
4. If codebase mode, scan for DDD signals using the resolved generator's conventions (or generic patterns):
   - **With generator**: Use directory structure, file patterns, and naming conventions from `generator.md`
   - **Generic fallback**: Scan for common DDD patterns across languages:
     - Directory patterns: `domain/`, `application/`, `ports/`, `adapters/`, `internal/{context}/`, `src/{context}/`
     - File patterns: `*entity*`, `*repository*`, `*service*`, `*event*`, `*aggregate*`, `*value_object*`
     - Code patterns: aggregate roots, value objects, domain events, port interfaces
   - If no DDD patterns found → show [No DDD Patterns](#error-no-ddd-patterns) error
5. Route to the selected lens/dimension combination

---

## The Two Lenses

### Pragmatic Lens

The pragmatic lens answers: **"Is this DDD helping the project?"**

It evaluates whether the DDD patterns are earning their keep — whether the boundaries reflect real business needs, whether the complexity is justified, and whether the team is getting value from the structure.

**Pragmatic scoring philosophy**:
- A well-placed shortcut that simplifies the codebase is a strength, not a violation
- An over-abstracted domain with three files where one would do scores poorly
- Unused layers or empty interfaces score poorly — ceremony without value
- Good naming that communicates intent scores well even if it bends conventions
- Business logic living in the domain where it belongs scores well

### Purity Lens

The purity lens answers: **"Is this DDD structurally correct?"**

It evaluates strict adherence to DDD tactical patterns, hexagonal architecture rules, and the conventions defined by this pipeline. This is the "by the book" evaluation.

**Purity scoring philosophy**:
- Every pattern deviation is a deduction, regardless of justification
- Missing template sections, wrong naming conventions, absent interface assertions — all count
- Import direction violations are hard failures
- Completeness matters — partial adoption scores lower than full adoption

---

## Command: Full Evaluation (default)

When invoked without arguments, run both lenses across all dimensions and synthesize.

### Actions

1. Detect data source mode (workspace or codebase)
2. Run each dimension through **both lenses**:
   - **PRD** — workspace mode only; skip with note in codebase mode
   - **Modeling** — both data source modes
   - **Implementation** — both data source modes
   - **Traceability** — workspace mode only; skip with note in codebase mode
3. Compute per-lens overall scores as weighted averages:
   - Workspace mode: PRD 15%, Modeling 30%, Implementation 40%, Traceability 15%
   - Codebase mode: Modeling 40%, Implementation 60%
4. Synthesize where the lenses agree and diverge
5. Present combined report

### Output

```markdown
## DDD Evaluation Report

**Project**: [project name from module file or manifest]
**Language**: [detected language]
**Generator**: [generator name or "Generic (no generator)"]
**Data Source**: [Workspace | Codebase]
**Date**: [current date]

### Scores at a Glance

| Dimension | Pragmatic | Purity | Notes |
|-----------|-----------|--------|-------|
| PRD Quality | [score] ([grade]) | [score] ([grade]) | [or "Skipped — no workspace"] |
| Modeling Quality | [score] ([grade]) | [score] ([grade]) | [one-line] |
| Implementation Quality | [score] ([grade]) | [score] ([grade]) | [one-line] |
| Traceability | [score] ([grade]) | [score] ([grade]) | [or "Skipped — no workspace"] |
| **Overall** | **[score] ([grade])** | **[score] ([grade])** | |

### Synthesis

#### Agreements — both lenses say the same thing

**Strengths** (pragmatic + purity agree these are good):
- [strength — e.g., "Domain isolation is clean AND serves the team well"]

**Problems** (pragmatic + purity agree these need work):
- [problem — e.g., "Missing port interfaces hurts both correctness and developer experience"]

#### Divergences — the lenses disagree

**Pragmatic high, Purity low** (works well but bends the rules):
- [e.g., "Application service accesses repository directly without port interface — simpler for a single-context app, but violates hexagonal purity"]

**Purity high, Pragmatic low** (correct but questionable value):
- [e.g., "Full FQBC template for a trivial lookup context — structurally complete but over-documented for its complexity"]

### Priority Actions

1. [most impactful — actions from the "both agree: problems" category first]
2. [second priority]
3. [third priority]

### Suggested Next Steps

- [actionable step, referencing pipeline skills where relevant]
```

---

## Command: Pragmatic

**Usage**: `/ddd-eval pragmatic`

Run the pragmatic lens across all dimensions.

### Output

```markdown
## DDD Pragmatic Evaluation

**Project**: [project name]
**Data Source**: [Workspace | Codebase]

### Overall Pragmatic Score: [score]/100 ([grade])

| Dimension | Score | Grade | Verdict |
|-----------|-------|-------|---------|
| PRD Quality | [score] | [grade] | [one-line pragmatic verdict] |
| Modeling Quality | [score] | [grade] | [one-line pragmatic verdict] |
| Implementation Quality | [score] | [grade] | [one-line pragmatic verdict] |
| Traceability | [score] | [grade] | [one-line pragmatic verdict] |

### What's Earning Its Keep

- [pattern/structure that is delivering real value]

### What's Not Pulling Its Weight

- [pattern/structure that adds complexity without proportional benefit]

### What's Missing That Would Help

- [practical improvement that would make the codebase easier to work with]
```

---

## Command: Purity

**Usage**: `/ddd-eval purity`

Run the purity lens across all dimensions.

### Output

```markdown
## DDD Purity Evaluation

**Project**: [project name]
**Data Source**: [Workspace | Codebase]

### Overall Purity Score: [score]/100 ([grade])

| Dimension | Score | Grade | Violations |
|-----------|-------|-------|------------|
| PRD Quality | [score] | [grade] | [N] issues |
| Modeling Quality | [score] | [grade] | [N] issues |
| Implementation Quality | [score] | [grade] | [N] issues |
| Traceability | [score] | [grade] | [N] issues |

### Violations by Severity

| Severity | Count | Examples |
|----------|-------|---------|
| error | [N] | [top violations] |
| warning | [N] | [top violations] |
| info | [N] | [top violations] |

### Detailed Findings

[Findings grouped by dimension, then by severity]:

[severity] `file:line` — Description (ref: pattern-file#section)
```

---

## Dimension: PRD

**Usage**: `/ddd-eval prd`

Score PRD quality through both lenses. Workspace mode only.

### Actions

1. If codebase mode (no `ddd-workspace/`), show:
   ```
   PRD evaluation requires a DDD workspace.
   Run `/ddd-extract-prd [source]` to create a PRD from your documentation.
   ```
2. Look for PRD files in `ddd-workspace/prd/*.md`
   - If none found, score 0 with note suggesting `/ddd-extract-prd`
3. Read the PRD file and score against both rubrics below

### PRD Pragmatic Rubric

| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| Requirements actionability | 25% | Can a developer read a requirement and know what to build? Are acceptance criteria specific enough to test? Deduct for vague stories or untestable criteria. |
| Business rule usefulness | 25% | Are business rules stated in domain language a developer can translate to code? Do they capture real constraints the business cares about, not obvious validations? Deduct for trivial rules (e.g., "field is required") or rules that restate the requirement. |
| Scope realism | 20% | Is the scope achievable? Are out-of-scope items handled with mitigations? Deduct for scope that tries to cover too much or defers critical dependencies without mitigation. |
| Domain language clarity | 15% | Does the glossary capture terms that actually disambiguate? Would a new team member understand the domain faster with this PRD? Deduct for glossary padding (obvious terms) or missing terms that caused real confusion. |
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

### Output

```markdown
## PRD Evaluation

**PRD**: [filename]

| Lens | Score | Grade |
|------|-------|-------|
| Pragmatic | [score] | [grade] |
| Purity | [score] | [grade] |

### Pragmatic Assessment

| Criterion | Score | Verdict |
|-----------|-------|---------|
| Requirements Actionability | [score] | [verdict] |
| Business Rule Usefulness | [score] | [verdict] |
| Scope Realism | [score] | [verdict] |
| Domain Language Clarity | [score] | [verdict] |
| Downstream Readiness | [score] | [verdict] |

### Purity Assessment

| Criterion | Score | Details |
|-----------|-------|---------|
| Section Completeness | [score] | [N/15] sections present |
| Business Rule Explicitness | [score] | [N] in catalog, [M] embedded |
| Glossary Coverage | [score] | [N] defined, [M] undefined |
| Functional Area Cohesion | [score] | [N/M] areas with rationale |
| Traceability IDs | [score] | [N]% coverage |
| Entity Clarity | [score] | [N/M] fully described |

### Synthesis

[Where the two lenses agree and diverge for this dimension]
```

---

## Dimension: Model

**Usage**: `/ddd-eval model`

Score domain modeling quality through both lenses. Works in both data source modes.

### Workspace Mode Actions

1. Read `ddd-workspace/ddd-model.manifest.json` for context list and phase status
2. Read each FQBC file in `ddd-workspace/fqbc/*.md`
3. Optionally read `ddd-workspace/bcr/coherence-review.md` for coherence findings
4. Score against both rubrics

### Codebase Mode Actions

1. Scan for bounded context directories using the resolved generator's directory structure (or generic patterns):
   - **With generator**: Use the generator's defined structure (e.g., `internal/{context}/` for Go-hex)
   - **Generic fallback**: Look for directories containing DDD layer subdirectories (`domain/`, `*domain/`, `ports/`, `application/`, `*application/`)
2. For each context, scan domain layer files for:
   - Entity definitions (types/classes with ID fields, constructors/factory methods)
   - Value object definitions (immutable types with validated constructors)
   - Aggregate roots (types composing or extending base entity types)
   - Domain events (types representing past-tense business occurrences)
   - Domain services
3. Scan for port interfaces in `ports/` directories or equivalent boundary definitions
4. Look for bounded context separation signals
5. Score against both rubrics

### Model Pragmatic Rubric

**Workspace mode**:

| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| Context boundary fitness | 30% | Do the bounded contexts align with real business capabilities? Could a team own one context independently? Deduct for contexts that are too granular (one entity) or too coarse (a monolith behind a label). |
| Ubiquitous language value | 20% | Does the glossary capture terms that actually vary across contexts (same word, different meaning)? Deduct for glossaries that just copy the PRD without refinement. |
| Aggregate sizing | 20% | Are aggregates sized for real transactional boundaries? Deduct for aggregates that are too large (entire context in one aggregate) or too small (every entity is its own aggregate). |
| Event usefulness | 15% | Do events represent real business moments that other contexts care about? Deduct for events that nobody subscribes to or events that are just CRUD notifications. |
| Context relationship clarity | 15% | Are upstream/downstream relationships clear about what data flows and who owns it? Deduct for vague relationships or missing integration patterns. |

**Codebase mode**:

| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| Context boundary fitness | 30% | Do directory boundaries match business capabilities? Is each context's domain package focused on a single responsibility? Deduct for contexts that share too many types or have blurred responsibilities. |
| Domain model expressiveness | 25% | Do entity/VO names and methods read like business language? Can you understand the domain from the code without external docs? Deduct for anemic models (structs with only getters/setters) or technical names that obscure domain intent. |
| Aggregate transaction scope | 20% | Do aggregates protect meaningful invariants? Deduct for aggregates that are just data containers or aggregates so large they'd cause contention. |
| Event business alignment | 15% | Do domain events represent real business moments? Deduct for events that are just persistence hooks or CRUD wrappers. |
| Port contract clarity | 10% | Do port interfaces communicate what the context needs from the outside world? Deduct for overly generic ports or ports that leak implementation details. |

### Model Purity Rubric

**Workspace mode**:

| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| FQBC completeness | 25% | All 9 sections per FQBC template present ([fqbc-template.md](../ddd-model/fqbc-template.md)). Average section completeness across all FQBCs. |
| Ubiquitous language coverage | 20% | Each FQBC has a populated glossary (Section 2) with terms used consistently. Deduct for empty glossaries or undefined terms in behaviors. |
| Domain model richness | 20% | Aggregates, entities, VOs defined (Section 4) with invariants and rules. Deduct for aggregates without invariants, entities without lifecycle. |
| Event contracts | 15% | Outbound events (Section 6) have triggers, payloads, consumers. Deduct per event missing fields. |
| Context relationships | 10% | Section 8 defines upstream/downstream with integration patterns. Deduct per context missing relationship definitions. |
| Coherence review | 10% | Coherence review exists and has no unresolved critical findings. Score 100 if review passed; deduct per unresolved finding. |

**Codebase mode**:

Derive from validate findings (same as impl purity). Use validate phases 1–3 and 8b findings to score domain modeling quality in code:

| Category | Weight | Source (validate phases) |
|----------|--------|--------------------------|
| Domain layer structure | 30% | Phase 1 (directory structure) + Phase 2 (domain layer) findings |
| Entity/VO/Aggregate patterns | 30% | Phase 2 (domain layer) findings |
| Bounded context separation | 20% | Phase 8b (cross-context isolation) findings |
| Event & port definitions | 20% | Phase 2 (domain events) + Phase 3 (ports) findings |

### Output

```markdown
## Modeling Evaluation

**Data Source**: [Workspace | Codebase]
**Contexts Evaluated**: [N]

| Lens | Score | Grade |
|------|-------|-------|
| Pragmatic | [score] | [grade] |
| Purity | [score] | [grade] |

### Pragmatic Assessment

| Criterion | Score | Verdict |
|-----------|-------|---------|
| [criterion] | [score] | [verdict — a short sentence explaining why] |

### Purity Assessment

| Criterion | Score | Details |
|-----------|-------|---------|
| [criterion] | [score] | [quantitative details] |

### Per-Context Summary

| Context | Pragmatic | Purity | Key Observation |
|---------|-----------|--------|-----------------|
| [name] | [score] | [score] | [what stands out — e.g., "well-modeled but over-documented"] |

### Synthesis

[Where the two lenses agree and diverge for modeling]
```

---

## Dimension: Impl

**Usage**: `/ddd-eval impl`

Score implementation architecture conformance through both lenses. Works in both data source modes.

### Actions

1. **Run validate** (from `ddd-implement/validate.md`) against the project to produce structural findings. If a `ddd-validation-report.md` already exists and is recent, read it instead of re-running.
2. Score the **pragmatic lens** by reading the source code directly — pragmatic assessment requires understanding intent, not just structure.
3. Score the **purity lens** by categorizing and counting validate findings by severity and phase.

### Impl Pragmatic Rubric

| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| Abstraction payoff | 25% | Are the layers earning their cost? Deduct for: port interfaces with only one implementation and no testing benefit, application services that just delegate to repositories, adapters that add a layer without adding value. Score highly when layers enable easy testing or swapping. |
| Domain logic placement | 25% | Does business logic live in the domain layer? Deduct for: business rules in HTTP handlers, validation scattered across adapters, domain entities that are just data carriers. Score highly when the domain package is where a developer goes to understand the business. |
| Developer experience | 20% | Can a new developer navigate the codebase? Is the structure predictable? Deduct for: deep nesting without payoff, inconsistent organization between contexts, unclear where to add new features. |
| Error handling value | 15% | Do error types communicate what went wrong in domain terms? Deduct for: generic error strings, swallowed errors, errors that lose domain context when crossing layers. |
| Cross-context communication | 15% | Do contexts communicate through well-defined boundaries? Deduct for: contexts reaching into each other's internals, missing event wiring, synchronous calls where async would be safer. |

### Impl Purity Rubric

The purity score is **derived from validate findings** (`ddd-implement/validate.md`). Validate is the single source of truth for structural checks — eval does not re-implement them.

**Scoring method**: Convert validate findings into a score per category by counting errors and warnings.

| Category | Weight | Source (validate phases) |
|----------|--------|--------------------------|
| Directory structure | 15% | Phase 0–1 findings |
| Domain layer correctness | 20% | Phase 2 findings |
| Port/adapter contracts | 20% | Phase 3–6 findings |
| Mock layer | 10% | Phase 7 findings |
| Dependency direction & isolation | 25% | Phase 8a–8b findings |
| API contract alignment | 10% | Phase 8c findings |

**Scoring formula per category**: Start at 100. Deduct 10 per error, 3 per warning. Floor at 0.

**Overall purity score**: Weighted average of category scores.

### Output

```markdown
## Implementation Evaluation

**Data Source**: [Workspace | Codebase]
**Contexts Evaluated**: [N]

| Lens | Score | Grade |
|------|-------|-------|
| Pragmatic | [score] | [grade] |
| Purity | [score] | [grade] |

### Pragmatic Assessment

| Criterion | Score | Verdict |
|-----------|-------|---------|
| Abstraction Payoff | [score] | [verdict] |
| Domain Logic Placement | [score] | [verdict] |
| Developer Experience | [score] | [verdict] |
| Error Handling Value | [score] | [verdict] |
| Cross-Context Communication | [score] | [verdict] |

### Purity Assessment (from validate)

| Category | Score | Errors | Warnings |
|----------|-------|--------|----------|
| Directory Structure | [score] | [N] | [N] |
| Domain Layer | [score] | [N] | [N] |
| Port/Adapter Contracts | [score] | [N] | [N] |
| Mock Layer | [score] | [N] | [N] |
| Dependency & Isolation | [score] | [N] | [N] |
| API Contract Alignment | [score] | [N] | [N] |

See `ddd-validation-report.md` for detailed findings with file:line references.

### Synthesis

**Agreements**:
- [e.g., "Domain isolation is both structurally clean and genuinely useful — business logic lives where it should"]

**Divergences**:
- [e.g., "Port interfaces exist for purity but the single-implementation ports add indirection without testing benefit yet"]

### Recommendations

- [prioritized by synthesis — fix "both agree" problems first]
```

---

## Traceability Scoring (Workspace Mode Only)

When running the full evaluation in workspace mode, traceability is scored as the fourth dimension.

### Traceability Pragmatic Rubric

| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| Requirement coverage | 50% | Can you trace from a business need in the PRD to the context that implements it? Deduct for requirements that disappear between PRD and FQBCs. |
| Decision rationale value | 50% | Do documented design decisions explain *why* in a way that helps future developers? Deduct for decisions that just restate *what* was done. |

### Traceability Purity Rubric

| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| PRD→FQBC references | 40% | FQBCs reference FR-\* and BR-\* IDs from PRD in their traceability sections (Section 9). Score based on ratio of PRD IDs referenced in at least one FQBC. |
| Design decisions documented | 30% | FQBCs include design decisions with rationale and alternatives (Section 9). Deduct per context with no design decisions. |
| Coherence review coverage | 30% | Coherence review exists and addresses all contexts. Score 100 if review covers all contexts; deduct proportionally. |

In codebase mode, traceability is skipped with the note: "Traceability requires a DDD workspace with PRD and FQBC documents."

---

## Error Handling

### Error: No Project Found

When no recognized language module file is found:

```markdown
## No Project Found

No recognized language module file found in the current project root.

No recognized language module file found. Checked against module files defined in available generators at `skills/ddd-implement/generators/*/generator.md`.

**Make sure** you're running from the project root (where your module/package file lives).
```

---

## Generic Analysis Fallback

When a project language is detected but no matching generator exists in `skills/ddd-implement/generators/`, the eval skill falls back to language-agnostic DDD heuristics.

### What changes in generic mode

| Aspect | With Generator | Generic Fallback |
|--------|---------------|-----------------|
| Directory scanning | Uses generator's defined structure | Scans for common DDD directories (`domain/`, `application/`, `ports/`, `adapters/`, or equivalents) |
| File patterns | Uses generator's naming conventions | Looks for files containing `entity`, `repository`, `service`, `event`, `aggregate`, `value_object` in their names |
| Dependency direction | Uses generator's import rules | Inspects language-native import/require/include statements against detected layer boundaries |
| Naming conventions (Purity) | Checks against generator's convention table | Skipped — reports "N/A (no generator)" for naming convention checks |
| Pattern compliance (Purity) | Validates code against generator's pattern files | Checks structural presence only (layers exist, interfaces defined) without language-specific pattern validation |

### Generic mode scoring adjustments

- **Purity lens**: Criteria that require generator-specific rules (naming conventions, exact pattern compliance) are scored as "N/A" and excluded from the weighted average. The purity score reflects only what can be validated generically (layer separation, dependency direction, bounded context isolation).
- **Pragmatic lens**: Fully applicable — pragmatic criteria are inherently language-agnostic (is the domain logic well-placed? are abstractions earning their keep?).
- A note is included in the report: "Partial purity scoring — no generator available for [language]. Install a generator for full purity analysis."

### Error: No DDD Patterns

When in codebase mode and no DDD patterns are detected:

```markdown
## No DDD Patterns Detected

Scanned the project but found no recognizable DDD patterns:

- No `internal/{context}/{context}domain/` directories
- No `domain/`, `ports/`, `adapters/` directory structure
- No entity, repository, or domain event files

**Possible reasons**:
- The project doesn't follow DDD patterns
- The project uses a different directory convention
- DDD patterns exist but use non-standard naming

**To get started with DDD**:
1. `/ddd-extract-prd [source]` — extract a PRD from your documentation
2. `/ddd-model` — model bounded contexts
3. `/ddd-implement` — generate a walking skeleton
```

### Error: Partial Workspace

When `ddd-workspace/` exists but is incomplete (e.g., PRD exists but no FQBCs):

Do not treat this as an error. Score what's available and note what's missing:

```markdown
### Workspace Status

| Artifact | Status |
|----------|--------|
| PRD | [Found / Not found] |
| Model Manifest | [Found / Not found] |
| FQBCs | [N found / Not found] |
| Coherence Review | [Found / Not found] |
| Implement Manifest | [Found / Not found] |

Dimensions with missing data will be scored on available information only,
or skipped with a note suggesting the appropriate pipeline skill.
```
