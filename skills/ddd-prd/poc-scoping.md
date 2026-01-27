# PoC Scoping Criteria

Guidelines for identifying the minimum viable feature set for a Proof of Concept.

## Inclusion Criteria

Features should be included in PoC scope when they meet ANY of these criteria:

### 1. Core Value Validation
- Demonstrates the primary value proposition to stakeholders
- Answers the key question: "Does this solution work?"
- Cannot be simulated or mocked without losing validation value

### 2. End-to-End Flow Enablement
- Required to complete at least one meaningful user journey
- Connects critical system components
- Enables demonstration of the "happy path"

### 3. Priority Indicators in Source
Look for these signals in the source documentation:
- `Priority: 1` or `Priority: P1` or `Priority: High`
- `Phase: 1` or `Phase: MVP` or `Phase: Initial`
- `Status: Must Have` or `MoSCoW: Must`
- Explicitly marked as "core" or "essential"

### 4. Stakeholder Visibility
- Features stakeholders will directly interact with during demo
- Features that produce visible, tangible output
- Administrative functions needed by primary users

## Exclusion Criteria

Features should be excluded from PoC when they meet ANY of these criteria:

### 1. Enhancement Over Core
- Improves UX but doesn't enable new capability
- Optimizes performance without functional change
- Adds convenience without validation value

**Examples**: Bulk operations, keyboard shortcuts, advanced filtering, export options

### 2. External Dependencies
- Requires integration with systems not yet available
- Depends on third-party services not yet contracted
- Needs data that doesn't exist yet

**Mitigation**: Note as assumption; mock or stub for PoC if critical path

### 3. Scale and Performance
- Handles edge cases for high volume
- Optimizes for production load
- Implements caching, queuing, or distribution

**Rationale**: PoC validates functionality, not scale

### 4. Secondary User Flows
- Error recovery workflows (manual intervention acceptable)
- Administrative tasks that can be done via database
- Audit/compliance features beyond basic logging

### 5. Priority Indicators in Source
- `Priority: 2` or `Priority: Low`
- `Phase: 2+` or `Phase: Future`
- `Status: Nice to Have` or `MoSCoW: Could/Won't`

## Scoping Decision Framework

For each feature, ask these questions in order:

```
1. Can we validate the core hypothesis without this feature?
   YES → Exclude (unless required for demo flow)
   NO  → Include

2. Can this feature be manually simulated for the PoC period?
   YES → Exclude (note in assumptions)
   NO  → Include

3. Is this feature explicitly marked as P1/MVP/Must-Have?
   YES → Include
   NO  → Review with stakeholder

4. Does a stakeholder need to see this feature working?
   YES → Include
   NO  → Exclude
```

## Documenting Scope Decisions

For each excluded feature, document:
- **Feature name**: Clear identifier
- **Reason for exclusion**: Which criterion applies
- **Mitigation**: How PoC handles absence (mock, manual, deferred)
- **Dependency**: What would need to change to include it

Example:
```
| Feature | Reason | Mitigation |
|---------|--------|------------|
| Email notifications | External dependency (email service) | Manual notification during demo |
| Bulk status update | Enhancement over core | Single-item update sufficient |
| Threshold configuration | Admin feature | Pre-seed thresholds in database |
```

## Functional Cohesion Criteria

When grouping features into functional areas, evaluate cohesion to identify potential Bounded Context boundaries.

### High Cohesion Indicators (Group Together)

- **Shared Ubiquitous Language**: Features use the same terms with the same meanings
- **Shared Entities**: Features operate on the same conceptual things
- **Shared Business Rules**: Features are governed by the same policies
- **Shared Lifecycle**: Features change together when business needs evolve
- **Single Stakeholder**: Features are owned by the same business role

### Low Cohesion Indicators (Consider Separating)

- **Terminology Collision**: Same word means different things across features
- **Independent Lifecycles**: One set of features changes frequently, another is stable
- **Different Stakeholders**: Features are owned by different business roles
- **Loose Interaction**: Features interact through well-defined data handoffs, not shared state

### Grouping Decision Framework

```
1. Do these features share key domain terms with consistent meaning?
   YES → Strong cohesion signal
   NO  → Consider separation

2. Do these features operate on the same conceptual entities?
   YES → Strong cohesion signal
   NO  → Consider separation

3. Would a business change likely affect both features together?
   YES → Strong cohesion signal
   NO  → Consider separation

4. Are these features owned by the same business stakeholder?
   YES → Supports grouping
   NO  → Consider separation (unless technically inseparable)
```

### Documentation

For each functional area, document:
- **Area Name**: Clear, domain-aligned name
- **Cohesion Rationale**: Why these features belong together
- **Key Terms**: Domain terminology specific to this area
- **Boundary Signals**: What distinguishes this area from others

## Minimum Viable Scope Checklist

Before finalizing scope, verify:

- [ ] At least one complete user journey is possible
- [ ] Core value proposition is demonstrable
- [ ] All P1/MVP items are included (or justified exclusion)
- [ ] No feature depends on excluded feature
- [ ] Excluded features have documented mitigation
- [ ] Scope is achievable in stated timeline
- [ ] Functional areas are cohesive (shared terms, entities, rules)
- [ ] Area boundaries align with terminology boundaries
