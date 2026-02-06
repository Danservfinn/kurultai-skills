# Domain-Specialist Routing

Use task type detection to route spec compliance reviews to appropriate specialist agents instead of generic reviewers.

## Task Type Detection

Before dispatching spec compliance reviewers, analyze the task description for keywords that indicate domain.

## Keyword → Specialist Mapping

| Keywords in Task | Domain | Specialist Agent |
|------------------|--------|------------------|
| API, endpoint, route, controller, backend, database, schema, migration, Prisma, SQL | **Backend** | `backend-development:backend-architect` |
| component, frontend, React, Vue, Next.js, page, ARIA, WCAG, accessibility | **Frontend** | `frontend-mobile-development:frontend-developer` |
| Docker, Kubernetes, Terraform, AWS, GCP, infrastructure, CI/CD, deployment, pipeline | **DevOps** | `senior-devops` |
| ETL, ELT, data pipeline, warehouse, analytics, transformation | **Data Engineering** | `senior-data-engineer` |
| ML, machine learning, inference, prediction, neural network, training, classifier | **Data Science** | `senior-data-scientist` |
| architecture, scalability, integration pattern, system design | **Architecture** | `senior-architect` |
| security, authentication, authorization, encryption, vulnerability, OWASP | **Security** | `security-auditor` (or conduct security-focused analysis) |

**Important:** Use word boundary matching when detecting keywords. Avoid single letters that appear as substrings:
- "component" not "UI" (avoids matching "ui" in "build")
- "frontend" not "end" (avoids matching in "dep**end**")
- Check for whole words, not substrings

## Enhanced Spec Review Dispatch

### Default (Generic)

For tasks without clear domain keywords, use generic `general-purpose` agent as defined in `spec-reviewer-prompt.md`.

### Backend Tasks

```
Task tool (backend-development:backend-architect):
  description: "Review backend spec compliance for Task N"
  prompt: |
    You are reviewing whether a backend implementation matches its specification
    from a backend architecture perspective.

    [Use template from spec-reviewer-prompt.md, adding:]

    **Backend-specific concerns:**
    - API design (RESTful principles, proper HTTP methods, status codes)
    - Data modeling (normalization, relationships, indexing)
    - Error handling (proper error types, user-safe messages)
    - Security (input validation, SQL injection prevention)
    - Performance (N+1 queries, efficient joins, caching)
```

### Frontend Tasks

```
Task tool (frontend-mobile-development:frontend-developer):
  description: "Review frontend spec compliance for Task N"
  prompt: |
    You are reviewing whether a frontend implementation matches its specification
    from a frontend development perspective.

    [Use template from spec-reviewer-prompt.md, adding:]

    **Frontend-specific concerns:**
    - Component reusability and composition
    - State management (appropriate lifting, avoiding prop drilling)
    - Performance (lazy loading, memoization, bundle size)
    - Responsive design (mobile, tablet, desktop)
    - Accessibility (keyboard navigation, ARIA labels, screen readers)
```

### DevOps Tasks

```
Task tool (senior-devops):
  description: "Review DevOps spec compliance for Task N"
  prompt: |
    You are reviewing whether infrastructure/DevOps implementation matches its specification.

    [Use template from spec-reviewer-prompt.md, adding:]

    **DevOps-specific concerns:**
    - Infrastructure as code (reproducibility, idempotency)
    - Security (secrets management, least privilege)
    - Reliability (health checks, retries, circuit breakers)
    - Observability (logs, metrics, tracing)
    - Deployment strategy (zero-downtime, rollback capability)
```

## Optional Third Review Gate

For certain task types, add an optional third review gate after code quality review:

### Security Review (for backend/auth/API tasks)

If task involves authentication, authorization, security, or sensitive data:

```
Task tool (general-purpose with security focus):
  description: "Security review for Task N"
  prompt: |
    Review this implementation for security vulnerabilities.
    Focus on: OWASP Top 10, input validation, output encoding,
    authentication/authorization, secrets handling, SQL injection,
    XSS, CSRF. Report any security concerns with severity ratings.
```

### Accessibility Review (for UI/frontend tasks)

If task involves user-facing components:

```
Task tool (accessibility-auditor):
  description: "Accessibility review for Task N"
  prompt: |
    Review this UI implementation for WCAG 2.1 AA compliance.
    Focus on: keyboard navigation, screen reader compatibility,
    color contrast, form labels, ARIA attributes, semantic HTML.
```

## Decision Flow

```
                      ┌─────────────────┐
                      │   Read Task     │
                      └────────┬────────┘
                               │
                               ▼
                      ┌─────────────────┐
                      │ Detect Keywords │
                      └────────┬────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │  Backend    │     │  Frontend   │     │   DevOps    │
    │  Keywords?  │     │  Keywords?  │     │  Keywords?  │
    └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
           │                   │                   │
           ▼                   ▼                   ▼
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │ backend-    │     │ frontend-   │     │ senior-     │
    │ architect  │     │ developer   │     │ devops      │
    └─────────────┘     └─────────────┘     └─────────────┘

           ┌───────────────────────────────────────┐
           │         No clear keywords?            │
           ▼                                       │
    ┌─────────────┐                               │
    │ general-    │◄──────────────────────────────┘
    │ purpose     │
    └─────────────┘
```
