# API Design Conventions

Standard HTTP API conventions for use across all Bounded Contexts. Reference this document when generating API Binding sections in FQBC documents.

## URL Structure

### Base Path Format

```
/api/{context-slug}/v{version}/{resource}
```

| Component | Convention | Example |
|-----------|------------|---------|
| API prefix | `/api/` | Always present |
| Context slug | kebab-case | `surveillance-items`, `role-management` |
| Version | `v1`, `v2`, etc. | Per-context versioning |
| Resource | plural nouns | `items`, `roles`, `thresholds` |

### Why Context-First Versioning?

Each bounded context is autonomous and evolves independently. Placing the version *inside* the context path:

- **Enables independent evolution**: `surveillance-items` can move to v2 while `role-management` stays at v1
- **Aligns with DDD principles**: Each context owns its entire API surface, including versioning
- **Simplifies microservice routing**: All `/api/surveillance-items/*` traffic routes to one service
- **Follows industry patterns**: Google Cloud APIs, Stripe, and many microservice architectures use per-service versioning

### Context Slug Derivation

Convert context name to kebab-case:
- "Surveillance Items" → `surveillance-items`
- "Role Management" → `role-management`
- "Compliance Reporting" → `compliance-reporting`
- "Audit Trail" → `audit-trail`

### Resource Paths

| Pattern | Use Case | Example |
|---------|----------|---------|
| `/{resources}` | List/create | `GET /items`, `POST /items` |
| `/{resources}/{id}` | Get/update/delete single | `GET /items/{itemId}` |
| `/{resources}/{id}/{sub-resource}` | Nested resource | `GET /items/{itemId}/history` |
| `/{resources}/{id}/{action}` | Action on resource | `PATCH /items/{itemId}/status` |

### Internal Endpoints

For context-to-context communication:

```
/api/{context-slug}/v1/internal/{operation}
```

Internal endpoints are not exposed to external clients but follow the same conventions.

---

## HTTP Method Mapping

### Domain Operation to HTTP Method

| Domain Operation | HTTP Method | Success Status | Idempotent |
|------------------|-------------|----------------|------------|
| Query (list) | GET | 200 | Yes |
| Query (single) | GET | 200 | Yes |
| Command (create) | POST | 201 | No |
| Command (full update) | PUT | 200 | Yes |
| Command (partial update) | PATCH | 200 | Yes* |
| Command (delete) | DELETE | 204 | Yes |
| Command (action) | POST or PATCH | 200 | Depends |

*PATCH is idempotent when applying the same change repeatedly yields the same result.

### Method Selection Guidelines

**Use POST when:**
- Creating a new resource
- Triggering an action with side effects
- Operation is not idempotent

**Use PATCH when:**
- Updating specific fields of a resource
- Changing resource state (e.g., status transitions)
- Partial modification

**Use PUT when:**
- Replacing entire resource
- Client provides complete resource representation

---

## Query Parameters

### Standard Parameter Names

| Purpose | Parameter | Type | Default | Notes |
|---------|-----------|------|---------|-------|
| Pagination (offset) | `offset` | integer | 0 | 0-indexed item offset |
| Pagination (limit) | `limit` | integer | 20 | Max typically 100 |
| Date range start | `dateFrom` | string | — | ISO-8601 format |
| Date range end | `dateTo` | string | — | ISO-8601 format |
| Sort field | `sortBy` | string | varies | Field name |
| Sort direction | `sortOrder` | string | `desc` | `asc` or `desc` |

### Filter Parameters

| Pattern | Example | Notes |
|---------|---------|-------|
| Single value | `status=PENDING` | Exact match |
| Multiple values | `status=PENDING&status=CHECKED` | OR logic |
| Array syntax | `status[]=PENDING&status[]=CHECKED` | Alternative |
| Comma-separated | `status=PENDING,CHECKED` | Alternative |

**Recommendation**: Use repeated parameters (`status=A&status=B`) for array filters.

### Naming Convention

- Use camelCase: `offset`, `limit`, `sortBy`, `dateFrom`
- Match domain model field names where possible
- Avoid abbreviations unless universally understood

---

## Request Body Format

### Content Type

```
Content-Type: application/json
```

### Field Naming

- Use camelCase for all fields
- Match domain model terminology

### Example Request

```json
{
  "newStatus": "CHECKED",
  "note": "Reviewed and approved"
}
```

---

## Response Envelope

### Success Response

```json
{
  "success": true,
  "data": {
    // Response payload
  },
  "meta": {
    // Optional metadata (pagination, etc.)
  }
}
```

### Success with Pagination

```json
{
  "success": true,
  "data": {
    "items": [...],
    "totalCount": 150
  },
  "meta": {
    "next": "/api/{context-slug}/v1/{resource}?offset=20&limit=20",
    "previous": null
  }
}
```

### Success (Single Resource)

