# Eval Report Formats

Output templates for each `/ddd-eval` command. All reports follow the same structure: header, scores table, lens-specific assessments, and synthesis/recommendations.

## Full Evaluation Report

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
- [e.g., "Application service accesses repository directly — simpler but violates hexagonal purity"]

**Purity high, Pragmatic low** (correct but questionable value):
- [e.g., "Full FQBC template for a trivial lookup context — complete but over-documented"]

### Priority Actions

1. [most impactful — actions from the "both agree: problems" category first]
2. [second priority]
3. [third priority]

### Suggested Next Steps

- [actionable step, referencing pipeline skills where relevant]
```

---

## Pragmatic Lens Report

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

## Purity Lens Report

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

## PRD Dimension Report

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

## Model Dimension Report

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
| [name] | [score] | [score] | [what stands out] |

### Synthesis

[Where the two lenses agree and diverge for modeling]
```

---

## Impl Dimension Report

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
- [e.g., "Domain isolation is both structurally clean and genuinely useful"]

**Divergences**:
- [e.g., "Port interfaces exist for purity but single-implementation ports add indirection without testing benefit yet"]

### Recommendations

- [prioritized by synthesis — fix "both agree" problems first]
```

---

## Error Templates

### No Project Found

```markdown
## No Project Found

No recognized language module file found in the current project root.
Checked against module files defined in available generators at `skills/ddd-implement/generators/*/generator.md`.

**Make sure** you're running from the project root (where your module/package file lives).
```

### No DDD Patterns

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

### Partial Workspace

When `ddd-workspace/` exists but is incomplete, do not treat as an error. Score what's available and note what's missing:

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
