"""
Constitution models for representing AI assistant principles and checks.

These models support the Constitution Showcase feature (User Story 3) which
demonstrates how GitHub Spec Kit enforces quality standards during the workflow.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from models import BaseModel


@dataclass
class ConstitutionPrinciple(BaseModel):
    """
    Represents a core principle from the Spec Kit constitution.
    
    A principle defines a quality standard or best practice that should
    be followed during feature development (e.g., performance, security).
    """
    
    principle_id: str  # Unique identifier (e.g., "performance", "security")
    title: str  # Display title (e.g., "Performance Optimization")
    description: str  # Full description of the principle
    category: str  # Category (technical, user-experience, security, maintainability)
    priority: int  # Priority level (1-5, where 1 is highest)
    examples: List[str]  # List of example guidelines
    
    def __post_init__(self):
        """Validate principle data after initialization."""
        if not self.principle_id or len(self.principle_id) < 2:
            raise ValueError("Principle ID must be at least 2 characters")
        if not self.title or len(self.title) < 3:
            raise ValueError("Title must be at least 3 characters")
        if not self.description or len(self.description) < 10:
            raise ValueError("Description must be at least 10 characters")
        if self.priority < 1 or self.priority > 5:
            raise ValueError("Priority must be between 1 and 5")
        
        valid_categories = ["technical", "user-experience", "security", "maintainability"]
        if self.category not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")


@dataclass
class ConstitutionCheck(BaseModel):
    """
    Represents a specific check performed against an artifact.
    
    A check evaluates whether an artifact (e.g., implementation plan)
    adheres to a specific constitution principle.
    """
    
    check_id: str  # Unique identifier
    principle_id: str  # Associated principle
    artifact_type: str  # Type of artifact checked (plan, spec, tasks, implement)
    check_name: str  # Name of the check
    check_description: str  # What the check validates
    status: str  # Status: not_run, passed, failed, warning
    evaluated_at: Optional[datetime] = None  # When the check was performed
    violations: List['ConstitutionViolation'] = None  # List of violations found
    
    def __post_init__(self):
        """Validate check data after initialization."""
        if not self.check_id or len(self.check_id) < 3:
            raise ValueError("Check ID must be at least 3 characters")
        if not self.principle_id:
            raise ValueError("Principle ID is required")
        if not self.check_name or len(self.check_name) < 5:
            raise ValueError("Check name must be at least 5 characters")
        
        valid_artifact_types = ["plan", "spec", "tasks", "implement"]
        if self.artifact_type not in valid_artifact_types:
            raise ValueError(f"Artifact type must be one of: {', '.join(valid_artifact_types)}")
        
        valid_statuses = ["not_run", "passed", "failed", "warning"]
        if self.status not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        
        if self.violations is None:
            self.violations = []


@dataclass
class ConstitutionViolation(BaseModel):
    """
    Represents a violation of a constitution principle found during a check.
    
    Violations indicate specific instances where an artifact does not
    meet the standards defined in the constitution.
    """
    
    violation_id: str  # Unique identifier
    check_id: str  # Associated check
    severity: str  # Severity: critical, high, medium, low, info
    message: str  # Human-readable violation message
    location: Optional[str] = None  # Where in the artifact (e.g., "Line 45")
    recommendation: Optional[str] = None  # Suggested fix
    detected_at: Optional[datetime] = None  # When violation was detected
    
    def __post_init__(self):
        """Validate violation data after initialization."""
        if not self.violation_id:
            raise ValueError("Violation ID is required")
        # check_id can be empty initially and set after parent check is created
        if not self.message or len(self.message) < 10:
            raise ValueError("Message must be at least 10 characters")
        
        valid_severities = ["critical", "high", "medium", "low", "info"]
        if self.severity not in valid_severities:
            raise ValueError(f"Severity must be one of: {', '.join(valid_severities)}")
        
        if self.detected_at is None:
            self.detected_at = datetime.utcnow()
