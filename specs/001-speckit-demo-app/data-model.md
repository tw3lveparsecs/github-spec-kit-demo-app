# Data Model: GitHub Spec Kit Demo Application

**Date**: 2025-11-23  
**Feature**: [spec.md](./spec.md)  
**Purpose**: Define entities, attributes, relationships, and validation rules

## Entity Definitions

### 1. DemoScenario

Represents a pre-configured or custom feature example used for demonstrating the Spec Kit workflow.

**Attributes**:
- `id` (string, required): Unique identifier (e.g., "user-authentication", "ecommerce-checkout")
- `title` (string, required): Human-readable name (e.g., "User Authentication System")
- `description` (string, required): Brief overview of the feature being demonstrated
- `domain` (string, required): Industry domain (e.g., "security", "ecommerce", "analytics")
- `created_at` (datetime, required): Timestamp when scenario was created
- `is_custom` (boolean, required): True if created by presenter, false if pre-loaded
- `workflow_phases` (array<WorkflowPhase>, required): Ordered list of workflow phases for this scenario
- `initial_prompt` (string, required): The feature description that starts the workflow

**Validation Rules**:
- `id` must be lowercase, alphanumeric with hyphens only (regex: `^[a-z0-9-]+$`)
- `title` must be 5-100 characters
- `description` must be 20-500 characters
- `domain` must be one of: ["security", "ecommerce", "analytics", "infrastructure", "data", "ui", "other"]
- `workflow_phases` must contain at least 2 phases (specify, clarify minimum)

**Relationships**:
- Has many `WorkflowPhase` (one-to-many composition)
- Referenced by `DemoSession.current_scenario` (one-to-many)

**State Transitions**:
- `Custom scenario created` → `Draft` → `Validated` → `Saved`
- Pre-loaded scenarios are always in `Validated` state

---

### 2. WorkflowPhase

Represents a single stage in the Spec Kit workflow process.

**Attributes**:
- `phase_name` (string, required): Phase identifier ("specify", "clarify", "plan", "tasks", "implement")
- `display_name` (string, required): User-friendly name (e.g., "Specification", "Clarification")
- `order` (integer, required): Sequential position in workflow (1-based index)
- `command` (string, required): Spec Kit command for this phase (e.g., "/speckit.specify")
- `input_required` (boolean, required): Whether phase requires user input
- `input_prompt` (string, optional): Prompt text if input_required is true
- `generated_artifact` (GeneratedArtifact, optional): Output artifact from this phase
- `estimated_duration_seconds` (integer, required): Expected time for simulated generation
- `status` (string, required): One of ["not_started", "in_progress", "completed", "skipped"]

**Validation Rules**:
- `phase_name` must be one of: ["specify", "clarify", "plan", "tasks", "implement"]
- `order` must be positive integer (1-5)
- `estimated_duration_seconds` must be 1-10 seconds (for animation pacing)
- If `input_required` is true, `input_prompt` must not be null

**Relationships**:
- Belongs to `DemoScenario` (many-to-one)
- Has one `GeneratedArtifact` (one-to-one optional)
- Referenced by `DemoSession.current_phase` (one-to-many)

**State Transitions**:
- `not_started` → `in_progress` (when user clicks "Run" or "Next")
- `in_progress` → `completed` (when artifact generation finishes)
- `not_started|in_progress|completed` → `skipped` (when user clicks "Jump to Phase")

---

### 3. GeneratedArtifact

Represents a markdown document produced during workflow simulation.

**Attributes**:
- `artifact_id` (string, required): Unique identifier (UUID)
- `artifact_type` (string, required): Type of document ("spec", "plan", "tasks")
- `filename` (string, required): Expected filename (e.g., "spec.md", "plan.md")
- `content` (string, required): Markdown content of the artifact
- `content_preview` (string, required): First 200 characters for list views
- `generated_at` (datetime, required): Timestamp of generation
- `line_count` (integer, required): Number of lines in content
- `word_count` (integer, required): Number of words for metadata display
- `has_constitution_checks` (boolean, required): Whether artifact includes constitution violations