```json
{
  "success": true,
  "data": {
    "id": "uuid-here",
    "field": "value"
  }
}
```

### Success (No Content)

For DELETE operations, return 204 with no body.

---

## Error Response

### Format

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "details": {
      // Optional structured details
    }
  }
}
```

### Standard Error Codes

| HTTP Status | Error Code | When to Use |
|-------------|------------|-------------|
| 400 | `VALIDATION_ERROR` | Request body validation failed |
| 400 | `INVALID_PARAMETER` | Query parameter invalid |
| 400 | `MISSING_REQUIRED_FIELD` | Required field not provided |
| 401 | `UNAUTHORIZED` | No valid authentication |
| 403 | `FORBIDDEN` | Authenticated but not authorized |
| 403 | `INSUFFICIENT_ROLE` | Missing required role |
| 404 | `NOT_FOUND` | Resource doesn't exist |
| 404 | `{RESOURCE}_NOT_FOUND` | Specific resource not found |
| 409 | `CONFLICT` | State conflict (e.g., already processed) |
| 409 | `INVALID_STATE_TRANSITION` | Invalid status change |
| 422 | `BUSINESS_RULE_VIOLATION` | Domain rule prevented operation |

### Error with Validation Details

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "fields": [
        { "field": "note", "message": "Note is required when dismissing" }
      ]
    }
  }
}
```

---

## Authentication & Authorization

### Authentication Header

```
Authorization: Bearer <jwt-token>
```

### Authorization Errors

- **401 Unauthorized**: Token missing, expired, or invalid
- **403 Forbidden**: Valid token but insufficient permissions

### Documenting Authorization

In API Binding, specify required roles:

```markdown
**Authorization**: `permissions.hasRole('ATSSupervisor')`
```

---

## Pagination

### Strategy: Offset Pagination

Offset pagination uses `offset` (number of items to skip) and `limit` (number of items to return). Responses include `next` and `previous` navigation URLs as relative paths so frontends can follow them directly without computing offsets.

### Request

```
GET /api/surveillance-items/v1/items?offset=40&limit=20
```

### Response

```json
{
  "success": true,
  "data": {
    "items": [...],
    "totalCount": 237
  },
  "meta": {
    "next": "/api/surveillance-items/v1/items?offset=60&limit=20",
    "previous": "/api/surveillance-items/v1/items?offset=20&limit=20"
  }
}
```

### Navigation URLs

| Field | Type | Description |
|-------|------|-------------|
| `next` | string \| null | Relative path for the next page, or `null` if on last page |
| `previous` | string \| null | Relative path for the previous page, or `null` if on first page |

Navigation URLs preserve any filters and sort parameters from the original request. For example:

```
GET /api/surveillance-items/v1/items?status=PENDING&offset=20&limit=20
```

Returns:
```json
"next": "/api/surveillance-items/v1/items?status=PENDING&offset=40&limit=20",
"previous": "/api/surveillance-items/v1/items?status=PENDING&offset=0&limit=20"
```

### Constraints

| Parameter | Min | Max | Default |
|-----------|-----|-----|---------|
| offset | 0 | — | 0 |
| limit | 1 | 100 | 20 |

---

## Date/Time Format

### Standard: ISO-8601

All dates and timestamps use ISO-8601 format:

| Type | Format | Example |
|------|--------|---------|
| Date only | `YYYY-MM-DD` | `2026-01-21` |
| Timestamp | `YYYY-MM-DDTHH:mm:ssZ` | `2026-01-21T14:30:00Z` |
| With offset | `YYYY-MM-DDTHH:mm:ss±HH:mm` | `2026-01-21T14:30:00+00:00` |

### In Query Parameters

```
GET /items?dateFrom=2026-01-01&dateTo=2026-01-31
```

### In Response Bodies

```json
{
  "createdAt": "2026-01-21T14:30:00Z",
  "resolvedAt": "2026-01-21T15:45:30Z"
}
```

---

## Versioning Strategy

### URL Path Versioning (Per-Context)

```
/api/{context-slug}/v1/...
/api/{context-slug}/v2/...
```

Version is scoped per context, enabling independent evolution of each bounded context's API.

### Version Increment Guidelines

| Change Type | Version Impact |
|-------------|----------------|
| New endpoint | None (additive) |
| New optional field | None (additive) |
| New required field | Major version |
| Remove field | Major version |
| Change field type | Major version |
| Change URL structure | Major version |

---

## Summary Checklist

When defining API bindings, verify:

- [ ] Base path follows `/api/{context-slug}/v1/` pattern
- [ ] HTTP methods match operation semantics
- [ ] Query parameters use standard names (offset, limit, dateFrom, etc.)
- [ ] Request/response bodies use camelCase
- [ ] Response envelope includes `success` and `data`/`error`
- [ ] Error responses include `code` and `message`
- [ ] Dates use ISO-8601 format
- [ ] Authorization requirements documented
- [ ] Pagination follows standard pattern
