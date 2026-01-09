"""
DemoScenario model for representing demo feature scenarios.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Any, Dict, Optional

from models import BaseModel


@dataclass
class DemoScenario(BaseModel):
    """
    Represents a pre-configured or custom feature example for demo purposes.
    
    Attributes:
        id: Unique identifier (e.g., "user-authentication")
        title: Human-readable name
        description: Brief overview of the feature
        domain: Industry domain (security, ecommerce, analytics, etc.)
        created_at: Timestamp when scenario was created
        is_custom: True if created by presenter, false if pre-loaded
        workflow_phases: List of workflow phase data
        initial_prompt: Feature description that starts the workflow
        complexity: Scenario complexity level (simple, medium, complex)
        estimated_duration_minutes: Estimated demo duration
        feature_description: Detailed feature description for custom scenarios
        tech_stack: List of technologies used in the scenario
    """

    id: str
    title: str
    description: str
    domain: str
    is_custom: bool = False
    workflow_phases: List[Dict[str, Any]] = field(default_factory=list)
    initial_prompt: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    complexity: str = "medium"
    estimated_duration_minutes: int = 10
    feature_description: Optional[str] = None
    tech_stack: List[str] = field(default_factory=list)

    # Optional preset clarifying questions/answers for demo scenarios.
    # This is used to simulate the clarify phase without requiring user input.
    demo_clarifications: List[Dict[str, str]] = field(default_factory=list)

    # Valid domains for pre-built scenarios (custom scenarios can have any domain)
    VALID_DOMAINS = [
        "security",
        "ecommerce",
        "analytics",
        "infrastructure",
        "data",
        "ui",
        "other",
    ]

    def __post_init__(self) -> None:
        """Validate scenario data after initialization."""
        # Allow alphanumeric, hyphens, and underscores in ID
        id_cleaned = self.id.replace("-", "").replace("_", "")
        if not self.id or not id_cleaned.isalnum():
            raise ValueError(f"Invalid scenario ID: {self.id}")

        if not (5 <= len(self.title) <= 100):
            raise ValueError(f"Title must be 5-100 characters, got {len(self.title)}")

        if not (20 <= len(self.description) <= 500):
            raise ValueError(
                f"Description must be 20-500 characters, got {len(self.description)}"
            )

        # Only validate domain for pre-built scenarios
        if not self.is_custom and self.domain not in self.VALID_DOMAINS:
            raise ValueError(f"Domain must be one of {self.VALID_DOMAINS}, got {self.domain}")
        
        # Validate complexity
        valid_complexities = ["simple", "medium", "complex"]
        if self.complexity not in valid_complexities:
            raise ValueError(f"Complexity must be one of {valid_complexities}")
        
        # Validate duration
        if not (1 <= self.estimated_duration_minutes <= 60):
            raise ValueError("Estimated duration must be between 1 and 60 minutes")
