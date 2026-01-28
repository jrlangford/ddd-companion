# BCR to TypeSpec Contract Generation Rules

This document defines the mapping rules from BCR (Bounded Context Registry) workspace definitions to TypeSpec API contracts.

## BCR Workspace Structure

The BCR workspace follows this structure:

```
ddd-workspace/
├── manifest.json               # Project state and phase tracking
├── prd/
│   └── {project}-PRD.md        # Source Product Requirements Document
├── bcr/
│   ├── context-discovery.md    # Phase 1: Context identification
│   ├── context-map.md          # Phase 2: Context relationships
│   └── coherence-review.md     # Phase 4: Cross-context consistency
└── fqbc/
    └── {context-name}.md       # Phase 3: Fully Qualified Bounded Context
```

### manifest.json Structure

```json
{
  "version": "1.0",
  "project_name": "Project Name",
  "created": "2026-01-17T10:00:00Z",
  "updated": "2026-01-19T10:00:00Z",
  "prd": {
    "ready": true,
    "path": "prd/Project-PRD.md"
  },
  "current_phase": "complete",
  "phases": {
    "context_discovery": {
      "status": "complete",
      "contexts_identified": ["context-a", "context-b"]
    },
    "context_mapping": { "status": "complete" },
    "fqbc_generation": {
      "status": "complete",
      "contexts": {
        "context-a": { "status": "complete", "file": "fqbc/context-a.md" }
      }
    },
    "coherence_review": { "status": "complete" }
  },
  "decisions": [
    {
      "id": "DEC-001",
      "date": "2026-01-17",
      "decision": "Decision text",
      "rationale": "Rationale text"
    }
  ]
}
```

## FQBC Document Structure

Each Fully Qualified Bounded Context (FQBC) document contains:

1. **Context Identity** - Name, description, boundary rationale
2. **Ubiquitous Language** - Domain terms with definitions
3. **Required Behaviors** - Use cases (commands/queries)
4. **Domain Model** - Business rules, aggregates, entities, value objects
5. **Published Interface** - Commands, queries, events
6. **Context Relationships** - Upstream/downstream dependencies
7. **Traceability** - PRD references

---

## Mapping Rules

### 1. Context to TypeSpec Namespace

Each bounded context maps to a TypeSpec namespace.

**FQBC Input (Section 1):**
```markdown
### Name
**Surveillance Items**

### Description
This context is the operational core of the surveillance system...
```

**TypeSpec Output:**
```typespec
import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";

using Http;
using Rest;

@service({
  title: "Surveillance Items Service",
  version: "1.0.0",
})
@doc("Manages surveillance items lifecycle - creation, routing, review, and resolution")
namespace SurveillanceItems;
```

### 2. Value Objects to TypeSpec Scalars and Models

**FQBC Input (Section 4 - Value Objects):**
```markdown
| Value Object | Attributes | Equality | Usage |
|--------------|------------|----------|-------|
| **VO** ItemInstanceId | value: UUID | UUIDs match | Identity of an item instance |
| **VO** Status | value: enum | Enum values match | PENDING, CHECKED, DISMISSED |
```

**TypeSpec Output:**
```typespec
@doc("Unique identifier for a surveillance item instance")
scalar ItemInstanceId extends string;

@doc("Lifecycle status of a surveillance item")
enum Status {
  @doc("Item awaits review by assigned role holder")
  PENDING: "PENDING",

  @doc("Item was reviewed and appropriately addressed")
  CHECKED: "CHECKED",

  @doc("Item was reviewed, no action needed (requires note)")
  DISMISSED: "DISMISSED",
}
```

### 3. Entities and Aggregates to Models

**FQBC Input (Section 4 - Model Diagram):**
```markdown
class ItemInstance {
    <<Aggregate Root>>
    +id: ItemInstanceId
    +typeId: ItemTypeId
    +status: Status
    +metadata: Metadata
    +sourceProcess: SourceProcessId
    +createdAt: Timestamp
    +resolvedAt: Timestamp?
    +resolvedBy: PersonId?
    +resolutionNote: String?
}
```

