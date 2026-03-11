# Authorization Patterns

## Input

From manifest and FQBC:
- Authorization pattern (currently only `permissions-object`)
- Permission requirements per operation (FQBC Section 5)
- Role definitions per context
- Permission check methods

## Output Files

Shared support infrastructure:
- `internal/support/auth/claims.go` - Claims type, constructor, role-check methods
- `internal/support/auth/permissions.go` - Permissions interface and errors
- `internal/support/auth/context.go` - `ClaimsContextKey` constant and `contextKey` type (extracted from Claims pattern block, lines 34-36)
- `internal/support/auth/jwt.go` - JWT signing and parsing using `github.com/golang-jwt/jwt/v5`

Per context:
- `internal/{context}/{context}application/permissions.go` - Context-specific permissions

HTTP middleware:
- `internal/adapters/driving/httpadapter/httpmiddleware/auth_middleware.go` - JWT extraction and Permissions building

Token generation tool:
- `cmd/gentoken/main.go` - CLI utility to mint JWTs for development and testing

## Patterns

### Claims Type (Support Layer)

```go
package auth

import "time"

// ClaimsContextKey is the context key for storing/retrieving claims
var ClaimsContextKey = contextKey("claims")

type contextKey string

// Claims represents the authenticated identity extracted from JWT
type Claims struct {
	Subject   string
	Issuer    string
	Email     string
	Roles     []string
	ExtraClaims map[string]string
	IssuedAt  time.Time
	ExpiresAt time.Time
}

// NewClaims creates a new Claims instance
func NewClaims(subject, issuer, email string, roles []string, extra map[string]string) (*Claims, error) {
	if subject == "" {
		return nil, NewAuthenticationError("subject is required")
	}
	return &Claims{
		Subject:     subject,
		Issuer:      issuer,
		Email:       email,
		Roles:       roles,
		ExtraClaims: extra,
		IssuedAt:    time.Now(),
	}, nil
}

// HasRole checks if the claims include a specific role
func (c *Claims) HasRole(role Role) bool {
	for _, r := range c.Roles {
		if r == string(role) {
			return true
		}
	}
	return false
}

// HasAnyRole checks if the claims include any of the specified roles
func (c *Claims) HasAnyRole(roles ...Role) bool {
	for _, role := range roles {
		if c.HasRole(role) {
			return true
		}
	}
	return false
}
```

### Permissions Interface (Support Layer)

```go
package auth

import "context"

// Permission represents a named capability
type Permission string

// Role represents a named role
type Role string

// Standard roles — each context may define additional context-specific roles
const (
	RoleAdmin    Role = "admin"
	RoleUser     Role = "user"
	RoleReadOnly Role = "readonly"
)

// ExtractClaims retrieves Claims from context
func ExtractClaims(ctx context.Context) (*Claims, error) {
	claims, ok := ctx.Value(ClaimsContextKey).(*Claims)
	if !ok || claims == nil {
		return nil, NewAuthenticationError("no valid claims in context")
	}
	return claims, nil
}

// AuthenticationError represents an authentication failure (401)
type AuthenticationError struct {
	Message string
}

func NewAuthenticationError(message string) AuthenticationError {
	return AuthenticationError{Message: message}
}

func (e AuthenticationError) Error() string {
	return "authentication failed: " + e.Message
}

// AuthorizationError represents an authorization failure (403)
type AuthorizationError struct {
	Message string
}

func NewAuthorizationError(message string) AuthorizationError {
	return AuthorizationError{Message: message}
}

func (e AuthorizationError) Error() string {
	return "authorization failed: " + e.Message
}
```

### Context-Specific Permissions (Application Layer)

Each context defines its own permissions and role-to-permission mappings. This file lives alongside the application service.