**Validation Rules**:
- `artifact_type` must be one of: ["spec", "plan", "tasks", "research", "data-model", "quickstart"]
- `filename` must match pattern: `^[a-z-]+\.md$`
- `content` must be valid Markdown (parsed without errors)
- `content_preview` must be <= 200 characters
- `line_count` and `word_count` must be positive integers

**Relationships**:
- Belongs to `WorkflowPhase` (many-to-one optional)
- Has many `ConstitutionViolation` if `has_constitution_checks` is true (one-to-many)

**State Transitions**:
- N/A - artifacts are immutable once generated (new artifact created for updates)

---

### 4. ConstitutionPrinciple

Represents one of the four organizational principles enforced by the constitution.

**Attributes**:
- `principle_id` (string, required): Identifier ("code-quality", "testing", "ux", "performance")
- `roman_numeral` (string, required): Display identifier ("I", "II", "III", "IV")
- `title` (string, required): Principle name (e.g., "Code Quality Standards")
- `description` (string, required): Full principle text from constitution.md
- `rationale` (string, required): Why this principle exists
- `checks` (array<string>, required): List of specific checks for this principle
- `is_non_negotiable` (boolean, required): Whether principle can be violated with justification

**Validation Rules**:
- `principle_id` must be one of: ["code-quality", "testing", "ux", "performance"]
- `roman_numeral` must match principle_id (I→code-quality, II→testing, III→ux, IV→performance)
- `checks` array must contain at least 3 items
- `is_non_negotiable` is true for "testing" principle only

**Relationships**:
- Has many `ConstitutionCheck` (one-to-many)
- Referenced by `ConstitutionViolation` (one-to-many)

**State Transitions**:
- N/A - principles are static configuration loaded from constitution.md

---

### 5. ConstitutionCheck

Represents a single validation item within a constitution principle.

**Attributes**:
- `check_id` (string, required): Unique identifier (e.g., "code-quality-linting")
- `principle_id` (string, required): Foreign key to ConstitutionPrinciple
- `check_text` (string, required): Description of what is being validated
- `status` (string, required): One of ["pass", "fail", "pending", "not_applicable"]
- `explanation` (string, optional): Additional context for the check result
- `can_be_justified` (boolean, required): Whether failure can be justified vs. blocking

**Validation Rules**:
- `status` must be one of: ["pass", "fail", "pending", "not_applicable"]
- If `status` is "fail" and `can_be_justified` is false, must block workflow progression
- If `status` is "fail" and `can_be_justified` is true, `explanation` is required

**Relationships**:
- Belongs to `ConstitutionPrinciple` (many-to-one)
- May create `ConstitutionViolation` if status is "fail" (one-to-one optional)

**State Transitions**:
- `pending` → `pass` (when validation succeeds)
- `pending` → `fail` (when validation fails)
- `pending|pass|fail` → `not_applicable` (when context changes)

---

### 6. ConstitutionViolation

Represents a failed constitution check that requires attention or justification.

**Attributes**:
- `violation_id` (string, required): Unique identifier (UUID)
- `check_id` (string, required): Foreign key to ConstitutionCheck
- `principle_id` (string, required): Foreign key to ConstitutionPrinciple
- `artifact_id` (string, required): Foreign key to GeneratedArtifact where violation occurred
- `violation_description` (string, required): User-friendly explanation of the issue
- `justification` (string, optional): Presenter's explanation for why violation is acceptable
- `is_blocking` (boolean, required): Whether violation prevents workflow progression
- `resolution_status` (string, required): One of ["unresolved", "justified", "fixed"]

**Validation Rules**:
- If `resolution_status` is "justified", `justification` must not be null
- If `is_blocking` is true and `resolution_status` is "unresolved", workflow cannot advance
- `violation_description` must be 20-500 characters

**Relationships**:
- Belongs to `ConstitutionCheck` (many-to-one)
- Belongs to `ConstitutionPrinciple` (many-to-one)
- Belongs to `GeneratedArtifact` (many-to-one)

