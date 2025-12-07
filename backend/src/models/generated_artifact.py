"""
GeneratedArtifact model for workflow phase outputs.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from models import BaseModel


@dataclass
class GeneratedArtifact(BaseModel):
    """
    Represents a generated document artifact from a workflow phase.

    Attributes:
        artifact_type: Type of artifact (spec, plan, tasks, implement)
        phase_name: Workflow phase that generated this artifact
        content_markdown: Raw markdown content
        content_html: Rendered HTML content
        generated_at: Timestamp of generation
        tokens_used: Number of tokens used in generation (if applicable)
        generation_duration_ms: Time taken to generate in milliseconds
    """

    artifact_type: str  # spec, plan, tasks, implement
    phase_name: str  # specify, clarify, plan, tasks, implement
    content_markdown: str
    content_html: Optional[str] = None
    generated_at: Optional[datetime] = None
    tokens_used: Optional[int] = None
    generation_duration_ms: Optional[int] = None

    def __post_init__(self):
        """Validate artifact fields after initialization."""
        if self.generated_at is None:
            self.generated_at = datetime.utcnow()

        # Validate artifact_type
        valid_types = ["spec", "plan", "tasks", "implement"]
        if self.artifact_type not in valid_types:
            raise ValueError(
                f"Invalid artifact_type: {self.artifact_type}. Must be one of {valid_types}"
            )

        # Validate phase_name
        valid_phases = ["specify", "clarify", "plan", "tasks", "implement"]
        if self.phase_name not in valid_phases:
            raise ValueError(
                f"Invalid phase_name: {self.phase_name}. Must be one of {valid_phases}"
            )

        # Validate content_markdown
        if not self.content_markdown or len(self.content_markdown) < 10:
            raise ValueError("content_markdown must be at least 10 characters")
