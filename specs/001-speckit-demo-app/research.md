# Research: GitHub Spec Kit Demo Application

**Date**: 2025-11-23  
**Feature**: [spec.md](./spec.md)  
**Purpose**: Resolve technical decisions for Python web app deployed to Azure with Bicep

## Technology Decisions

### Decision 1: Web Framework Selection

**Decision**: Flask (not FastAPI or Django)

**Rationale**:
- **Minimal dependencies**: Flask is lightweight (~7 core dependencies) aligning with "minimal libraries" requirement
- **Simplicity**: No need for async capabilities (FastAPI) - demo app has low concurrent load (10-50 presenters)
- **Quick setup**: Flask dev server starts in <2 seconds, meeting SC-001 (60-second Codespaces launch)
- **Mature ecosystem**: Extensive documentation, proven Azure App Service compatibility
- **No ORM needed**: Since we're using file-based storage, Django's ORM is unnecessary overhead

**Alternatives Considered**:
- **FastAPI**: Async capabilities overkill for this use case; adds complexity without performance benefit at our scale
- **Django**: Too heavy with ORM, admin panel, and batteries-included philosophy; contradicts "minimal libraries"
- **Bottle**: Even lighter than Flask but lacks ecosystem maturity for production Azure deployment

### Decision 2: Frontend Approach

**Decision**: Vanilla JavaScript with Alpine.js for reactivity (not React/Vue/Angular)

