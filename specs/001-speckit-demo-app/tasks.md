# Tasks: GitHub Spec Kit Demo Application

**Input**: Design documents from `/specs/001-speckit-demo-app/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in spec.md, so this task list focuses on implementation only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- File paths follow project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per plan.md (backend/, frontend/, infra/, .devcontainer/)
- [x] T002 Initialize Python virtual environment and install Flask in backend/requirements.txt
- [x] T003 [P] Configure Black formatter in backend/pyproject.toml
- [x] T004 [P] Configure mypy type checker in backend/pyproject.toml
- [x] T005 [P] Configure flake8 linter in backend/.flake8
- [x] T006 [P] Configure ESLint for JavaScript in frontend/.eslintrc.json
- [x] T007 Create .gitignore with Python, Node, and IDE exclusions at repository root
- [x] T008 Create README.md at repository root with project overview
- [x] T009 [P] Add Alpine.js (15KB) and Primer CSS via CDN in frontend/src/index.html
- [x] T010 [P] Install pytest and pytest-cov in backend/requirements-dev.txt
- [x] T011 [P] Install Playwright for e2e testing in frontend/package.json

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T012 Create Flask application entry point in backend/src/app.py with health endpoint
- [x] T013 [P] Configure Flask environment variables in backend/.flaskenv (FLASK_APP, FLASK_ENV)
- [x] T014 [P] Implement error handlers for 404/500 in backend/src/app.py
- [x] T015 [P] Setup structured logging with JSON output in backend/src/app.py
- [x] T016 [P] Configure CORS for frontend communication in backend/src/app.py
- [x] T017 Create data model base classes in backend/src/models/__init__.py
- [x] T018 Setup file-based scenario loader utility in backend/src/services/loader.py
- [x] T019 [P] Implement LRU cache decorator for scenario caching in backend/src/services/cache.py
- [x] T020 Create API route registration in backend/src/api/routes.py
- [x] T021 [P] Setup frontend main.js entry point with Alpine.js initialization in frontend/src/js/main.js
- [x] T022 [P] Create API client service for backend communication in frontend/src/js/services/api-client.js
- [x] T023 [P] Implement LocalStorage state manager in frontend/src/js/services/state-manager.js
- [x] T024 Create base CSS with Primer design tokens in frontend/src/css/main.css
- [x] T025 [P] Setup GitHub Codespaces devcontainer.json configuration in .devcontainer/devcontainer.json
- [x] T026 [P] Create Dockerfile for development environment in .devcontainer/Dockerfile
- [x] T027 Load constitution.md and parse into data structures in backend/src/services/constitution_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Quick Demo Setup (Priority: P1) 🎯 MVP

**Goal**: Presenter can launch demo in Codespaces <60s, see clean interface, reset demo <5s

**Independent Test**: Open in Codespaces, verify home screen loads in <10s, click "Reset Demo", verify clean state returns in <5s

### Implementation for User Story 1

#### Data Models
- [x] T028 [P] [US1] Create DemoScenario model in backend/src/models/demo_scenario.py
- [x] T029 [P] [US1] Create WorkflowPhase model in backend/src/models/workflow_phase.py
- [x] T030 [P] [US1] Create DemoSession model in backend/src/models/session.py

#### Pre-loaded Scenarios
- [x] T031 [P] [US1] Create user-authentication.json scenario in backend/data/scenarios/user-authentication.json
- [x] T032 [P] [US1] Create ecommerce-checkout.json scenario in backend/data/scenarios/ecommerce-checkout.json
- [x] T033 [P] [US1] Create data-dashboard.json scenario in backend/data/scenarios/data-dashboard.json

#### Backend Services
- [x] T034 [US1] Implement ScenarioService.list_scenarios() in backend/src/services/scenario_service.py
- [x] T035 [US1] Implement ScenarioService.get_scenario_by_id() in backend/src/services/scenario_service.py
- [x] T036 [US1] Implement SessionService.create_session() in backend/src/services/session_service.py
- [x] T037 [US1] Implement SessionService.reset_session() in backend/src/services/session_service.py

#### Backend API Endpoints
- [x] T038 [US1] Implement GET /api/health in backend/src/api/routes.py
- [x] T039 [US1] Implement GET /api/scenarios in backend/src/api/scenarios.py
- [x] T040 [US1] Implement GET /api/scenarios/{scenarioId} in backend/src/api/scenarios.py
- [x] T041 [US1] Implement GET /api/session in backend/src/api/routes.py
- [x] T042 [US1] Implement POST /api/workflow/reset in backend/src/api/workflow.py

#### Frontend Components
- [x] T043 [P] [US1] Create scenario-selector component in frontend/src/js/components/scenario-selector.js
- [x] T044 [P] [US1] Implement home screen layout in frontend/src/index.html
- [x] T045 [US1] Add reset button handler in frontend/src/js/main.js
- [x] T046 [US1] Implement scenario card styling with Primer CSS in frontend/src/css/components/scenario-card.css

#### Deployment Configuration
- [x] T047 [P] [US1] Create docker-compose.yml for local development at repository root
- [x] T048 [P] [US1] Create production Dockerfile with multi-stage build at repository root
- [x] T049 [US1] Configure Codespaces postCreateCommand in .devcontainer/devcontainer.json
- [x] T050 [US1] Add health check validation to quickstart.md at repository root

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Interactive Workflow Walkthrough (Priority: P2)

**Goal**: Presenter walks audience through specify→clarify→plan→tasks with animated artifact generation

**Independent Test**: Select sample scenario, click through all workflow phases, verify spec.md/plan.md/tasks.md display correctly

### Implementation for User Story 2

#### Data Models
- [x] T051 [P] [US2] Create GeneratedArtifact model in backend/src/models/generated_artifact.py
- [x] T052 [P] [US2] Create ActionLogEntry model in backend/src/models/session.py

#### Backend Services
- [x] T053 [P] [US2] Implement WorkflowService.initialize_workflow() in backend/src/services/workflow_service.py
- [x] T054 [US2] Implement WorkflowService.advance_phase() in backend/src/services/workflow_service.py
- [x] T055 [US2] Implement WorkflowService.jump_to_phase() in backend/src/services/workflow_service.py
- [x] T056 [P] [US2] Implement MarkdownService.render_to_html() in backend/src/services/markdown_service.py
- [x] T057 [P] [US2] Implement MarkdownService.highlight_code() using Pygments in backend/src/services/markdown_service.py
- [x] T058 [US2] Implement ArtifactGenerator.generate_spec() in backend/src/services/artifact_generator.py
- [x] T059 [US2] Implement ArtifactGenerator.generate_plan() in backend/src/services/artifact_generator.py
- [x] T060 [US2] Implement ArtifactGenerator.generate_tasks() in backend/src/services/artifact_generator.py

#### Template Artifacts
- [x] T061 [P] [US2] Create spec-template.md with placeholders in backend/data/templates/spec-template.md
- [x] T062 [P] [US2] Create plan-template.md with placeholders in backend/data/templates/plan-template.md
- [x] T063 [P] [US2] Create tasks-template.md with placeholders in backend/data/templates/tasks-template.md

#### Backend API Endpoints
- [x] T064 [US2] Implement GET /api/workflow/{scenarioId} in backend/src/api/workflow.py
- [x] T065 [US2] Implement POST /api/workflow/{scenarioId}/step in backend/src/api/workflow.py
- [x] T066 [US2] Implement POST /api/workflow/{scenarioId}/jump in backend/src/api/workflow.py

#### Frontend Components
- [x] T067 [P] [US2] Create workflow-stepper component in frontend/src/js/components/workflow-stepper.js
- [x] T068 [P] [US2] Create artifact-viewer component with syntax highlighting in frontend/src/js/components/artifact-viewer.js
- [x] T069 [US2] Implement typing animation helper in frontend/src/js/utils/animation-helpers.js
- [x] T070 [US2] Add workflow phase transition animations in frontend/src/css/animations.css
- [x] T071 [US2] Create workflow stepper UI in frontend/src/index.html
- [x] T072 [US2] Implement artifact side panel with expand/collapse in frontend/src/index.html

#### Workflow Phase UI
- [x] T073 [P] [US2] Style workflow progress bar with Primer CSS in frontend/src/css/components/workflow-stepper.css
- [x] T074 [P] [US2] Create artifact viewer panel styling in frontend/src/css/components/artifact-viewer.css
- [x] T075 [US2] Implement "Next Phase" button handler in frontend/src/js/main.js
- [x] T076 [US2] Implement "Jump to Phase" dropdown handler in frontend/src/js/main.js

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Constitution Showcase (Priority: P3)

**Goal**: Demonstrate constitution principles and enforcement during planning phase

**Independent Test**: Click "Constitution" tab, verify 4 principles display, run workflow to plan phase, verify constitution checks appear

### Implementation for User Story 3

#### Data Models
- [x] T077 [P] [US3] Create ConstitutionPrinciple model in backend/src/models/constitution.py
- [x] T078 [P] [US3] Create ConstitutionCheck model in backend/src/models/constitution.py
- [x] T079 [P] [US3] Create ConstitutionViolation model in backend/src/models/constitution.py

#### Backend Services
- [x] T080 [US3] Implement ConstitutionService.load_constitution() parsing .specify/memory/constitution.md in backend/src/services/constitution_service.py
- [x] T081 [US3] Implement ConstitutionService.evaluate_checks() for plan.md in backend/src/services/constitution_service.py
- [x] T082 [US3] Implement ConstitutionService.get_principles() in backend/src/services/constitution_service.py
- [x] T083 [US3] Add constitution check simulation to WorkflowService.advance_phase() during plan phase in backend/src/services/workflow_service.py

#### Backend API Endpoints
- [x] T084 [US3] Implement GET /api/constitution in backend/src/api/constitution.py
- [x] T085 [US3] Implement GET /api/constitution/check/{artifactId} in backend/src/api/constitution.py

#### Frontend Components
- [x] T086 [P] [US3] Create constitution-panel component in frontend/src/js/components/constitution-panel.js
- [x] T087 [US3] Add constitution tab to main UI in frontend/src/index.html
- [x] T088 [US3] Implement principle expandable sections in constitution-panel component
- [x] T089 [US3] Add constitution check badges to workflow stepper in workflow-stepper component

#### Styling
- [x] T090 [P] [US3] Style constitution panel with Primer CSS in frontend/src/css/components/constitution-panel.css
- [x] T091 [P] [US3] Create check status indicators (pass/fail badges) in frontend/src/css/components/check-badge.css
- [x] T092 [US3] Add violation warning indicators to plan phase in frontend/src/css/animations.css

**Checkpoint**: All three user stories (US1, US2, US3) should now be independently functional

---

## Phase 6: User Story 4 - Customizable Demo Scenarios (Priority: P4)

**Goal**: Presenter can create custom scenarios tailored to audience industry

**Independent Test**: Click "Create Custom", enter feature description, verify demo generates with custom input

### Implementation for User Story 4

#### Backend Services
- [x] T093 [US4] Implement ScenarioService.validate_custom_scenario() in backend/src/services/scenario_service.py
- [x] T094 [US4] Implement ScenarioService.create_custom_scenario() in backend/src/services/scenario_service.py
- [x] T095 [US4] Add custom scenario persistence to LocalStorage sync in SessionService

#### Backend API Endpoints
- [x] T096 [US4] Implement POST /api/scenarios/custom in backend/src/api/scenarios.py

#### Frontend Components
- [x] T097 [P] [US4] Create custom scenario form in frontend/src/index.html
- [x] T098 [US4] Implement custom scenario form validation in scenario-selector component
- [x] T099 [US4] Add "Create Custom" button handler in frontend/src/js/main.js
- [x] T100 [US4] Implement custom scenario save to LocalStorage in state-manager service

#### Styling
- [x] T101 [P] [US4] Style custom scenario form with Primer CSS in frontend/src/css/components/custom-scenario.css
- [x] T102 [P] [US4] Add form validation error styling in frontend/src/css/components/form-validation.css

**Checkpoint**: All four user stories should now be independently functional

---

## Phase 7: Presenter Notes (Optional Enhancement)

**Goal**: Add presenter notes panel for talking points (from spec.md FR-013)

**Independent Test**: Toggle presenter notes panel, verify context-specific tips appear

- [x] T103 [P] Create PresenterNote model in backend/src/models/presenter_note.py
- [x] T104 [P] Add sample presenter notes JSON files in backend/data/presenter-notes/
- [x] T105 Implement PresenterNoteService in backend/src/services/presenter_note_service.py
- [x] T106 Implement GET /api/presenter-notes/{contextType}/{contextId} in backend/src/api/routes.py
- [x] T107 [P] Create presenter-notes component in frontend/src/js/components/presenter-notes.js
- [x] T108 [P] Add presenter notes toggle button to UI in frontend/src/index.html
- [x] T109 Style presenter notes panel in frontend/src/css/components/presenter-notes.css

---

## Phase 8: Azure Infrastructure (Deployment)

**Goal**: Deploy application to Azure App Service using Bicep

**Independent Test**: Run `az deployment group create`, verify app accessible at Azure URL

- [x] T110 [P] Create main.bicep with App Service module in infra/main.bicep
- [x] T111 [P] Create app-service.bicep using Azure Verified Module in infra/modules/app-service.bicep
- [x] T112 [P] Create app-insights.bicep for monitoring in infra/modules/app-insights.bicep
- [x] T113 [P] Create dev.bicepparam with development parameters in infra/parameters/dev.bicepparam
- [x] T114 [P] Create prod.bicepparam with production parameters in infra/parameters/prod.bicepparam
- [x] T115 Create infrastructure deployment README in infra/README.md
- [x] T116 [P] Configure App Service startup command in main.bicep
- [x] T117 [P] Add Application Insights connection string to app settings in app-service.bicep

---

## Phase 9: CI/CD Pipeline

**Goal**: Automated testing, linting, and deployment via GitHub Actions

**Independent Test**: Push to main branch, verify Actions workflow passes and deploys to Azure

- [x] T118 [P] Create CI workflow for testing and linting in .github/workflows/ci.yml
- [x] T119 [P] Create CD workflow for Azure deployment in .github/workflows/cd.yml
- [x] T120 [P] Create infrastructure deployment workflow in .github/workflows/infrastructure.yml
- [x] T121 [P] Configure pytest with coverage reporting in CI workflow
- [x] T122 [P] Configure Black formatting check in CI workflow
- [x] T123 [P] Configure mypy type checking in CI workflow
- [x] T124 [P] Configure Playwright e2e tests in CI workflow
- [x] T125 Add deployment documentation to quickstart.md

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T126 [P] Add offline capability with service worker in frontend/src/sw.js
- [x] T127 [P] Implement response compression in Flask app
- [x] T128 [P] Add browser caching headers for static assets
- [x] T129 [P] Optimize bundle size (ensure <200KB per FR-008)
- [x] T130 [P] Add loading spinners for API calls in main.css
- [x] T131 [P] Implement toast notifications for user feedback in frontend/src/js/utils/toast.js
- [x] T132 [P] Add ARIA labels for accessibility (WCAG 2.1 AA) across all HTML
- [x] T133 [P] Ensure keyboard navigation works for all interactive elements
- [x] T134 [P] Add focus indicators for accessibility in main.css
- [x] T135 Add demo checklist validation script matching quickstart.md checklist
- [x] T136 Run performance profiling to verify <100ms API p95 target
- [x] T137 [P] Create comprehensive README with screenshots at repository root
- [x] T138 [P] Document API endpoints in OpenAPI Viewer link from README
- [x] T139 Run constitution compliance check on implementation
- [x] T140 Final validation against all 10 Success Criteria from spec.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion + User Story 1 models
- **User Story 3 (Phase 5)**: Depends on Foundational completion + User Story 2 workflow
- **User Story 4 (Phase 6)**: Depends on Foundational completion + User Story 1 scenario management
- **Presenter Notes (Phase 7)**: Optional - depends on Foundational completion
- **Azure Infrastructure (Phase 8)**: Can be developed in parallel with user stories, deployed after MVP
- **CI/CD (Phase 9)**: Should be set up early, can run in parallel with Phase 3+
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - MVP)**: Can start after Foundational (Phase 2) - No dependencies on other stories
  - Provides: Scenario management, session management, home screen, reset functionality
  - Blocking for: US2 (needs scenarios), US4 (extends scenario service)

- **User Story 2 (P2)**: Can start after Foundational (Phase 2) + US1 models complete (T028-T030)
  - Provides: Workflow execution, artifact generation, phase navigation
  - Blocking for: US3 (constitution checks happen during workflow)

- **User Story 3 (P3)**: Can start after Foundational (Phase 2) + US2 workflow service (T053-T055)
  - Provides: Constitution display, check enforcement
  - Not blocking for: Any other stories

- **User Story 4 (P4)**: Can start after Foundational (Phase 2) + US1 scenario service (T034-T035)
  - Provides: Custom scenario creation
  - Not blocking for: Any other stories

### Within Each User Story

For optimal TDD approach (if tests were requested):
1. Write tests first (contract tests, then integration tests)
2. Verify tests FAIL before implementation
3. Create models in parallel (all marked [P])
4. Implement services (may have dependencies on models)
5. Implement API endpoints (depend on services)
6. Create frontend components in parallel (all marked [P])
7. Wire up components to main application
8. Verify tests PASS

Since tests are NOT requested, implementation order:
1. Create models in parallel (all marked [P])
2. Create template files/JSON data in parallel (all marked [P])
3. Implement services (may have dependencies on models)
4. Implement API endpoints (depend on services)
5. Create frontend components in parallel (all marked [P])
6. Wire up components and styling
7. Manual testing per Independent Test criteria

### Parallel Opportunities

#### Within Setup (Phase 1)
```bash
# All configuration tasks can run together:
T003-T006: Black, mypy, flake8, ESLint configs
T009-T011: Frontend dependencies and test frameworks
```

#### Within Foundational (Phase 2)
```bash
# Backend foundation:
T013-T016: Flask config, error handlers, logging, CORS
T019, T027: Cache and constitution utilities

