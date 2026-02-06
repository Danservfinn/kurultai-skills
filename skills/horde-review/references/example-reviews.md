# Example Critical Reviews

This file contains example critical review reports to demonstrate expected output quality and structure.

---

## Example 1: Authentication Form (Simple Component)

# Critical Review Report: Authentication Form Design

## Executive Summary
Basic authentication form design with minimal specification. Lacks critical security features, accessibility considerations, error handling, and user experience enhancements. Requires significant additions before production use.

## Findings by Domain

### User Experience & Accessibility
- **Missing labels** (Line: "Email input field") - Inputs need proper `<label>` elements with `for` attributes for screen reader accessibility
- **No password visibility toggle** - Users cannot verify password entry, causing frustration and errors
- **Missing form validation feedback** - No inline validation for email format or password strength
- **No error message display area** - Users won't see authentication failures clearly
- **"Forgot password" link placement unclear** - Should be near password field, not at bottom
- **No loading state indication** - Users may click login multiple times during processing
- **Missing keyboard navigation support** - Ensure proper tab order and Enter key submission

### Backend & API Design
- **No rate limiting specified** (Security: Critical) - Vulnerable to brute force attacks on email/password combinations
- **No mention of password hashing** - Must use bcrypt/argon2 with proper work factor
- **"Remember me" security unclear** - Needs secure token strategy (not just extending session)
- **No account lockout mechanism** - Should lock after failed attempts
- **Missing CSRF protection** - Login forms require CSRF tokens
- **No timing attack mitigation** - Use constant-time comparison for password verification
- **Forgot password flow unspecified** - Needs secure token-based reset mechanism

### Frontend & Implementation
- **No component structure defined** - Need atomic design or component hierarchy
- **State management unclear** - How are form state, loading, and errors managed?
- **No form validation strategy** - Client-side vs server-side validation approach
- **Missing input types** - Should use `type="email"` and `type="password"` with `autocomplete` attributes
- **No aria-describedby for errors** - Accessibility requires linking error messages to inputs
- **Missing submit prevention** - Should disable button during submission to prevent double-submit

### Architecture & System Design
- **No authentication protocol specified** - Session-based? JWT? OAuth?
- **Missing session management strategy** - Cookie configuration, expiration, refresh
- **No integration with larger auth system** - How does this fit with user registration, profile, logout?
- **Scalability not addressed** - How does this handle concurrent logins?
- **Missing multi-factor authentication** - No consideration for 2FA/MFA
- **No audit logging** - Authentication events should be logged for security monitoring

### Infrastructure & DevOps
- **No monitoring specified** - Failed login attempts, latency, error rates
- **Missing alerting** - Suspicious activity thresholds not defined
- **No secrets management** - Where are JWT secrets, pepper, API keys stored?
- **Deployment considerations missing** - Feature flags for auth changes, blue/green deployment

## Cross-Cutting Concerns
- **Security addressed by 3 domains** - Backend (CSRF, rate limiting), Architecture (auth protocol), DevOps (secrets management) - all highlight incomplete security design
- **Error handling missing across domains** - UX (no error display), Frontend (no error state), Backend (no error response format specified)

## Prioritized Improvement List

| Priority | Domain | Issue | Suggested Action |
|----------|--------|-------|------------------|
| Critical | Security | No rate limiting | Implement exponential backoff rate limiter (5/minute, then lock) |
| Critical | Security | Password handling unclear | Specify bcrypt/argon2 with work factor ≥12 |
| Critical | Security | Missing CSRF protection | Add CSRF token to form and server validation |
| Critical | Security | No timing attack mitigation | Use constant-time string comparison |
| High | UX | No inline validation | Add real-time email format and password strength feedback |
| High | UX | Missing error display | Add error message area with aria-live region |
| High | Accessibility | No proper labels | Add `<label>` elements with `for` attributes |
| High | Accessibility | No password toggle | Add visibility toggle button |
| High | Frontend | No loading states | Add spinner and disable button during submission |
| Medium | Architecture | Auth protocol unspecified | Choose session/JWT approach and document |
| Medium | Architecture | No 2FA consideration | Design for future TOTP/SMS 2FA integration |
| Medium | Backend | "Remember me" insecure | Design secure persistent token strategy |
| Medium | DevOps | No monitoring | Add auth success/failure metrics |
| Low | UX | Forgot password placement | Move link near password field |

---

## Example 2: REST API Design

