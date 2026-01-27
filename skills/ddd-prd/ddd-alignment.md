# DDD Alignment Guide

Guidance for extracting Domain-Driven Design artifacts from product documentation to feed Bounded Context Review.

## Extraction Goals

The PRD should provide raw material for DDD work without prescribing technical design:

| Extract This | To Seed This (in FQBC) |
|--------------|------------------------|
| Domain terminology | Ubiquitous Language |
| Business rules | Domain model rules |
| Conceptual entities | Aggregates, Entities, Value Objects |
| Functional areas | Bounded Context candidates |
| Integration touchpoints | Context mapping |
| Role capabilities | Access patterns, Commands |

## Domain Terminology Extraction

### What to Capture

- **Nouns**: Things the business talks about (Order, Customer, Threshold, Alert)
- **Verbs**: Actions the business performs (Submit, Approve, Escalate, Archive)
- **States**: Conditions things can be in (Pending, Active, Suspended)
- **Roles**: Who interacts with the system (Analyst, Manager, Auditor)

### How to Capture

For each term, record:
- **Term**: The word as used in source docs
- **Working Definition**: What it means in this domain (may differ from common usage)
- **Functional Area**: Which area uses this term
- **Variants**: Other words used for the same concept (synonyms to resolve)

### Warning Signs

- **Same word, different meanings**: "Customer" in Sales vs Support — indicates context boundary
- **Different words, same meaning**: "Client" and "Customer" used interchangeably — needs resolution
- **Vague terms**: "Item", "Record", "Thing" — needs domain-specific naming

## Business Rules Extraction

### What Qualifies as a Business Rule

Business rules are **explicit policies and constraints** that govern the domain. They are NOT:
- UI validation (that's implementation)
- Database constraints (that's technical design)
- Acceptance criteria (those verify behavior; rules define policy)

### Categories

1. **Invariants**: Must always be true
   - "An order must have at least one line item"
   - "Account balance cannot be negative"

2. **Preconditions**: Must be true before an action
   - "Only managers can approve expenses over $1000"
   - "Items can only be added to cart if in stock"

3. **Postconditions**: Must be true after an action
   - "After submission, order status must be 'Pending'"
   - "Approval must generate audit entry"

4. **Derivations**: How values are calculated
   - "Total = sum of line items minus discounts plus tax"
   - "Risk score = weighted average of factors A, B, C"

### How to Capture

| ID | Rule Statement | Type | Entities | Area |
|----|----------------|------|----------|------|
| BR-01 | [Clear, testable statement] | Invariant/Pre/Post/Derivation | [What it governs] | [Functional area] |

## Conceptual Entity Extraction

### What to Capture

Identify **what things exist** in the domain, not how to model them technically.

- **Identity**: Does this thing have a unique identity that persists over time?
- **Attributes**: What characteristics define or describe it?
- **Relationships**: How does it relate to other things?
- **Lifecycle**: What states can it be in? What transitions occur?

### How to Capture

```
Entity: [Name]
Description: [What it represents in the business]
Key Attributes: [Important characteristics]
Relationships: [Links to other entities]
Lifecycle: [States and transitions, if applicable]
Area: [Functional area]
```

### Avoid

- Data types (string, int, date) — that's technical design
- Database columns — that's implementation
- API field names — that's interface design

Focus on **what the business cares about**, not how developers might store it.

## Functional Area Identification

### Cohesion Signals

Features belong in the same functional area when they:

1. **Share terminology**: Same words mean the same things
2. **Share entities**: Operate on the same conceptual things
3. **Share rules**: Governed by the same business policies
4. **Change together**: Business changes affect them as a unit
5. **Have same stakeholder**: Owned by the same business role

### Boundary Signals

Features belong in different areas when:

1. **Terminology diverges**: Same word means different things
2. **Different lifecycles**: One changes frequently, other is stable
3. **Different stakeholders**: Owned by different business roles
4. **Loose coupling**: Interact through well-defined handoffs

### Documentation Format

```
Functional Area: [Name]
Cohesion Rationale: [Why these features belong together]
Key Terms: [Domain terms specific to this area]
Key Entities: [Conceptual entities owned by this area]
Key Rules: [Business rules enforced by this area]
Stakeholder: [Primary business owner]
```

## Integration Touchpoints

### What to Capture

Identify where functional areas (or external systems) must interact:

- **Direction**: Who initiates? Who responds?
- **Trigger**: What causes the interaction?
- **Data**: What information flows?
- **Timing**: Synchronous need or eventual consistency acceptable?

### How to Capture

| From | To | Trigger | Data Flow | Timing |
|------|-----|---------|-----------|--------|
| [Area/System] | [Area/System] | [What initiates] | [What passes] | Sync/Async |

### Maps to Context Mapping

These touchpoints become inputs for Context Mapping patterns:
- Tight coupling → Shared Kernel or Partnership
- Clear upstream/downstream → Customer-Supplier
- Translation needed → Anti-Corruption Layer
- Event-based → Published Language

## Product Team Technical Expectations

### What to Capture

Product teams often include technical concepts (APIs, data models, schemas) in their docs. Capture these as **context for engineering**, not specifications:

- What did product team envision?
- What assumptions did they make?
- What constraints did they express?

### How to Present

```
Product Team Expectations

The source documentation included technical concepts:

- [Concept]: [What they envisioned] — [Why they thought this]

Note: These provide context for engineering decisions but are not
specifications. The Bounded Context Review will determine appropriate
technical design.
```

## Traceability

### Why It Matters

The Bounded Context Review and FQBC documents should trace back to PRD requirements. This enables:
- Impact analysis when requirements change
- Validation that all requirements are addressed
- Audit trail for design decisions

### ID Scheme

Use consistent, traceable IDs:
- `FR-[area]-[number]` for functional requirements
- `BR-[number]` for business rules
- `CE-[number]` for conceptual entities
- `IT-[number]` for integration touchpoints

FQBC documents will reference these IDs when citing source requirements.
