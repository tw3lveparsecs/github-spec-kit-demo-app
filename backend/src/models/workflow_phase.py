"""
WorkflowPhase model for representing stages in the Spec Kit workflow.
"""

from dataclasses import dataclass
from typing import Optional, Any, Dict

from models import BaseModel


@dataclass
class WorkflowPhase(BaseModel):
    """
    Represents a single stage in the Spec Kit workflow process.
    
    Attributes:
        phase_name: Phase identifier (specify, clarify, plan, tasks, implement)
        display_name: User-friendly name
        order: Sequential position (1-based index)
        command: Spec Kit command (e.g., "/speckit.specify")
        input_required: Whether phase requires user input
        input_prompt: Prompt text if input is required
        generated_artifact: Output artifact from this phase (optional)
        estimated_duration_seconds: Expected time for simulated generation
        status: Current phase status (not_started, in_progress, completed, skipped)
    """

    phase_name: str
    display_name: str
    order: int
    command: str
    status: str = "not_started"
    input_required: bool = False
    input_prompt: Optional[str] = None
    generated_artifact: Optional[Dict[str, Any]] = None
    estimated_duration_seconds: int = 3

    def __post_init__(self) -> None:
        """Validate workflow phase data."""
        valid_phases = ["specify", "clarify", "plan", "tasks", "implement"]
        if self.phase_name not in valid_phases:
            raise ValueError(f"Phase name must be one of {valid_phases}, got {self.phase_name}")

        if not (1 <= self.order <= 5):
            raise ValueError(f"Order must be 1-5, got {self.order}")

        valid_statuses = ["not_started", "in_progress", "completed", "skipped"]
        if self.status not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}, got {self.status}")

        if not (1 <= self.estimated_duration_seconds <= 10):
            raise ValueError(
                f"Duration must be 1-10 seconds, got {self.estimated_duration_seconds}"
            )

        if self.input_required and not self.input_prompt:
            raise ValueError("Input prompt is required when input_required is True")