**State Transitions**:
- `unresolved` → `justified` (presenter provides justification)
- `unresolved` → `fixed` (presenter corrects the issue)
- Transitions blocked if `is_blocking` is true until resolution

---

### 7. DemoSession

Represents the current state of a demonstration presentation.

**Attributes**:
- `session_id` (string, required): Unique identifier (UUID)
- `started_at` (datetime, required): When demo session began
- `current_scenario_id` (string, optional): Foreign key to DemoScenario being demonstrated
- `current_phase_name` (string, optional): Current WorkflowPhase phase_name
- `presenter_notes_visible` (boolean, required, default: false): UI toggle state
- `custom_scenarios` (array<string>, required): List of custom scenario IDs created in this session
- `action_log` (array<ActionLogEntry>, required): History of presenter actions for analytics

**Validation Rules**:
- If `current_scenario_id` is set, `current_phase_name` must be valid for that scenario
- `action_log` entries must have valid timestamps in chronological order
- `custom_scenarios` IDs must exist in DemoScenario table

**Relationships**:
- References `DemoScenario` via `current_scenario_id` (many-to-one optional)
- Contains many `ActionLogEntry` (one-to-many composition)

**State Transitions**:
- `Session started` → `Scenario selected` → `Workflow in progress` → `Workflow complete` → `Reset`
- Can jump to any state via demo controls (not a strict state machine)

---

### 8. PresenterNote

Represents contextual talking points and tips for presenters.

**Attributes**:
- `note_id` (string, required): Unique identifier
- `context_type` (string, required): Where note appears ("scenario", "phase", "principle")
- `context_id` (string, required): Foreign key to related entity
- `note_text` (string, required): Markdown-formatted talking points
- `is_critical` (boolean, required): Whether to highlight as important
- `display_order` (integer, required): Order for multiple notes in same context

**Validation Rules**:
- `context_type` must be one of: ["scenario", "phase", "principle", "general"]
- `note_text` must be 10-1000 characters
- `display_order` must be positive integer

**Relationships**:
- Belongs to `DemoScenario`, `WorkflowPhase`, or `ConstitutionPrinciple` via polymorphic association
- Referenced by `DemoSession` when presenter_notes_visible is true

**State Transitions**:
- N/A - notes are static content loaded from configuration

---

### 9. ActionLogEntry

Represents a single recorded action during a demo session (for analytics).

**Attributes**:
- `entry_id` (string, required): Unique identifier (UUID)
- `timestamp` (datetime, required): When action occurred
- `action_type` (string, required): Category of action
- `action_detail` (string, required): Specific action taken
- `duration_ms` (integer, optional): How long action took (for performance tracking)

**Validation Rules**:
- `action_type` must be one of: ["scenario_select", "phase_advance", "phase_jump", "reset", "custom_create", "notes_toggle"]
- `timestamp` must be within current session timeframe
- `duration_ms`, if present, must be positive integer

**Relationships**:
- Belongs to `DemoSession` (many-to-one composition)

**State Transitions**:
- N/A - log entries are immutable (append-only log)

---

## Entity Relationships Diagram

```
DemoScenario (1) ──┬── (many) WorkflowPhase
                   │
                   └── (many) DemoSession [via current_scenario_id]

WorkflowPhase (1) ──── (1) GeneratedArtifact [optional]

GeneratedArtifact (1) ──── (many) ConstitutionViolation

ConstitutionPrinciple (1) ──┬── (many) ConstitutionCheck
                             │
                             └── (many) ConstitutionViolation

ConstitutionCheck (1) ──── (1) ConstitutionViolation [optional]

DemoSession (1) ──┬── (many) ActionLogEntry
                  │
                  └── (1) DemoScenario [via current_scenario_id, optional]

PresenterNote (polymorphic) ─┬── DemoScenario
                              ├── WorkflowPhase
                              └── ConstitutionPrinciple
```

## Storage Strategy

### File-Based Storage

