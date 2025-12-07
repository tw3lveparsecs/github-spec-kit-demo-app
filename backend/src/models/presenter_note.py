"""
PresenterNote model for context-specific talking points.

Presenter notes help demo presenters communicate key concepts
effectively during live demonstrations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from models import BaseModel


@dataclass
class PresenterNote(BaseModel):
    """
    Represents a context-specific presenter note with talking points.
    
    Attributes:
        note_id: Unique identifier for the note
        title: Brief title for the note
        content: Main content of the note
        context_type: Type of context (phase, scenario, feature)
        context_id: ID of the specific context (e.g., "plan", "user-authentication")
        timing: When to show the note (before, during, after)
        tips: Optional presenter tips
        emphasis_level: Priority level (1=low, 2=medium, 3=high)
    """
    
    note_id: str
    title: str
    content: str
    context_type: str  # "phase", "scenario", "feature"
    context_id: str
    timing: Optional[str] = None  # "before", "during", "after"
    tips: List[str] = field(default_factory=list)
    emphasis_level: int = 1  # 1-3
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Valid context types
    VALID_CONTEXT_TYPES = ["phase", "scenario", "feature"]
    VALID_TIMINGS = ["before", "during", "after"]
    
    def __post_init__(self):
        """Validate presenter note data."""
        if not self.note_id:
            raise ValueError("Note ID is required")
        if self.context_type and self.context_type not in self.VALID_CONTEXT_TYPES:
            raise ValueError(f"Context type must be one of: {self.VALID_CONTEXT_TYPES}")
        if not self.context_id:
            raise ValueError("Context ID is required")
        if not self.title or len(self.title) < 3:
            raise ValueError("Title must be at least 3 characters")
        if self.timing and self.timing not in self.VALID_TIMINGS:
            raise ValueError(f"Timing must be one of: {self.VALID_TIMINGS}")
        if self.emphasis_level < 1 or self.emphasis_level > 3:
            raise ValueError("Emphasis level must be between 1 and 3")
