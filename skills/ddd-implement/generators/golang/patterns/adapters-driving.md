# Driving Adapter Patterns

> **FQBC-First**: HTTP adapters are generated directly from FQBC definitions and primary port interfaces.
> TypeSpec is generated separately as a documentation artifact (OpenAPI specs, client libraries).
> DTOs, handlers, and routes should conform to the FQBC API Binding (Section 7) and Context Contract (Section 6).
> See `api-conventions.md` for project-wide HTTP conventions that FQBC bindings follow.

## Output Files

- `internal/adapters/driving/httpadapter/dto.go`
- `internal/adapters/driving/httpadapter/handlers.go`
- `internal/adapters/driving/httpadapter/internal_handlers.go` (if internal endpoints exist)
- `internal/adapters/driving/httpadapter/routes.go`
- `internal/adapters/driving/httpadapter/httpmiddleware/auth_middleware.go`

---

## HTTP Handler Pattern

```go
package httpadapter

import (
	"encoding/json"
	"net/http"

	"{module}/internal/{context}/ports/{context}primary"
	"{module}/internal/{context}/{context}domain"
	"{module}/internal/support/auth"
	supporterrors "{module}/internal/support/errors"
	"{module}/internal/support/validation"
)

// Handler is the main HTTP handler
type Handler struct {
	{context}Service {context}primary.{Context}Service
}

// NewHandler creates a new HTTP handler
func NewHandler({context}Service {context}primary.{Context}Service) *Handler {
	return &Handler{
		{context}Service: {context}Service,
	}
}

// {Operation}Handler handles {operation} requests
func (h *Handler) {Operation}Handler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	// Parse request body
	var req {Operation}Request
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.writeErrorResponse(w, "INVALID_REQUEST", "Invalid JSON format", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	// Validate request
	if err := validation.Validate(req); err != nil {
		h.writeErrorResponse(w, "VALIDATION_ERROR", err.Error(), http.StatusBadRequest)
		return
	}

	// Call service
	result, err := h.{context}Service.{Operation}(r.Context(), req.{Params}...)
	if err != nil {
		h.handleServiceError(w, err)
		return
	}

	// Return response
	response := {Operation}ToResponse(result)
	w.WriteHeader(http.StatusOK) // or http.StatusCreated for POST
	json.NewEncoder(w).Encode(SuccessResponse{
		Success: true,
		Data:    response,
	})
}

// handleServiceError maps domain and auth errors to appropriate HTTP responses
func (h *Handler) handleServiceError(w http.ResponseWriter, err error) {
	switch e := err.(type) {
	case auth.AuthenticationError:
		h.writeErrorResponse(w, "UNAUTHORIZED", e.Error(), http.StatusUnauthorized)
	case auth.AuthorizationError:
		h.writeErrorResponse(w, "INSUFFICIENT_ROLE", e.Error(), http.StatusForbidden)
	case {context}domain.DomainValidationError:
		h.writeErrorResponse(w, "VALIDATION_ERROR", e.Error(), http.StatusUnprocessableEntity)
	default:
		status := supporterrors.HTTPStatusCode(err)
		h.writeErrorResponse(w, "INTERNAL_ERROR", err.Error(), status)
	}
}

func (h *Handler) writeErrorResponse(w http.ResponseWriter, errorCode, message string, httpStatus int) {
	w.WriteHeader(httpStatus)
	json.NewEncoder(w).Encode(ErrorResponse{
		Success: false,
		Error: ErrorDetail{
			Code:    errorCode,
			Message: message,
		},
	})
}

func (h *Handler) writeValidationErrorResponse(w http.ResponseWriter, message string, fields []FieldError) {
	w.WriteHeader(http.StatusBadRequest)
	json.NewEncoder(w).Encode(ErrorResponse{
		Success: false,
		Error: ErrorDetail{
			Code:    "VALIDATION_ERROR",
			Message: message,
			Details: map[string]interface{}{"fields": fields},
		},
	})
}

// FieldError represents a single field validation failure
type FieldError struct {
	Field   string `json:"field"`
	Message string `json:"message"`
}
```