# Frontend foundation:
T021-T023: main.js, api-client, state-manager
```

#### Within User Story 1
```bash
# Models launch together:
T028-T030: DemoScenario, WorkflowPhase, DemoSession models

# Scenario files launch together:
T031-T033: All 3 pre-loaded scenario JSON files

# Frontend components launch together:
T043-T044: scenario-selector, home screen layout

# Deployment configs launch together:
T047-T048: docker-compose, Dockerfile
```

#### Within User Story 2
```bash
# Models launch together:
T051-T052: GeneratedArtifact, ActionLogEntry models

# Services launch together:
T053, T056-T057: Workflow and Markdown services

# Template files launch together:
T061-T063: spec, plan, tasks templates

# Frontend components launch together:
T067-T068: workflow-stepper, artifact-viewer
T073-T074: Component styling
```

#### Within User Story 3
```bash
# Models launch together:
T077-T079: ConstitutionPrinciple, ConstitutionCheck, ConstitutionViolation

# Styling launch together:
T090-T091: constitution-panel, check-badge CSS
```

#### Within Phase 8 (Azure Infrastructure)
```bash
# All Bicep modules can be developed in parallel:
T110-T112: main.bicep, app-service, app-insights
T113-T114: dev and prod parameters
T116-T117: App Service configuration
```

#### Within Phase 9 (CI/CD)
```bash
# All workflows can be created in parallel:
T118-T120: ci.yml, cd.yml, infrastructure.yml
T121-T124: All CI checks (pytest, Black, mypy, Playwright)
```

#### Within Phase 10 (Polish)
```bash
# Performance optimizations:
T126-T129: service worker, compression, caching, bundle optimization