```go
package {context}application

import (
	"{module}/internal/support/auth"
)

// {Context}-specific permissions
const (
	Permission{Operation1} auth.Permission = "{context}.{operation1}"
	Permission{Operation2} auth.Permission = "{context}.{operation2}"
)

// {Context}-specific roles (supplement standard roles)
const (
	Role{ContextRole1} auth.Role = "{context}_{role1}"
	Role{ContextRole2} auth.Role = "{context}_{role2}"
)

// Require{Context}Permission checks if claims have the required permission for this context
func Require{Context}Permission(claims *auth.Claims, permission auth.Permission) error {
	if claims == nil {
		return auth.NewAuthorizationError("no claims present")
	}

	// Admin role has all permissions
	if claims.HasRole(auth.RoleAdmin) {
		return nil
	}

	// Check context-specific role-to-permission mapping
	switch permission {
	case Permission{Operation1}:
		if claims.HasAnyRole(Role{ContextRole1}, auth.RoleUser) {
			return nil
		}
	case Permission{Operation2}:
		if claims.HasAnyRole(Role{ContextRole2}) {
			return nil
		}
	}

	return auth.NewAuthorizationError("insufficient permissions for " + string(permission))
}
```

### JWT Signing and Parsing (Support Layer)

This package provides real JWT operations using `github.com/golang-jwt/jwt/v5`. The walking skeleton ships with a known dev secret (`dev-secret-change-me` from config) so tokens generated with the `gentoken` tool work immediately.

```go
package auth

import (
	"fmt"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

// jwtClaims maps JWT standard + custom claims
type jwtClaims struct {
	jwt.RegisteredClaims
	Email string   `json:"email,omitempty"`
	Roles []string `json:"roles"`
}

// GenerateToken creates a signed JWT with the given claims and secret
func GenerateToken(subject, issuer, email string, roles []string, secret []byte, ttl time.Duration) (string, error) {
	now := time.Now()
	claims := jwtClaims{
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   subject,
			Issuer:    issuer,
			IssuedAt:  jwt.NewNumericDate(now),
			ExpiresAt: jwt.NewNumericDate(now.Add(ttl)),
		},
		Email: email,
		Roles: roles,
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(secret)
}

// ParseToken validates a JWT string and returns Claims.
// It constructs Claims directly from the parsed JWT fields to preserve
// the token's original timestamps (IssuedAt, ExpiresAt).
func ParseToken(tokenString string, secret []byte) (*Claims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &jwtClaims{}, func(t *jwt.Token) (interface{}, error) {
		if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", t.Header["alg"])
		}
		return secret, nil
	})
	if err != nil {
		return nil, NewAuthenticationError("invalid token: " + err.Error())
	}

	jc, ok := token.Claims.(*jwtClaims)
	if !ok || !token.Valid {
		return nil, NewAuthenticationError("invalid token claims")
	}

	if jc.Subject == "" {
		return nil, NewAuthenticationError("subject is required")
	}

	claims := &Claims{
		Subject: jc.Subject,
		Issuer:  jc.Issuer,
		Email:   jc.Email,
		Roles:   jc.Roles,
	}
	if jc.IssuedAt != nil {
		claims.IssuedAt = jc.IssuedAt.Time
	}
	if jc.ExpiresAt != nil {
		claims.ExpiresAt = jc.ExpiresAt.Time
	}
	return claims, nil
}
```

### Token Generation Tool

A CLI utility for minting JWTs during development and testing. Developers use it to create tokens with specific roles to exercise all authorization paths.

```go
// cmd/gentoken/main.go
package main

import (
	"flag"
	"fmt"
	"os"
	"strings"
	"time"

	"{module}/internal/support/auth"
)

func main() {
	subject := flag.String("sub", "dev-user", "Token subject (user ID)")
	email := flag.String("email", "dev@localhost", "User email")
	roles := flag.String("roles", "admin", "Comma-separated roles")
	ttl := flag.Duration("ttl", 24*time.Hour, "Token time-to-live")
	secret := flag.String("secret", "", "JWT secret (default: JWT_SECRET env or dev-secret-change-me)")
	flag.Parse()

	jwtSecret := *secret
	if jwtSecret == "" {
		jwtSecret = os.Getenv("JWT_SECRET")
	}
	if jwtSecret == "" {
		jwtSecret = "dev-secret-change-me"
	}

	roleList := strings.Split(*roles, ",")
	token, err := auth.GenerateToken(*subject, "dev", *email, roleList, []byte(jwtSecret), *ttl)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		os.Exit(1)
	}

	fmt.Println(token)
}
```