## List Handler Pattern (Paginated Query)

When a context exposes a paginated list endpoint (per FQBC API Binding), generate this handler alongside the standard command handler above. It reads query parameters instead of a JSON body and builds the paginated response envelope per api-conventions.md.

```go
// List{Entities}Handler handles paginated list requests
func (h *Handler) List{Entities}Handler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	// Parse query parameters
	offset, limit := parsePaginationParams(r)

	// Call service
	result, err := h.{context}Service.List{Entities}(r.Context(), {context}domain.ListQuery{
		Offset: offset,
		Limit:  limit,
	})
	if err != nil {
		h.handleServiceError(w, err)
		return
	}

	// Build response items
	items := make([]{Entity}Response, len(result.Items))
	for i, entity := range result.Items {
		items[i] = {Entity}ToResponse(entity)
	}

	// Build pagination links
	meta := buildPaginationMeta(r, offset, limit, result.TotalCount)

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(SuccessResponse{
		Success: true,
		Data: map[string]interface{}{
			"items":      items,
			"totalCount": result.TotalCount,
		},
		Meta: meta,
	})
}

// parsePaginationParams extracts offset and limit from query string with defaults
func parsePaginationParams(r *http.Request) (offset, limit int) {
	offset = 0
	limit = 20 // default per api-conventions.md

	if v := r.URL.Query().Get("offset"); v != "" {
		if parsed, err := strconv.Atoi(v); err == nil && parsed >= 0 {
			offset = parsed
		}
	}
	if v := r.URL.Query().Get("limit"); v != "" {
		if parsed, err := strconv.Atoi(v); err == nil && parsed >= 1 && parsed <= 100 {
			limit = parsed
		}
	}
	return
}

// buildPaginationMeta builds next/previous links preserving existing query parameters
func buildPaginationMeta(r *http.Request, offset, limit, totalCount int) *Meta {
	meta := &Meta{}
	basePath := r.URL.Path
	query := r.URL.Query()

	if offset+limit < totalCount {
		query.Set("offset", strconv.Itoa(offset+limit))
		query.Set("limit", strconv.Itoa(limit))
		next := basePath + "?" + query.Encode()
		meta.Next = &next
	}
	if offset > 0 {
		prevOffset := offset - limit
		if prevOffset < 0 {
			prevOffset = 0
		}
		query.Set("offset", strconv.Itoa(prevOffset))
		query.Set("limit", strconv.Itoa(limit))
		previous := basePath + "?" + query.Encode()
		meta.Previous = &previous
	}
	return meta
}
```

**Note**: Add `"strconv"` to the import block when generating list handlers.

## Request/Response Types (DTO) Pattern

These types live in the HTTP adapter layer and translate between HTTP payloads and domain types. The FQBC uses "Payload" and "Response" in domain terms; the adapter layer names them `{Operation}Request` and `{Entity}Response`. The file is named `dto.go` by convention.

```go
package httpadapter

import (
	"time"

	"{module}/internal/{context}/{context}domain"
)

// {Operation}Request represents the request payload
type {Operation}Request struct {
	{{range .RequestFields}}
	{FieldName} {FieldType} `json:"{json_name}" validate:"{validation_tags}"`
	{{end}}
}

// {Entity}Response represents the response payload
type {Entity}Response struct {
	{{range .ResponseFields}}
	{FieldName} {FieldType} `json:"{json_name}{{if .OmitEmpty}},omitempty{{end}}"`
	{{end}}
}

// SuccessResponse wraps successful responses per api-conventions.md envelope
type SuccessResponse struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data"`
	Meta    *Meta       `json:"meta,omitempty"`
}