# Accessibility:
T132-T134: ARIA labels, keyboard nav, focus indicators

# Documentation:
T137-T138: README, API docs
```

---

## Parallel Example: User Story 1 Models & Data

**Goal**: Get all foundational User Story 1 data structures ready simultaneously

```bash
# Launch all models together (no dependencies):
Task T028: "Create DemoScenario model in backend/src/models/demo_scenario.py"
Task T029: "Create WorkflowPhase model in backend/src/models/workflow_phase.py"
Task T030: "Create DemoSession model in backend/src/models/session.py"

# Launch all scenario data files together:
Task T031: "Create user-authentication.json scenario"
Task T032: "Create ecommerce-checkout.json scenario"
Task T033: "Create data-dashboard.json scenario"
```

Once these 6 tasks complete, services can begin (T034-T037).

---

## Implementation Strategy

### MVP First (Recommended)

**Goal**: Get a working demo in presenter's hands ASAP

1. **Phase 1: Setup** (T001-T011) → ~1-2 hours
   - Parallel: All config files (T003-T006, T009-T011)
   
2. **Phase 2: Foundational** (T012-T027) → ~3-4 hours
   - Parallel: Backend foundation (T013-T016), Frontend foundation (T021-T023)
   - **CRITICAL CHECKPOINT**: Foundation must be solid before continuing
   
3. **Phase 3: User Story 1 - MVP** (T028-T050) → ~6-8 hours
   - Parallel: Models (T028-T030), Scenarios (T031-T033), Frontend components (T043-T044)
   - **STOP and VALIDATE**: Test User Story 1 independently
   - Success criteria: Launch in Codespaces <60s, see 3 scenarios, reset <5s
   
4. **Phase 9: CI/CD (Partial)** (T118, T121-T123) → ~2 hours
   - Get basic CI working for continuous validation
   
5. **Demo MVP** → Total ~12-16 hours of focused development

At this point, you have a **demonstrable MVP** that satisfies:
- FR-001: Codespaces quick launch ✅
- FR-002: GitHub-styled UI ✅
- FR-003: Three pre-loaded scenarios ✅
- FR-007: Reset functionality ✅
- SC-001: Launch <60 seconds ✅
- SC-002: Reset <5 seconds ✅

### Incremental Delivery (Full Feature Set)

**After MVP is validated**, add remaining user stories in priority order:

6. **Phase 4: User Story 2 - Workflow** (T051-T076) → ~10-12 hours
   - Parallel: Models (T051-T052), Templates (T061-T063), Frontend (T067-T068, T073-T074)
   - **VALIDATE**: Full workflow walkthrough works end-to-end
   
7. **Phase 5: User Story 3 - Constitution** (T077-T092) → ~6-8 hours
   - Parallel: Models (T077-T079), Styling (T090-T091)
   - **VALIDATE**: Constitution displays, checks appear during plan phase
   
8. **Phase 6: User Story 4 - Custom Scenarios** (T093-T102) → ~4-6 hours
   - Parallel: Frontend form (T097), Styling (T101-T102)
   - **VALIDATE**: Custom scenario creation works
   
9. **Phase 8: Azure Deployment** (T110-T117) → ~4-6 hours
   - Parallel: All Bicep modules (T110-T114)
   - **VALIDATE**: Deploys to Azure successfully
   
10. **Phase 9: CI/CD (Complete)** (T119-T120, T124-T125) → ~2-3 hours
    - Add CD and Playwright tests
    
11. **Phase 10: Polish** (T126-T140) → ~6-8 hours
    - Parallel: Optimizations (T126-T129), Accessibility (T132-T134), Docs (T137-T138)
    - **FINAL VALIDATION**: All 10 Success Criteria met

**Total estimated effort**: ~44-60 hours for complete feature set

### Parallel Team Strategy

With **3 developers** after Foundational phase completes:

- **Developer A**: User Story 1 (Phase 3) → 6-8 hours
- **Developer B**: Azure Infrastructure (Phase 8) → 4-6 hours, then CI/CD (Phase 9) → 4-5 hours
- **Developer C**: Data preparation (scenarios JSON, templates) → 2-3 hours, then User Story 2 prep (models, services) → 6-8 hours

After User Story 1 validates:
- **Developer A**: User Story 2 (Phase 4) → 10-12 hours
- **Developer B**: User Story 3 (Phase 5) → 6-8 hours
- **Developer C**: User Story 4 (Phase 6) → 4-6 hours

Stories integrate independently without conflicts.

---

## Notes

- **[P] marker**: Tasks with [P] operate on different files and can run in parallel
- **[Story] label**: Maps task to specific user story (US1, US2, US3, US4) for traceability
- **File paths**: Follow project structure from plan.md (backend/src/, frontend/src/, infra/)
- **Independent testing**: Each user story has clear acceptance criteria for validation
- **Constitution compliance**: Phase 10 includes final constitution check (T139)
- **Performance validation**: T136 verifies <100ms API response target from FR-008
- **Success criteria**: T140 validates all 10 metrics from spec.md section "Success Criteria"

**Critical Success Factors**:
1. ✅ Complete Foundational phase before starting ANY user story
2. ✅ Validate User Story 1 (MVP) before proceeding to US2
3. ✅ Use parallel tasks (marked [P]) to accelerate development
4. ✅ Test each user story independently per "Independent Test" criteria
5. ✅ Follow constitution principles throughout (Black formatting, type hints, error handling)