**Pre-loaded Scenarios** (`backend/data/scenarios/*.json`):
```json
{
  "id": "user-authentication",
  "title": "User Authentication System",
  "description": "Implement secure user authentication...",
  "domain": "security",
  "is_custom": false,
  "workflow_phases": [
    {
      "phase_name": "specify",
      "display_name": "Specification",
      "order": 1,
      "command": "/speckit.specify",
      "input_required": false,
      "estimated_duration_seconds": 3,
      "status": "not_started",
      "generated_artifact": null
    }
  ]
}
```

**Constitution Data** (loaded from `/.specify/memory/constitution.md`):
- Parsed at application startup
- Cached in memory for fast access
- Mapped to ConstitutionPrinciple and ConstitutionCheck entities

**Browser LocalStorage** (JSON serialized):
- Key: `speckit_demo_session`
- Value: DemoSession object with current state
- Size limit: ~5MB (sufficient for demo state)
- Persistence: Until user clicks "Reset Demo" or clears browser data

### Caching Strategy

**In-Memory Cache** (Python backend):
```python
# LRU cache with 100 item limit
@lru_cache(maxsize=100)
def get_scenario_by_id(scenario_id: str) -> DemoScenario:
    # Load from file, cache result
    pass

# Warm cache at startup with all pre-loaded scenarios
def warm_cache():
    for scenario_file in glob("backend/data/scenarios/*.json"):
        load_scenario(scenario_file)
```

**Benefits**:
- API response <50ms (cached reads)
- No database overhead
- Simple deployment (no external dependencies)
- Easy demo reset (clear cache + reload from files)

## Data Validation Examples

### Scenario Creation Validation

```python
def validate_custom_scenario(data: dict) -> tuple[bool, list[str]]:
    errors = []
    
    # ID format
    if not re.match(r'^[a-z0-9-]+$', data.get('id', '')):
        errors.append("ID must be lowercase alphanumeric with hyphens")
    
    # Title length
    title = data.get('title', '')
    if not (5 <= len(title) <= 100):
        errors.append("Title must be 5-100 characters")
    
    # Description length
    description = data.get('description', '')
    if not (20 <= len(description) <= 500):
        errors.append("Description must be 20-500 characters")
    
    # Domain enum
    valid_domains = ["security", "ecommerce", "analytics", "infrastructure", "data", "ui", "other"]
    if data.get('domain') not in valid_domains:
        errors.append(f"Domain must be one of: {', '.join(valid_domains)}")
    
    return (len(errors) == 0, errors)
```

### Constitution Check Validation

```python
def evaluate_constitution_checks(artifact: GeneratedArtifact) -> list[ConstitutionViolation]:
    violations = []
    
    # Example: Check if plan.md has constitution check section
    if artifact.artifact_type == "plan":
        if "## Constitution Check" not in artifact.content:
            violations.append(ConstitutionViolation(
                check_id="plan-has-constitution-check",
                principle_id="testing",  # Principle II
                violation_description="Plan must include Constitution Check section",
                is_blocking=True,
                resolution_status="unresolved"
            ))
    
    return violations
```

## Performance Considerations

**Entity Access Patterns**:
- DemoScenario: Read-heavy (95% reads, 5% custom scenario writes)
- WorkflowPhase: Read-heavy (100% reads during demo, updated in-place)
- GeneratedArtifact: Write-once, read-many
- ConstitutionPrinciple: Read-only (loaded at startup)
- DemoSession: Read/write balanced (frequent state updates)

**Optimization Strategies**:
- Pre-load all scenarios at startup → O(1) access
- Cache constitution principles → avoid repeated file parsing
- Lazy-load presenter notes → only when panel toggled
- Batch action log writes → reduce localStorage thrashing

**Memory Footprint**:
- 3 pre-loaded scenarios × ~50KB each = 150KB
- Constitution data: ~20KB
- Session state: ~10KB
- Total backend memory: <200KB data + ~312MB Python runtime = **<512MB**
- Meets Azure App Service B1 tier constraint ✓