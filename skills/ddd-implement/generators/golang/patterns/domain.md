# Domain Layer Patterns

## Input

From manifest and BCR:
- Context name
- Entities (name, properties, isAggregateRoot, idType)
- Value objects (name, properties, validation rules)
- Domain events (name, payload properties)

## Output Files

For each context:
- `internal/{context}/{context}domain/{entity_snake}.go` - Entity definitions
- `internal/{context}/{context}domain/{value_object_snake}.go` - Value objects (if standalone)
- `internal/{context}/{context}domain/events.go` - Domain events
- `internal/{context}/{context}domain/errors.go` - Domain errors

## Patterns

### Entity ID Pattern

```go
package {context}domain

import "github.com/google/uuid"

// {EntityId} uniquely identifies a {Entity}
type {EntityId} struct {
	uuid.UUID
}

// New{EntityId} creates a new unique identifier
func New{EntityId}() {EntityId} {
	return {EntityId}{UUID: uuid.New()}
}

// {EntityId}FromString parses a string into a {EntityId}
func {EntityId}FromString(s string) ({EntityId}, error) {
	id, err := uuid.Parse(s)
	if err != nil {
		return {EntityId}{}, NewDomainValidationError("invalid {entity} ID format", err)
	}
	return {EntityId}{UUID: id}, nil
}

// String returns the string representation
func (id {EntityId}) String() string {
	return id.UUID.String()
}
```

### Aggregate Root Pattern

```go
package {context}domain

import (
	"{module}/internal/support/basedomain"
	"{module}/internal/support/validation"
	"time"
)

// {Entity} represents {entity_description}
// This is the main aggregate root for the {Context} Context
type {Entity} struct {
	basedomain.BaseEntity[{EntityId}] `json:",inline"`

	// The {entity}'s data and current state
	Data {Entity}Data `json:"data"`
}

// {Entity}Data represents the value object containing {entity}'s business data
type {Entity}Data struct {
	{{range .Properties}}
	{PropertyName} {PropertyType} `json:"{json_name}" validate:"{validation_tags}"`
	{{end}}
}

// New{Entity} creates a new {Entity} aggregate with validation
func New{Entity}({{constructor_params}}) ({Entity}, error) {
	id := New{EntityId}()

	data := {Entity}Data{
		{{range .Properties}}
		{PropertyName}: {param_name},
		{{end}}
	}

	if err := validation.Validate(data); err != nil {
		return {Entity}{}, NewDomainValidationError("{entity} validation failed", err)
	}

	entity := {Entity}{
		BaseEntity: basedomain.NewBaseEntity(id),
		Data:       data,
	}

	// Raise domain event for creation
	entity.AddEvent(New{Entity}CreatedEvent(id, data))

	return entity, nil
}

// New{Entity}FromExisting creates an entity from existing data (for repository loading)
func New{Entity}FromExisting(id {EntityId}, data {Entity}Data) ({Entity}, error) {
	if err := validation.Validate(data); err != nil {
		return {Entity}{}, NewDomainValidationError("{entity} validation failed", err)
	}

	return {Entity}{
		BaseEntity: basedomain.NewBaseEntity(id),
		Data:       data,
	}, nil
}

// Get{EntityId} returns the entity's identifier
func (e {Entity}) Get{EntityId}() {EntityId} {
	return e.Id
}

{{range .Properties}}
// Get{PropertyName} returns the {property_description}
func (e {Entity}) Get{PropertyName}() {PropertyType} {
	return e.Data.{PropertyName}
}
{{end}}

// Domain behavior methods go here
// Example:
// func (e *{Entity}) DoSomething(params) error {
//     // Business logic
//     // Raise events
//     e.AddEvent(NewSomethingHappenedEvent(...))
//     return nil
// }
```

### Value Object Pattern

```go
package {context}domain

import (
	"{module}/internal/support/validation"
)

// {ValueObject} represents {value_object_description}
type {ValueObject} struct {
	{{range .Properties}}
	{PropertyName} {PropertyType} `json:"{json_name}" validate:"{validation_tags}"`
	{{end}}
}

// New{ValueObject} creates a validated {ValueObject}
func New{ValueObject}({{constructor_params}}) ({ValueObject}, error) {
	vo := {ValueObject}{
		{{range .Properties}}
		{PropertyName}: {param_name},
		{{end}}
	}

	if err := validation.Validate(vo); err != nil {
		return {ValueObject}{}, NewDomainValidationError("{value_object} validation failed", err)
	}

	{{if .CustomValidation}}
	// Custom business rule validation
	{custom_validation_code}
	{{end}}

	return vo, nil
}
```

### Domain Event Pattern

```go
package {context}domain

import "time"

// {EventName}Event is raised when {event_description}
type {EventName}Event struct {
	{{range .PayloadProperties}}
	{PropertyName} {PropertyType} `json:"{json_name}"`
	{{end}}
	occurredAt time.Time
}

// New{EventName}Event creates a new {EventName} event
func New{EventName}Event({{constructor_params}}) {EventName}Event {
	return {EventName}Event{
		{{range .PayloadProperties}}
		{PropertyName}: {param_name},
		{{end}}
		occurredAt: time.Now(),
	}
}

// EventName returns the event type identifier
func (e {EventName}Event) EventName() string {
	return "{context}.{event_name_snake}"
}

// OccurredAt returns when the event happened
func (e {EventName}Event) OccurredAt() time.Time {
	return e.occurredAt
}
```

### Domain Errors Pattern

```go
package {context}domain

import "fmt"

// DomainValidationError represents a validation error in the domain
type DomainValidationError struct {
	Message string
	Cause   error
}

func NewDomainValidationError(message string, cause error) DomainValidationError {
	return DomainValidationError{
		Message: message,
		Cause:   cause,
	}
}

func (e DomainValidationError) Error() string {
	if e.Cause != nil {
		return fmt.Sprintf("%s: %v", e.Message, e.Cause)
	}
	return e.Message
}

func (e DomainValidationError) Unwrap() error {
	return e.Cause
}

// DomainError represents a general domain error
type DomainError struct {
	Code    string
	Message string
}

func NewDomainError(code, message string) DomainError {
	return DomainError{
		Code:    code,
		Message: message,
	}
}

func (e DomainError) Error() string {
	return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}
```

## Type Mapping

| BCR Type | Go Type |
|----------|---------|
| string | `string` |
| int | `int` |
| int32 | `int32` |
| int64 | `int64` |
| float | `float64` |
| boolean | `bool` |
| datetime | `time.Time` |
| uuid | Custom ID type embedding `uuid.UUID` |
| optional<T> | `*T` (pointer) |
| list<T> | `[]T` |
| map<K,V> | `map[K]V` |

## Validation Tag Mapping

| BCR Validation | Go Validator Tag |
|----------------|------------------|
| required | `validate:"required"` |
| min_length(n) | `validate:"min=n"` |
| max_length(n) | `validate:"max=n"` |
| min_value(n) | `validate:"gte=n"` |
| max_value(n) | `validate:"lte=n"` |
| pattern(regex) | `validate:"regexp=regex"` |
| email | `validate:"email"` |
| url | `validate:"url"` |
| oneof(a,b,c) | `validate:"oneof=a b c"` |