// Meta holds response metadata (pagination links, etc.)
type Meta struct {
	Next     *string `json:"next"`
	Previous *string `json:"previous"`
}

// ErrorDetail represents the nested error object in error responses
type ErrorDetail struct {
	Code    string      `json:"code"`
	Message string      `json:"message"`
	Details interface{} `json:"details,omitempty"`
}

// ErrorResponse wraps error responses per api-conventions.md envelope
type ErrorResponse struct {
	Success bool        `json:"success"`
	Error   ErrorDetail `json:"error"`
}

// {Entity}ToResponse converts domain entity to response DTO
func {Entity}ToResponse(entity {context}domain.{Entity}) {Entity}Response {
	return {Entity}Response{
		{{range .FieldMappings}}
		{ResponseField}: entity.{DomainGetter}(),
		{{end}}
	}
}

// RequestTo{DomainInput} converts request DTO to domain input type
func RequestTo{DomainInput}(req {Operation}Request) {context}domain.{DomainInput} {
	return {context}domain.{DomainInput}{
		{{range .FieldMappings}}
		{DomainField}: req.{RequestField},
		{{end}}
	}
}
```

## Routes Pattern

```go
package httpadapter

import (
	"net/http"

	"{module}/internal/adapters/driving/httpadapter/httpmiddleware"
)

// RegisterRoutes registers all HTTP routes
func (h *Handler) RegisterRoutes(mux *http.ServeMux, authMiddleware *httpmiddleware.AuthMiddleware) {
	// Public endpoints
	mux.HandleFunc("GET /health", h.HealthHandler)
	mux.HandleFunc("GET /info", h.InfoHandler)

	// Protected endpoints - {Context}
	// Base path follows api-conventions.md: /api/{context-slug}/v1/{resource}
	mux.HandleFunc("POST /api/{context-slug}/v1/{entities}", authMiddleware.RequireAuth(h.Create{Entity}Handler))
	mux.HandleFunc("GET /api/{context-slug}/v1/{entities}", authMiddleware.RequireAuth(h.List{Entities}Handler))
	mux.HandleFunc("GET /api/{context-slug}/v1/{entities}/{id}", authMiddleware.RequireAuth(h.Get{Entity}Handler))
	mux.HandleFunc("PUT /api/{context-slug}/v1/{entities}/{id}", authMiddleware.RequireAuth(h.Update{Entity}Handler))
	mux.HandleFunc("DELETE /api/{context-slug}/v1/{entities}/{id}", authMiddleware.RequireAuth(h.Delete{Entity}Handler))
}
```

## Internal Endpoint Handlers

Internal endpoints follow the same handler pattern as public endpoints but live in a separate file (`internal_handlers.go`). Only generate this file when the FQBC API Binding defines internal endpoints.

Differences from public handlers:
1. Registered under `/api/{context-slug}/v1/internal/{operation}` path prefix (per api-conventions.md)
2. Not included in TypeSpec/OpenAPI generation
3. Used for context-to-context synchronous communication

```go
// internal_handlers.go
package httpadapter

import (
	"encoding/json"
	"net/http"
)

// {InternalOperation}Handler handles internal {operation} requests from other contexts
func (h *Handler) {InternalOperation}Handler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	var req {InternalOperation}Request
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.writeErrorResponse(w, "INVALID_REQUEST", "Invalid JSON format", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	result, err := h.{context}Service.{InternalOperation}(r.Context(), req.{Params}...)
	if err != nil {
		h.handleServiceError(w, err)
		return
	}

	response := {InternalOperation}ToResponse(result)
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(SuccessResponse{
		Success: true,
		Data:    response,
	})
}
```

Route registration in `routes.go`:

```go
	// Internal routes (not documented in OpenAPI)
	mux.HandleFunc("{METHOD} /api/{context-slug}/v1/internal/{path}", authMiddleware.RequireAuth(h.{InternalOperation}Handler))
```