Usage:
```bash
# Generate an admin token (default)
go run cmd/gentoken/main.go

# Generate a token with specific roles
go run cmd/gentoken/main.go -roles "user,supervisor" -email "test@example.com"

# Use with curl
TOKEN=$(go run cmd/gentoken/main.go -roles "admin")
curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/{context-slug}/v1/{resource}
```

### Auth Middleware (Driving Adapter Layer)

The middleware extracts JWT claims and attaches them to the request context. It does NOT resolve context-specific permissions — that happens in the application service.

```go
package httpmiddleware

import (
	"context"
	"net/http"
	"strings"

	"{module}/internal/support/auth"
)

// AuthMiddleware handles JWT extraction and claims propagation
type AuthMiddleware struct {
	jwtSecret []byte
}

// NewAuthMiddleware creates a new auth middleware
func NewAuthMiddleware(jwtSecret []byte) *AuthMiddleware {
	return &AuthMiddleware{jwtSecret: jwtSecret}
}

// RequireAuth wraps a handler to require valid authentication
func (m *AuthMiddleware) RequireAuth(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// Extract Bearer token from Authorization header
		authHeader := r.Header.Get("Authorization")
		if authHeader == "" || !strings.HasPrefix(authHeader, "Bearer ") {
			http.Error(w, `{"success":false,"error":{"code":"UNAUTHORIZED","message":"Missing or invalid Authorization header"}}`, http.StatusUnauthorized)
			return
		}
		token := strings.TrimPrefix(authHeader, "Bearer ")

		// Parse and validate JWT, extract claims
		claims, err := m.parseToken(token)
		if err != nil {
			http.Error(w, `{"success":false,"error":{"code":"UNAUTHORIZED","message":"Invalid or expired token"}}`, http.StatusUnauthorized)
			return
		}

		// Attach claims to request context — permission checks happen in application layer
		ctx := context.WithValue(r.Context(), auth.ClaimsContextKey, claims)
		next.ServeHTTP(w, r.WithContext(ctx))
	}
}

func (m *AuthMiddleware) parseToken(tokenString string) (*auth.Claims, error) {
	return auth.ParseToken(tokenString, m.jwtSecret)
}
```

## Authorization Flow Summary

```
HTTP Request
    │
    ▼
┌─────────────────────┐
│   Auth Middleware    │  1. Extract JWT from Authorization header
│   (driving adapter) │  2. Parse token → Claims
│                     │  3. Attach Claims to context
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   HTTP Handler      │  4. Decode request body
│   (driving adapter) │  5. Call primary port method
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   Application Svc   │  6. ExtractClaims(ctx)
│   (application)     │  7. Require{Context}Permission(claims, permission)
│                     │  8. Execute business logic if authorized
└─────────────────────┘
```

**Key principle**: Authentication (who you are) is resolved once in middleware. Authorization (what you can do) is checked per-operation in the application service using context-specific permission definitions.

## Guidelines

1. **Middleware resolves identity only** — it does NOT check permissions or roles
2. **Application service checks permissions** — using `Require{Context}Permission()`
3. **Each context owns its permissions** — no shared permission registry
4. **Admin bypass** — admin role always has all permissions (checked first)
5. **Error types distinguish 401 vs 403** — `AuthenticationError` (middleware) vs `AuthorizationError` (application)
6. **Test context** — mock applications create admin claims for test data population
