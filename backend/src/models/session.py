"""
DemoSession model for tracking the current demo presentation state.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4

from models import BaseModel


@dataclass
class ActionLogEntry(BaseModel):
    """
    Represents a single recorded action during a demo session.
    
    Attributes:
        entry_id: Unique identifier
        timestamp: When action occurred
        action_type: Category of action
        action_detail: Specific action taken
        duration_ms: How long action took (optional)
    """

    entry_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    action_type: str = "scenario_select"
    action_detail: str = ""
    duration_ms: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate action log entry."""
        valid_types = [
            "scenario_select",
            "phase_advance",
            "phase_jump",
            "phase_input",
            "reset",
            "custom_create",
            "notes_toggle",
        ]
        if self.action_type not in valid_types:
            raise ValueError(f"Action type must be one of {valid_types}, got {self.action_type}")


@dataclass
class DemoSession(BaseModel):
    """
    Represents the current state of a demonstration presentation.
    
    Attributes:
        session_id: Unique identifier
        started_at: When demo session began
        current_scenario_id: ID of scenario being demonstrated (optional)
        current_phase_name: Current workflow phase name (optional)
        presenter_notes_visible: UI toggle state
        custom_scenarios: List of custom scenario IDs created in this session
        action_log: History of presenter actions for analytics
    """

    session_id: str = field(default_factory=lambda: str(uuid4()))
    started_at: datetime = field(default_factory=datetime.utcnow)
    current_scenario_id: Optional[str] = None
    current_phase_name: Optional[str] = None
    presenter_notes_visible: bool = False
    custom_scenarios: List[str] = field(default_factory=list)
    action_log: List[ActionLogEntry] = field(default_factory=list)
    phase_inputs: Dict[str, Any] = field(default_factory=dict)

    def log_action(
        self, action_type: str, action_detail: str, duration_ms: Optional[int] = None
    ) -> None:
        """
        Add an action to the session log.
        
        Args:
            action_type: Type of action performed
            action_detail: Details about the action
            duration_ms: Duration in milliseconds (optional)
        """
        entry = ActionLogEntry(
            action_type=action_type, action_detail=action_detail, duration_ms=duration_ms
        )
        self.action_log.append(entry)