# Critical Review Report: User Profile API

## Executive Summary
RESTful API design for user profile CRUD operations. Generally follows REST conventions but lacks pagination, filtering, validation specifications, rate limiting, and comprehensive error handling. Not production-ready without security and observability additions.

## Findings by Domain

### Backend & API Design
- **GET /users/{id} returns 404 for non-existent users** - Should use 404, but document whether this leaks user existence (enumeration attack)
- **No pagination on GET /users** - Will break with large datasets; add `?page=1&limit=50`
- **No filtering/sorting on list endpoint** - Clients must fetch all users; add `?filter=status:active&sort=created_at`
- **Missing request validation spec** - No OpenAPI/Swagger schema for request bodies
- **No rate limiting** (Security: High) - Endpoints vulnerable to abuse
- **PUT vs PATCH unclear** - Document whether PUT replaces entire resource or PATCH does partial updates
- **No ETag/Last-Modified headers** - Cannot implement conditional requests for caching

### Frontend & Implementation
- **No pagination metadata structure** - Frontend cannot build pagination UI without knowing total pages/counts
- **Error response format inconsistent** - Specify consistent error structure: `{ "error": { "code": "VALIDATION_ERROR", "message": "...", "details": [...] } }`
- **No loading states guidance** - Frontend should show skeleton during API calls

### Architecture & System Design
- **No versioning strategy** - Use `/v1/users` to allow breaking changes
- **Missing HATEOAS considerations** - No hypermedia links for navigation (if REST purist approach desired)
- **No bulk operations** - Consider `POST /users/bulk` for multiple creates
- **No relationship endpoints** - How to fetch user's posts? `/users/{id}/posts` or separate `/posts?userId={id}`?

### Security & Performance
- **No authentication requirement specified** - Which endpoints require auth? All? Public list?
- **No authorization checks mentioned** - Can user A update user B's profile?
- **No CORS configuration** - Document allowed origins for frontend integration
- **No query result limits** - Database could return millions of rows; enforce max page size
- **No indexing guidance** - Ensure email, username, created_at are indexed

### Infrastructure & DevOps
- **No observability** - Add structured logging, metrics (latency, error rate, request count)
- **No circuit breaker pattern** - Downstream service failures could cascade
- **No API documentation** - Include OpenAPI/Swagger spec in repo

## Cross-Cutting Concerns
- **Security gaps across Backend + Architecture** - No auth/authorization specified at either layer
- **Performance scalability** - Backend (no pagination), Architecture (no bulk ops), Infrastructure (no circuit breaker) all indicate scaling issues

## Prioritized Improvement List

| Priority | Domain | Issue | Suggested Action |
|----------|--------|-------|------------------|
| Critical | Security | No authentication specified | Document auth requirement (Bearer JWT) for all endpoints |
| Critical | Security | No authorization checks | Specify that users can only modify their own resources |
| High | Backend | No pagination | Add `?page` and `?limit` query parameters with metadata response |
| High | Backend | No validation spec | Create OpenAPI 3.0 schema for all request/response bodies |
| High | Performance | No max result limit | Enforce max page size of 100; default to 20 |
| High | Architecture | No API versioning | Add `/v1/` prefix to all routes |
| Medium | Backend | No filtering/sorting | Add `?filter=` and `?sort=` support |
| Medium | Frontend | Error format inconsistent | Specify standard error JSON structure |
| Medium | DevOps | No observability | Add request logging and Prometheus metrics |
| Low | Architecture | No bulk operations | Add `POST /v1/users/bulk` endpoint |
| Low | Backend | No ETag support | Add ETag header for conditional requests |

---

## Example 3: Minimal Artifact (All Clear)

# Critical Review Report: Simple Counter Component

## Executive Summary
Simple React counter component with useState hook. Well-implemented for its scope. No critical issues. Minor suggestions for accessibility and extensibility.

## Findings by Domain

### Frontend & Implementation
- **Missing aria-label on increment/decrement buttons** - Add `aria-label="Increment"` and `aria-label="Decrement"` for screen readers
- **Hardcoded initial value of 0** - Consider accepting `initialValue` prop for reusability

## Prioritized Improvement List

| Priority | Domain | Issue | Suggested Action |
|----------|--------|-------|------------------|
| Low | Frontend | Missing aria-labels | Add aria-label to buttons for screen reader announcement |
| Low | Frontend | Hardcoded initial value | Accept `initialValue` prop for flexibility |