**Rationale**:
- **Bundle size**: Alpine.js is ~15KB gzipped vs React ~40KB + React DOM ~130KB - critical for FR-008 (<200KB initial JS)
- **Offline capability**: Simpler service worker implementation without complex build tooling
- **Performance**: Direct DOM manipulation for animations meets SC-003 (<500ms transitions) and SC-005 (<100ms interactions)
- **Learning curve**: Presenters modifying demos don't need to learn JSX or Vue templates
- **GitHub alignment**: Primer CSS (GitHub's design system) works seamlessly with vanilla JS

**Alternatives Considered**:
- **React**: Excellent developer experience but bundle size violates performance budget; overkill for demo app
- **Vue 3**: Better bundle size than React but still requires build tooling; composition API adds learning curve
- **Svelte**: Smallest bundle but less mature ecosystem; presenters may struggle with custom scenarios
- **Pure vanilla JS**: Considered but Alpine.js provides just enough reactivity without complexity

### Decision 3: Azure Deployment Architecture

**Decision**: Azure App Service with Linux container (not Container Apps, Functions, or Static Web Apps)

**Rationale**:
- **Simplicity**: Single service deployment - App Service hosts both backend API and serves static frontend
- **Cost-effective**: B1 tier ($13/month) sufficient for demo load; Container Apps has higher baseline cost
- **Azure Verified Modules**: App Service has mature AVM Bicep modules with excellent documentation
- **Integrated features**: Built-in application insights, deployment slots, easy rollback
- **Codespaces alignment**: Dev container can mirror production environment exactly

**Alternatives Considered**:
- **Azure Container Apps**: Over-engineered for single-service demo app; microservices complexity unnecessary
- **Azure Functions**: Serverless adds cold start latency (violates SC-005 <100ms); state management harder
- **Azure Static Web Apps**: Backend API support but less mature Python integration; preview feature instability
- **VM/AKS**: Manual infrastructure management contradicts Bicep IaC goals; unnecessary complexity

### Decision 4: Bicep Module Strategy

**Decision**: Azure Verified Modules (AVM) for all infrastructure

**Rationale**:
- **Official support**: Microsoft-maintained modules with guaranteed compatibility and security updates
- **Best practices**: AVMs encode Azure Well-Architected Framework principles by default
- **Compliance**: Pre-configured for common governance policies (tagging, diagnostics, RBAC)
- **Testing**: All AVMs have comprehensive test suites reducing deployment risk
- **Documentation**: Each module has detailed examples and parameter references

**Alternatives Considered**:
- **Custom Bicep modules**: Reinventing the wheel; higher maintenance burden
- **Terraform**: Not Bicep; contradicts requirement "deploying using Azure Bicep"
- **ARM templates**: Verbose JSON syntax; Bicep transpiles to ARM providing better developer experience

### Decision 5: State Management

**Decision**: Browser LocalStorage + in-memory server cache (not Redis/database)

**Rationale**:
- **Stateless backend**: Each demo session independent; no cross-session data sharing needed
- **Fast reset**: Clear localStorage and reload = instant reset (SC-002: <5 seconds)
- **Offline capability**: LocalStorage persists without server for FR-012 and FR-015
- **Simplicity**: No external dependencies; aligns with "minimal libraries" requirement
- **Scale appropriate**: 10-50 concurrent presenters don't need distributed state

**Alternatives Considered**:
- **Redis**: Adds cost ($10+/month) and complexity for minimal benefit at this scale
- **Cosmos DB**: Massive overkill; demo scenarios are static read-mostly data
- **Session cookies**: Browser storage limits (4KB) insufficient for demo state; server affinity issues

### Decision 6: Markdown Rendering

**Decision**: Python-Markdown with Pygments extension (server-side) + markdown-it (client-side for preview)

**Rationale**:
- **Consistency**: Server renders spec/plan/tasks files using same templates as real Spec Kit
- **Syntax highlighting**: Pygments provides GitHub-style code highlighting for FR-006
- **Performance**: Pre-render on server, cache aggressively, serve as HTML (faster than client-side parsing)
- **Offline**: Client-side markdown-it for custom scenario preview when offline

**Alternatives Considered**:
- **Marked.js (client-only)**: Violates performance budget; parsing 50KB markdown takes >100ms
- **CommonMark.py**: Stricter spec compliance but lacks GitHub-flavored markdown extensions
- **Mistune**: Faster but Pygments integration requires custom extension development

### Decision 7: Testing Strategy

**Decision**: pytest (backend) + Playwright (e2e) with 85% coverage target

**Rationale**:
- **Constitution compliance**: Exceeds 80% minimum (Principle II); 85% for safety margin
- **Pytest ecosystem**: Rich fixture support, parametrization, great Flask integration (test_client)
- **Playwright**: Cross-browser testing (Chrome, Firefox, Edge) ensures FR-016 compatibility
- **Fast feedback**: Unit tests <5 seconds, integration <15 seconds, e2e <60 seconds
- **CI/CD**: GitHub Actions has first-class support for both pytest and Playwright

**Alternatives Considered**:
- **Selenium**: More mature but slower than Playwright; lacks modern async capabilities
- **unittest**: Python stdlib but pytest fixtures and parametrization reduce boilerplate
- **Cypress**: JavaScript-only; doesn't test Python backend in same test suite

## Best Practices Research

### Python Web Development

**Key Practices**:
1. **Virtual environments**: Use `venv` or `virtualenv` to isolate dependencies
2. **Requirements pinning**: Pin exact versions in `requirements.txt` (Flask==3.0.0, not Flask>=3.0)
3. **Configuration**: Use environment variables with `python-dotenv` for secrets management
4. **Logging**: Structured logging with JSON output for Application Insights ingestion
5. **Error handling**: Custom error handlers for 404/500 with user-friendly messages (Principle III)
6. **Type hints**: Use `typing` module for all public APIs; validate with `mypy` (Principle I)
7. **Security**: Enable Flask security headers, validate all inputs, escape HTML output

**Sources**:
- Flask documentation: https://flask.palletsprojects.com/
- Python Packaging Guide: https://packaging.python.org/
- Real Python Flask tutorials: https://realpython.com/tutorials/flask/

### Azure App Service Best Practices

**Key Practices**:
1. **Container strategy**: Use multi-stage Dockerfile (build → production) to minimize image size
2. **Health checks**: Implement `/health` endpoint for App Service health probes
3. **Scaling**: Start with B1 tier, configure autoscale rules based on CPU/memory (not needed initially)
4. **Deployment slots**: Use staging slot for blue-green deployments (test before prod swap)
5. **Application Insights**: Enable auto-instrumentation for Flask with `opencensus-ext-azure`
6. **Environment variables**: Use App Service Configuration for secrets (not in code/Bicep)
7. **Managed identity**: Enable system-assigned identity for Key Vault access (if secrets needed)

**Sources**:
- Azure App Service docs: https://learn.microsoft.com/azure/app-service/
- Azure Well-Architected Framework: https://learn.microsoft.com/azure/well-architected/

### Bicep Infrastructure as Code

**Key Practices**:
1. **Azure Verified Modules**: Use `br/public:avm/res/*` registry for all resources
2. **Parameters**: Externalize environment-specific values to `.bicepparam` files
3. **Naming conventions**: Use `param` prefix for parameters, `var` for variables, descriptive resource names
4. **Outputs**: Export resource IDs, endpoints, managed identity principal IDs for downstream consumption
5. **Idempotency**: All deployments must be repeatable; avoid imperative scripts in Bicep
6. **Validation**: Use `az deployment group validate` before actual deployment
7. **What-if**: Always run `--what-if` to preview changes before production deployment

**Sources**:
- Azure Bicep documentation: https://learn.microsoft.com/azure/azure-resource-manager/bicep/
- Azure Verified Modules: https://aka.ms/avm
- Bicep best practices: https://learn.microsoft.com/azure/azure-resource-manager/bicep/best-practices

### GitHub Primer Design System

**Key Practices**:
1. **CSS framework**: Use Primer CSS via CDN or npm package (`@primer/css`)
2. **Component library**: Leverage Primer React for complex components (optional)
3. **Design tokens**: Use CSS variables for colors, spacing, typography from Primer
4. **Accessibility**: Primer components include ARIA attributes by default (Principle III)
5. **Icons**: Use Octicons icon set for GitHub-consistent visuals
6. **Dark mode**: Primer supports automatic dark mode based on `prefers-color-scheme`
7. **Responsive**: Primer includes responsive utilities matching GitHub breakpoints

**Sources**:
- Primer documentation: https://primer.style/
- Primer CSS: https://primer.style/css
- Octicons: https://primer.style/octicons

### Performance Optimization

**Key Practices**:
1. **Caching**: Aggressive browser caching for static assets (365 days), ETags for API responses
2. **Compression**: Enable gzip/brotli compression in Azure App Service
3. **Lazy loading**: Load demo scenarios on-demand, not all upfront
4. **Image optimization**: Use WebP format with fallback; lazy-load images below fold
5. **Bundle splitting**: Separate vendor JS from application code for better caching
6. **Service worker**: Cache assets for offline (FR-012), implement stale-while-revalidate strategy
7. **Metrics**: Monitor Web Vitals (LCP, FID, CLS) in Application Insights

**Sources**:
- Web.dev performance guides: https://web.dev/performance/
- Azure Front Door optimization: https://learn.microsoft.com/azure/frontdoor/

## Integration Patterns

### Pattern 1: API Communication

**Pattern**: RESTful JSON API with consistent error responses

**Implementation**:
```
GET  /api/scenarios                    - List all demo scenarios
GET  /api/scenarios/{id}               - Get specific scenario
POST /api/scenarios/custom             - Create custom scenario
GET  /api/workflow/{scenario_id}       - Get workflow state
POST /api/workflow/{scenario_id}/step  - Advance workflow step
POST /api/workflow/reset               - Reset demo state
GET  /api/constitution                 - Get constitution principles
GET  /api/health                       - Health check endpoint
```

**Error format**: `{"error": "description", "code": "ERROR_CODE", "status": 400}`

### Pattern 2: Service Worker for Offline

**Pattern**: Cache-first for static assets, network-first for API with fallback

**Implementation**:
- Install phase: Pre-cache critical assets (HTML, CSS, JS, demo scenarios JSON)
- Fetch phase: Network-first for `/api/*`, cache-first for `/static/*`, fallback for offline
- Update phase: Show update notification, activate new service worker on user action

### Pattern 3: State Management

**Pattern**: Single source of truth in LocalStorage, synced to server on critical actions

**Implementation**:
- LocalStorage schema: `{currentScenario, currentPhase, customScenarios[], presenterNotesVisible}`
- Sync triggers: Scenario selection, workflow phase change, custom scenario save
- Conflict resolution: Server state wins on refresh (demo can be re-run easily)

## Resolved Clarifications

All technical context fields from the plan template have been filled with informed decisions. No "NEEDS CLARIFICATION" markers remain.

**Summary**:
- **Language**: Python 3.11+ with Flask framework
- **Frontend**: Vanilla JS + Alpine.js with Primer CSS
- **Azure**: App Service (Linux container) deployed via Bicep AVMs
- **Storage**: File-based with LocalStorage for state
- **Testing**: pytest + Playwright with 85% coverage
- **Performance**: <100ms API, <50ms UI, <200KB bundle
- **Deployment**: GitHub Actions CI/CD with Bicep infrastructure pipeline
