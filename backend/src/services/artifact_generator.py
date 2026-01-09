"""
ArtifactGenerator for creating spec, plan, and tasks documents.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from models.generated_artifact import GeneratedArtifact
from models.demo_scenario import DemoScenario
from services.markdown_service import MarkdownService

logger = logging.getLogger(__name__)


class ArtifactGenerator:
    """Service for generating workflow artifacts from templates."""

    def __init__(self, templates_dir: Path = None):
        """
        Initialize artifact generator.

        Args:
            templates_dir: Path to templates directory. Defaults to backend/data/templates.
        """
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent.parent / "data" / "templates"

        self.templates_dir = templates_dir
        self.markdown_service = MarkdownService()
        logger.info(f"ArtifactGenerator initialized with templates: {templates_dir}")

    def _load_template(self, template_name: str) -> str:
        """Load template file content."""
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            logger.warning(f"Template not found: {template_path}")
            return f"# {template_name}\n\nTemplate not yet created."

        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()

    def _replace_placeholders(self, template: str, context: Dict[str, Any]) -> str:
        """Replace placeholders in template with context values."""
        result = template
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value) if value else "")
        return result

    def generate_with_context(
        self, 
        phase_name: str, 
        scenario: DemoScenario, 
        context: Dict[str, Any]
    ) -> GeneratedArtifact:
        """
        Generate an artifact for a specific phase using provided context.

        This method creates context-aware artifacts that incorporate user input
        from the current and previous phases.

        Args:
            phase_name: The workflow phase (specify, clarify, plan, tasks, implement).
            scenario: The demo scenario.
            context: Dictionary containing all context including user inputs.

        Returns:
            GeneratedArtifact with the generated content.
        """
        start_time = datetime.utcnow()
        
        # Determine artifact type and generate appropriate content
        # Map phase names to artifact types (clarify produces a refined spec)
        phase_to_artifact_type = {
            "specify": "spec",
            "clarify": "spec",  # Clarify produces a refined specification
            "plan": "plan",
            "tasks": "tasks",
            "implement": "implement"
        }
        
        if phase_name == "specify":
            markdown_content = self._generate_spec_content(scenario, context)
            artifact_type = "spec"
        elif phase_name == "clarify":
            markdown_content = self._generate_clarify_content(scenario, context)
            artifact_type = "spec"  # Clarify refines the spec
        elif phase_name == "plan":
            markdown_content = self._generate_plan_content(scenario, context)
            artifact_type = "plan"
        elif phase_name == "tasks":
            markdown_content = self._generate_tasks_content(scenario, context)
            artifact_type = "tasks"
        elif phase_name == "implement":
            markdown_content = self._generate_implement_content(scenario, context)
            artifact_type = "implement"
        else:
            markdown_content = f"# {phase_name.title()} Phase\n\nNo content generated for this phase."
            artifact_type = phase_name

        # Render to HTML
        html_content = self.markdown_service.render_to_html(markdown_content)
        
        # Calculate duration
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        # Estimate token count (roughly 4 characters per token for English text)
        estimated_tokens = len(markdown_content) // 4

        artifact = GeneratedArtifact(
            artifact_type=artifact_type,
            phase_name=phase_name,
            content_markdown=markdown_content,
            content_html=html_content,
            generated_at=datetime.utcnow(),
            generation_duration_ms=duration_ms,
            tokens_used=estimated_tokens,
        )

        logger.info(f"Generated {artifact_type} artifact for phase {phase_name} (~{estimated_tokens} tokens, {duration_ms}ms)")
        return artifact

    def _generate_spec_content(self, scenario: DemoScenario, context: Dict[str, Any]) -> str:
        """Generate specification content from user input or scenario's initial prompt."""
        user_input = context.get("user_input", "") or context.get("specify_input", "")
        
        # For demo scenarios (no user input), use the scenario's initial_prompt as the specification
        # For custom scenarios, use the user's input
        specification_content = user_input if user_input else scenario.initial_prompt
        
        content = f"""# Feature Specification: {context.get('title', scenario.title)}

## Overview

{context.get('description', scenario.description)}

## 📝 User Specification Input

> {specification_content}

## Domain

**Industry/Domain:** {context.get('domain', scenario.domain)}

## Technical Context

{f"**Tech Stack:** {context.get('tech_stack')}" if context.get('tech_stack') else ""}

## Analysis

Based on the specification above, this feature will require:

- **User Interface**: Interactive components for user interaction
- **Backend Services**: API endpoints and business logic
- **Data Layer**: Storage and retrieval mechanisms
- **Security**: Authentication and authorization checks

## Next Steps

Proceed to the **Clarification** phase to refine requirements and resolve any ambiguities.

## Generated

*Generated on {context.get('date', datetime.utcnow().strftime('%Y-%m-%d'))}*
"""
        return content

    def _generate_clarify_content(self, scenario: DemoScenario, context: Dict[str, Any]) -> str:
        """Generate clarification summary content."""
        clarifications = context.get("clarifications", "")
        user_input = context.get("user_input", "")
        specify_input = context.get("specify_input", "")
        
        # Build previous context section
        previous_context = ""
        if specify_input and specify_input != scenario.initial_prompt:
            previous_context = f"""
## 📋 Previous Context: Specification Phase

> **User Input from Specify Phase:**
> 
> {specify_input}

---
"""
        
        content = f"""# Clarification Summary: {context.get('title', scenario.title)}
{previous_context}
## Original Requirements

{scenario.initial_prompt}

## Clarifying Questions & Answers

{clarifications if clarifications else "*Answer the questions above and click 'Generate Artifact' to see your clarifications here.*"}

## Additional Context

{user_input if user_input else "*No additional context provided.*"}

## Next Steps

Based on the clarifications above, the next phase will create a detailed implementation plan.

## Generated

*Generated on {context.get('date', datetime.utcnow().strftime('%Y-%m-%d'))}*
"""
        return content

    def _generate_plan_content(self, scenario: DemoScenario, context: Dict[str, Any]) -> str:
        """Generate implementation plan content."""
        user_input = context.get("user_input", "")
        specify_input = context.get("specify_input", "")
        clarifications = context.get("clarifications", "")
        
        # Build previous context section
        previous_context = ""
        if specify_input and specify_input != scenario.initial_prompt:
            previous_context += f"""
> **From Specify Phase:**
> {specify_input}
"""
        if clarifications:
            previous_context += f"""
> **From Clarify Phase:**
> {clarifications}
"""
        
        previous_section = ""
        if previous_context:
            previous_section = f"""
## 📋 Previous Context

{previous_context}

---
"""
        
        content = f"""# Implementation Plan: {context.get('title', scenario.title)}
{previous_section}
## Executive Summary

This plan outlines the implementation approach for {context.get('title', scenario.title)}.

## Requirements Summary

{scenario.initial_prompt}

## Clarifications Applied

{clarifications if clarifications else '*No clarifications were provided.*'}

## Technical Approach

{user_input if user_input else f'''
### Architecture Overview

The implementation will follow a modular architecture with the following components:

1. **Frontend Layer** - User interface and experience
2. **Backend Layer** - Business logic and API endpoints  
3. **Data Layer** - Data persistence and management
4. **Integration Layer** - External service connections

### Technology Stack

{context.get('tech_stack', 'To be determined based on requirements')}

### Key Design Decisions

- Follow industry best practices for {context.get('domain', 'software development')}
- Implement comprehensive error handling
- Ensure scalability and maintainability
'''}

## Implementation Phases

1. **Phase 1: Foundation** - Project setup and infrastructure
2. **Phase 2: Core Features** - Primary functionality implementation
3. **Phase 3: Integration** - External services and APIs
4. **Phase 4: Polish** - Testing, documentation, and optimization

## Generated

*Generated on {context.get('date', datetime.utcnow().strftime('%Y-%m-%d'))}*
"""
        return content

    def _generate_tasks_content(self, scenario: DemoScenario, context: Dict[str, Any]) -> str:
        """Generate task breakdown content."""
        user_input = context.get("user_input", "")
        specify_input = context.get("specify_input", "")
        clarifications = context.get("clarifications", "")
        plan_input = context.get("plan_input", "")
        
        # Build previous context section.
        # For step 4 (tasks), we want the previous step's *output* (plan) to be the primary context,
        # rather than re-showing step 2 clarifications.
        previous_context_parts = []
        if plan_input:
            previous_context_parts.append(f"> **From Plan Phase:**\n> {plan_input}")
        elif clarifications:
            previous_context_parts.append(f"> **From Clarify Phase:**\n> {clarifications}")
        elif specify_input and specify_input != scenario.initial_prompt:
            previous_context_parts.append(f"> **From Specify Phase:**\n> {specify_input}")
        
        previous_section = ""
        if previous_context_parts:
            previous_section = f"""
## 📋 Previous Context

{chr(10).join(previous_context_parts)}

---
"""

        custom_requirements_section = (
            f"## Custom Requirements\n\n{user_input}" if user_input else ""
        )
        
        content = f"""# Task Breakdown: {context.get('title', scenario.title)}
{previous_section}
## Overview

This document contains the detailed task breakdown for implementing {context.get('title', scenario.title)}.

    {custom_requirements_section}

## Clarifications Applied

{clarifications if clarifications else '*No clarifications were provided.*'}

## Phase 1: Setup & Foundation

- [ ] T001 Create project directory structure
- [ ] T002 Configure development environment
- [ ] T003 Set up linting and formatting tools
- [ ] T004 Initialize version control
- [ ] T005 Create initial documentation

## Phase 2: Core Implementation

- [ ] T006 Implement data models
- [ ] T007 Create service layer
- [ ] T008 Build API endpoints
- [ ] T009 Develop frontend components
- [ ] T010 Implement business logic

## Phase 3: Integration & Testing

- [ ] T011 Write unit tests
- [ ] T012 Write integration tests
- [ ] T013 Configure CI/CD pipeline
- [ ] T014 Set up monitoring

## Phase 4: Polish & Documentation

- [ ] T015 Create user documentation
- [ ] T016 Performance optimization
- [ ] T017 Security review
- [ ] T018 Final testing and QA

## Dependencies

Tasks should be completed in order within each phase.

## Generated

*Generated on {context.get('date', datetime.utcnow().strftime('%Y-%m-%d'))}*
"""
        return content

    def _generate_implement_content(self, scenario: DemoScenario, context: Dict[str, Any]) -> str:
        """Generate implementation code/output content."""
        user_input = context.get("user_input", "")
        specify_input = context.get("specify_input", "")
        clarifications = context.get("clarifications", "")
        plan_input = context.get("plan_input", "")
        tasks_input = context.get("tasks_input", "")
        
        # Build previous context section.
        # For step 5 (implementation), the "previous" step is tasks, so prefer that output.
        previous_context_parts = []
        if tasks_input:
            previous_context_parts.append(f"> **From Tasks Phase:**\n> {tasks_input}")
        elif plan_input:
            previous_context_parts.append(f"> **From Plan Phase:**\n> {plan_input}")
        elif clarifications:
            previous_context_parts.append(f"> **From Clarify Phase:**\n> {clarifications}")
        elif specify_input and specify_input != scenario.initial_prompt:
            previous_context_parts.append(f"> **From Specify Phase:**\n> {specify_input}")
        
        previous_section = ""
        if previous_context_parts:
            previous_section = f"""
## 📋 Previous Context

{chr(10).join(previous_context_parts)}

---
"""

        implementation_notes_section = (
            f"## Implementation Notes\n\n{user_input}" if user_input else ""
        )
        
        content = f"""# Implementation: {context.get('title', scenario.title)}
{previous_section}
## Implementation Progress

🎉 **Congratulations!** You've completed the Spec Kit workflow demonstration.

## Summary of Workflow

1. ✅ **Specification** - Captured requirements
2. ✅ **Clarification** - Answered questions and refined scope
3. ✅ **Planning** - Created implementation approach
4. ✅ **Tasks** - Broke down work into actionable items
5. ✅ **Implementation** - Ready to execute!

## Clarifications Applied

{clarifications if clarifications else '*No clarifications were provided.*'}

{implementation_notes_section}

## What's Next?

In a real Spec Kit workflow, this phase would:

- Execute tasks automatically using AI assistance
- Generate code based on the plan and task breakdown
- Create pull requests with implemented features
- Run tests and validation checks

## Demo Complete

This demonstration shows how Spec Kit helps teams:

- **Specify** requirements clearly
- **Clarify** ambiguities before coding
- **Plan** implementation thoughtfully
- **Break down** work into manageable tasks
- **Implement** with confidence

## Generated

*Generated on {context.get('date', datetime.utcnow().strftime('%Y-%m-%d'))}*
"""
        return content

    def generate_spec(self, scenario: DemoScenario) -> GeneratedArtifact:
        """
        Generate spec.md artifact.

        Args:
            scenario: The demo scenario to generate spec for.

        Returns:
            GeneratedArtifact with spec content.
        """
        start_time = datetime.utcnow()

        # Load template
        template = self._load_template("spec-template.md")

        # Build context
        context = {
            "title": scenario.title,
            "description": scenario.description,
            "domain": scenario.domain,
            "initial_prompt": scenario.initial_prompt,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
        }

        # Replace placeholders
        markdown_content = self._replace_placeholders(template, context)

        # Render to HTML
        html_content = self.markdown_service.render_to_html(markdown_content)

        # Calculate duration
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        artifact = GeneratedArtifact(
            artifact_type="spec",
            phase_name="specify",
            content_markdown=markdown_content,
            content_html=html_content,
            generated_at=datetime.utcnow(),
            generation_duration_ms=duration_ms,
        )

        logger.info(f"Generated spec artifact for scenario: {scenario.id}")
        return artifact

    def generate_plan(self, scenario: DemoScenario) -> GeneratedArtifact:
        """
        Generate plan.md artifact.

        Args:
            scenario: The demo scenario to generate plan for.

        Returns:
            GeneratedArtifact with plan content.
        """
        start_time = datetime.utcnow()

        # Load template
        template = self._load_template("plan-template.md")

        # Build context
        context = {
            "title": scenario.title,
            "description": scenario.description,
            "domain": scenario.domain,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
        }

        # Replace placeholders
        markdown_content = self._replace_placeholders(template, context)

        # Render to HTML
        html_content = self.markdown_service.render_to_html(markdown_content)

        # Calculate duration
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        artifact = GeneratedArtifact(
            artifact_type="plan",
            phase_name="plan",
            content_markdown=markdown_content,
            content_html=html_content,
            generated_at=datetime.utcnow(),
            generation_duration_ms=duration_ms,
        )

        logger.info(f"Generated plan artifact for scenario: {scenario.id}")
        return artifact

    def generate_tasks(self, scenario: DemoScenario) -> GeneratedArtifact:
        """
        Generate tasks.md artifact.

        Args:
            scenario: The demo scenario to generate tasks for.

        Returns:
            GeneratedArtifact with tasks content.
        """
        start_time = datetime.utcnow()

        # Load template
        template = self._load_template("tasks-template.md")

        # Build context with workflow phases
        phases_list = "\n".join(
            [
                f"- [ ] {phase['display_name']}: {phase.get('description', 'Implementation task')}"
                for phase in scenario.workflow_phases
            ]
        )

        context = {
            "title": scenario.title,
            "description": scenario.description,
            "phases": phases_list,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
        }

        # Replace placeholders
        markdown_content = self._replace_placeholders(template, context)

        # Render to HTML
        html_content = self.markdown_service.render_to_html(markdown_content)

        # Calculate duration
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        artifact = GeneratedArtifact(
            artifact_type="tasks",
            phase_name="tasks",
            content_markdown=markdown_content,
            content_html=html_content,
            generated_at=datetime.utcnow(),
            generation_duration_ms=duration_ms,
        )

        logger.info(f"Generated tasks artifact for scenario: {scenario.id}")
        return artifact
