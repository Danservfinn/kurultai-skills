# Domain-Specialist Routing Guide

This reference provides detailed routing instructions for directing spec compliance reviews to domain specialists.

## Routing Decision Tree

```
Task Description Analysis
├── Contains API, endpoint, route, backend, database, schema?
│   └── Route to: backend-development:backend-architect
├── Contains component, UI, frontend, React, Vue, Angular, CSS?
│   └── Route to: senior-frontend
├── Contains infrastructure, CI/CD, Docker, Kubernetes, terraform?
│   └── Route to: senior-devops
├── Contains data, pipeline, ETL, analytics, warehouse?
│   └── Route to: senior-data-engineer
├── Contains ML, model, training, inference, prediction?
│   └── Route to: senior-data-scientist
├── Contains architecture, design, scalability, patterns?
│   └── Route to: senior-architect
└── Unclear or multiple domains?
    └── Use generic spec-reviewer-prompt.md
```

## Keyword Scoring

When keywords overlap, score each domain:

| Keyword | Backend | Frontend | DevOps | Data Eng | Data Science | Architecture |
|---------|---------|----------|--------|----------|--------------|--------------|
| API | 3 | 1 | 1 | 0 | 0 | 1 |
| endpoint | 3 | 1 | 0 | 0 | 0 | 1 |
| database | 3 | 0 | 1 | 2 | 0 | 1 |
| component | 0 | 3 | 0 | 0 | 0 | 0 |
| UI | 0 | 3 | 0 | 0 | 0 | 0 |
| React | 0 | 3 | 0 | 0 | 0 | 0 |
| Docker | 0 | 0 | 3 | 1 | 0 | 0 |
| Kubernetes | 0 | 0 | 3 | 1 | 0 | 0 |
| pipeline | 1 | 0 | 2 | 3 | 1 | 0 |
| ETL | 0 | 0 | 0 | 3 | 1 | 0 |
| ML | 0 | 0 | 0 | 1 | 3 | 0 |
| model | 1 | 0 | 0 | 1 | 3 | 1 |
| scalability | 1 | 0 | 1 | 0 | 0 | 3 |

**Routing Rule**: Route to highest scoring domain. If tie, prefer: Backend > Frontend > DevOps > Data Eng > Data Science > Architecture.

## Specialist Prompt Customization

### Backend Specialist (backend-development:backend-architect)

Additional focus areas:
- API design patterns (REST, GraphQL, gRPC)
- Database schema and query optimization
- Authentication and authorization
- Error handling and status codes
- Performance and caching

### Frontend Specialist (senior-frontend)

Additional focus areas:
- Component architecture
- State management patterns
- Accessibility (WCAG compliance)
- Responsive design
- Bundle size and performance

### DevOps Specialist (senior-devops)

Additional focus areas:
- Infrastructure as Code best practices
- CI/CD pipeline design
- Containerization and orchestration
- Monitoring and observability
- Security hardening

### Data Engineering Specialist (senior-data-engineer)

Additional focus areas:
- Data pipeline reliability
- Schema design and evolution
- Data quality and validation
- ETL/ELT patterns
- Performance optimization

### Data Science Specialist (senior-data-scientist)

Additional focus areas:
- Model selection and validation
- Statistical rigor
- Bias and fairness
- Reproducibility
- Experiment design

### Architecture Specialist (senior-architect)

Additional focus areas:
- System boundaries and coupling
- Scalability patterns
- SOLID principles
- Integration patterns
- Technical debt assessment

## Fallback Strategy

When confidence is low (< 60%):

1. Use generic spec-reviewer-prompt.md
2. Note the ambiguity in the review output
3. Suggest domain specialists to consult if issues are found

## Examples

**Example 1**: "Create a React component for user profiles"
- Frontend: 3 (component, React)
- Backend: 0
- **Route to**: senior-frontend

**Example 2**: "Build API endpoint for ML model predictions"
- Backend: 7 (API, endpoint, model)
- Data Science: 4 (ML, model)
- **Route to**: backend-development:backend-architect (higher score)

**Example 3**: "Set up Kubernetes deployment for data pipeline"
- DevOps: 5 (Kubernetes, pipeline)
- Data Eng: 4 (pipeline, data)
- **Route to**: senior-devops (higher score)
