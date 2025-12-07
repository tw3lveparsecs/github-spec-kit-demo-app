"""
ArtifactGenerator for creating spec, plan, and tasks documents.
"""

import logging
from typing import Dict, Any
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
            result = result.replace(placeholder, str(value))
        return result

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