**TypeSpec Output:**
```typespec
@doc("A surveillance item instance - the core aggregate")
model ItemInstance {
  @key
  @doc("Unique identifier")
  id: ItemInstanceId;

  @doc("Reference to the item type definition")
  typeId: ItemTypeId;

  @doc("Current lifecycle status")
  status: Status;

  @doc("Type-specific contextual data captured at creation")
  metadata: Record<unknown>;

  @doc("The system that created this item")
  sourceProcess: string;

  @doc("When the item was created")
  createdAt: utcDateTime;

  @doc("When the item was resolved (checked or dismissed)")
  resolvedAt?: utcDateTime;

  @doc("Who resolved the item")
  resolvedBy?: PersonId;

  @doc("Resolution explanation (required for dismissal)")
  resolutionNote?: string;
}
```

### 4. Commands to POST Endpoints

**FQBC Input (Section 5 - Inbound Commands):**
```markdown
#### UpdateItemStatus

**Intent:** Role holder marks an item as reviewed

{
  itemId: ItemInstanceId
  newStatus: "CHECKED" | "DISMISSED"
  note: String?    — required if DISMISSED
}

**Authorization:** `permissions.roles.contains(item.assignedRole)`

**Failure Scenarios:**
- Item not found → 404 Not Found
- User lacks role → 403 Forbidden
- Item not Pending → 409 Conflict
- Dismissal without note → 400 Bad Request
```

**TypeSpec Output:**
```typespec
@doc("Request to update a surveillance item's status")
model UpdateItemStatusRequest {
  @doc("ID of the item to update")
  itemId: ItemInstanceId;

  @doc("New status (CHECKED or DISMISSED)")
  newStatus: "CHECKED" | "DISMISSED";

  @doc("Resolution note (required for DISMISSED, optional for CHECKED)")
  note?: string;
}

@doc("Response after successfully updating item status")
model UpdateItemStatusResponse {
  itemId: ItemInstanceId;
  status: Status;
  resolvedAt: utcDateTime;
}

@error
model ItemNotFoundError {
  @statusCode statusCode: 404;
  error: "item_not_found";
  message: string;
}

@error
model ForbiddenError {
  @statusCode statusCode: 403;
  error: "forbidden";
  message: string;
}

@error
model ConflictError {
  @statusCode statusCode: 409;
  error: "conflict";
  message: string;
}

@route("/api/v1/items/{itemId}/status")
interface ItemStatusOperations {
  @put
  @doc("Update surveillance item status (mark as checked or dismissed)")
  updateStatus(
    @path itemId: ItemInstanceId,
    @body request: UpdateItemStatusRequest
  ): UpdateItemStatusResponse | ItemNotFoundError | ForbiddenError | ConflictError;
}
```

### 5. Queries to GET Endpoints

**FQBC Input (Section 5 - Inbound Queries):**
```markdown
#### GetItemsList

**Intent:** User views items assigned to their role(s)

{
  statusFilter: Status?
  itemTypeFilter: ItemTypeId?
  dateFrom: Date?
  dateTo: Date?
  sortBy: "createdAt" | "status" | "itemType"
  sortOrder: "asc" | "desc"
  page: Int
  pageSize: Int
}

**Response:**
{
  items: [...]
  totalCount: Int
  page: Int
  pageSize: Int
}
```

**TypeSpec Output:**
```typespec
@doc("Paginated list of surveillance items")
model ItemsListResponse {
  @doc("Items matching the query")
  items: ItemSummary[];

  @doc("Total count of matching items")
  totalCount: int32;

  @doc("Current page number")
  page: int32;

  @doc("Items per page")
  pageSize: int32;
}

model ItemSummary {
  id: ItemInstanceId;
  itemType: ItemTypeSummary;
  status: Status;
  createdAt: utcDateTime;
  sourceProcess: string;
  metadataSummary: string;
}

@route("/api/v1/items")
interface ItemsQueries {
  @get
  @doc("List surveillance items for authenticated user's roles")
  list(
    @query statusFilter?: Status,
    @query itemTypeFilter?: ItemTypeId,
    @query dateFrom?: plainDate,
    @query dateTo?: plainDate,
    @query sortBy?: "createdAt" | "status" | "itemType",
    @query sortOrder?: "asc" | "desc",
    @query page?: int32 = 1,
    @query pageSize?: int32 = 20,
  ): ItemsListResponse;

  @get
  @route("{itemId}")
  @doc("Get full details of a surveillance item")
  getDetails(@path itemId: ItemInstanceId): ItemInstance | ItemNotFoundError;
}
```

### 6. Domain Events to Event Schemas

