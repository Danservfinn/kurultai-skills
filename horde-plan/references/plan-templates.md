# Plan Templates

This directory contains templates for common plan types that horde-plan can generate.

## Template: CRUD Feature

Use this template when creating plans for standard CRUD operations.

```markdown
# [Resource] CRUD Implementation Plan

## Overview

**Goal:** Create full CRUD interface for [Resource]

**Architecture:** RESTful API with [ORM/ODM], [Frontend Framework] components

**Tech Stack:** [List technologies]

## Phase Breakdown

### Phase 1: Database & Models
- Task 1.1: Create [table/collection] schema
- Task 1.2: Create model definitions
- Task 1.3: Add validation rules

### Phase 2: Backend API
- Task 2.1: GET /api/[resource] - List all
- Task 2.2: GET /api/[resource]/:id - Get one
- Task 2.3: POST /api/[resource] - Create
- Task 2.4: PUT /api/[resource]/:id - Update
- Task 2.5: DELETE /api/[resource]/:id - Delete

### Phase 3: Frontend UI
- Task 3.1: List view component
- Task 3.2: Detail view component
- Task 3.3: Create/Edit form
- Task 3.4: Delete confirmation

### Phase 4: Testing
- Task 4.1: API tests
- Task 4.2: Component tests
- Task 4.3: E2E tests
```

## Template: Integration Work

Use this template when integrating external services.

```markdown
# [Service] Integration Plan

## Overview

**Goal:** Integrate [External Service] for [Purpose]

**Architecture:** [Sync/Async] integration via [protocol]

**Tech Stack:** [List technologies]

## Phase Breakdown

### Phase 1: Client Setup
- Task 1.1: Install SDK/client library
- Task 1.2: Configure authentication
- Task 1.3: Create wrapper service

### Phase 2: Core Integration
- Task 2.1: Implement primary operation
- Task 2.2: Add error handling
- Task 2.3: Add retry logic

### Phase 3: Data Mapping
- Task 3.1: Map external format to internal models
- Task 3.2: Handle edge cases
- Task 3.3: Add transformation tests

### Phase 4: UI Integration
- Task 4.1: Connect to existing forms
- Task 4.2: Add loading states
- Task 4.3: Add error display

### Phase 5: Testing & Docs
- Task 5.1: Mock external service for tests
- Task 5.2: Integration tests
- Task 5.3: Setup documentation
```

## Template: Refactoring

Use this template when refactoring existing code.

```markdown
# [Component] Refactoring Plan

## Overview

**Goal:** Refactor [Component] for [motivation]

**Architecture:** [New architecture pattern]

**Current Issues:** [List problems being solved]

## Phase Breakdown

### Phase 1: Analysis
- Task 1.1: Map current dependencies
- Task 1.2: Identify coupling points
- Task 1.3: Design new structure

### Phase 2: Extraction
- Task 2.1: Extract module A
- Task 2.2: Extract module B
- Task 2.3: Update imports

### Phase 3: Implementation
- Task 3.1: Implement new pattern
- Task 3.2: Migrate existing code
- Task 3.3: Remove old code

### Phase 4: Verification
- Task 4.1: All existing tests pass
- Task 4.2: Add new tests
- Task 4.3: Performance comparison
```

## Template: Infrastructure

Use this template for DevOps/infrastructure work.

```markdown
# [Infrastructure] Setup Plan

## Overview

**Goal:** Set up [service/infrastructure]

**Architecture:** [Diagram/description]

**Tech Stack:** [Cloud provider, tools]

## Phase Breakdown

### Phase 1: Planning
- Task 1.1: Design architecture
- Task 1.2: Create diagrams
- Task 1.3: Estimate costs

### Phase 2: Implementation
- Task 2.1: Configure [service A]
- Task 2.2: Configure [service B]
- Task 2.3: Set up networking

### Phase 3: Automation
- Task 3.1: Create IaC templates
- Task 3.2: Set up CI/CD
- Task 3.3: Add monitoring

### Phase 4: Validation
- Task 4.1: Test failover
- Task 4.2: Load testing
- Task 4.3: Security review
```