**FQBC Input (Section 5 - Outbound Events):**
```markdown
#### ItemStatusChanged

**Trigger:** Status transition from Pending to Checked or Dismissed

{
  eventId: UUID
  eventType: "ITEM_STATUS_CHANGED"
  timestamp: Timestamp
  itemId: ItemInstanceId
  itemTypeName: String
  fromStatus: Status
  toStatus: Status
  changedBy: PersonId
  note: String?
}
```

**TypeSpec Output:**
```typespec
@doc("Event raised when a surveillance item's status changes")
model ItemStatusChangedEvent {
  @doc("Unique event identifier")
  eventId: string;

  @doc("Event type discriminator")
  eventType: "ITEM_STATUS_CHANGED";

  @doc("When the event occurred")
  timestamp: utcDateTime;

  @doc("Affected item")
  itemId: ItemInstanceId;

  @doc("Item type name for context")
  itemTypeName: string;

  @doc("Previous status")
  fromStatus: Status;

  @doc("New status")
  toStatus: Status;

  @doc("Who made the change")
  changedBy: PersonId;

  @doc("Resolution note if provided")
  note?: string;
}
```

### 7. Cross-Context Integration Contracts

**FQBC Input (Section 6 - Context Relationships):**
```markdown
### 5.3 Surveillance Items → Notification Delivery

**Pattern:** `Customer-Supplier`

| Aspect | Detail |
|--------|--------|
| **Query Interface** | `GetPendingItemsByRole()` → Map<RoleId, [PendingItemSummary]> |
```

**TypeSpec Output (internal API):**
```typespec
// internal/surveillance-items-internal.tsp
@doc("Internal API for Surveillance Items context - consumed by other contexts")
namespace SurveillanceItemsInternal;

model PendingItemSummary {
  id: ItemInstanceId;
  itemTypeName: string;
  createdAt: utcDateTime;
  metadataSummary: string;
}

model PendingItemsByRoleResponse {
  @doc("Pending items grouped by role ID")
  byRole: Record<PendingItemSummary[]>;
}

@route("/internal/surveillance-items")
interface InternalQueries {
  @get
  @route("pending-by-role")
  @doc("Get all pending items grouped by assigned role (for Notification Delivery)")
  getPendingItemsByRole(): PendingItemsByRoleResponse;
}
```

---

## Type Mapping Reference

| FQBC Type | TypeSpec Type | Notes |
|-----------|---------------|-------|
| UUID | `scalar X extends string` | Create custom scalar per domain ID |
| String | `string` | |
| Int | `int32` | |
| Long/Int64 | `int64` | |
| Decimal | `decimal` | |
| Boolean | `boolean` | |
| Timestamp | `utcDateTime` | ISO 8601 format |
| Date | `plainDate` | |
| Time | `plainTime` | |
| `X?` (optional) | `property?: Type` | |
| `List<X>` | `Type[]` | |
| `Map<K,V>` | `Record<V>` | Keys are always strings in HTTP |
| Enum | `enum X { ... }` | |

## Authorization Mapping

FQBC authorization rules map to OpenAPI security requirements:

| FQBC Authorization | TypeSpec Decorator |
|-------------------|-------------------|
| `permissions.roles.contains(X)` | `@useAuth(BearerAuth)` + document in `@doc` |
| `permissions.roles.containsAny(X, Y)` | `@useAuth(BearerAuth)` + document in `@doc` |
| System-to-system | Separate internal API namespace |

---

## Generation Process

1. **Read BCR manifest.json** → Identify contexts and phase status
2. **For each context in `fqbc_generation.contexts`:**
   - Parse FQBC markdown file
   - Extract Section 4 (Domain Model) → Generate models, enums, scalars
   - Extract Section 5 (Published Interface) → Generate endpoints
   - Extract Section 6 (Context Relationships) → Generate internal APIs
3. **Generate shared types** from context-map.md (Published Language)
4. **Compile TypeSpec** → Generate OpenAPI 3.0 specs
5. **Validate contracts** → Ensure all contexts' contracts are consistent

## File Output Structure

```
api/
├── main.tsp                    # Main entry point, imports all contexts
├── common/
│   └── types.tsp               # Shared types (PersonId, Permissions, etc.)
├── {context-name}/
│   ├── models.tsp              # Domain models for this context
│   ├── endpoints.tsp           # Public API endpoints
│   ├── events.tsp              # Domain event schemas
│   └── internal.tsp            # Internal API (if consumer of other contexts)
└── openapi/                    # Generated OpenAPI specs
    └── {context-name}.yaml
```
