"""
ScenarioService for managing demo scenarios.
"""

import logging
import re
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.demo_scenario import DemoScenario
from services.loader import ScenarioLoader

logger = logging.getLogger(__name__)


class ScenarioService:
    """Service for managing demo scenarios."""

    # Custom scenarios stored in memory for the demo (in production, use DB)
    _custom_scenarios: Dict[str, DemoScenario] = {}

    def __init__(self) -> None:
        """Initialize the scenario service with a loader."""
        self.loader = ScenarioLoader()

    def list_scenarios(self) -> List[DemoScenario]:
        """
        Get all available demo scenarios.

        Returns:
            List of DemoScenario objects.
        """
        scenarios_data = self.loader.load_all_scenarios()
        scenarios = []

        for data in scenarios_data:
            try:
                # Convert datetime string to datetime object if needed
                if isinstance(data.get("created_at"), str):
                    data["created_at"] = datetime.fromisoformat(data["created_at"].rstrip("Z"))
                elif "created_at" not in data:
                    data["created_at"] = datetime.utcnow()

                scenario = DemoScenario(**data)
                scenarios.append(scenario)
            except Exception as e:
                logger.error(f"Failed to create scenario from data: {e}")
                continue

        logger.info(f"Listed {len(scenarios)} scenarios")
        return scenarios

    def get_scenario_by_id(self, scenario_id: str) -> Optional[DemoScenario]:
        """
        Get a specific scenario by its ID.

        Args:
            scenario_id: The scenario identifier.

        Returns:
            DemoScenario object or None if not found.
        """
        # Custom scenarios are stored in memory (no JSON file).
        custom = self._custom_scenarios.get(scenario_id)
        if custom is not None:
            logger.info(f"Retrieved custom scenario: {scenario_id}")
            return custom

        scenario_data = self.loader.load_scenario(scenario_id)

        if not scenario_data:
            logger.warning(f"Scenario not found: {scenario_id}")
            return None

        try:
            # Convert datetime string to datetime object if needed
            if isinstance(scenario_data.get("created_at"), str):
                scenario_data["created_at"] = datetime.fromisoformat(
                    scenario_data["created_at"].rstrip("Z")
                )
            elif "created_at" not in scenario_data:
                scenario_data["created_at"] = datetime.utcnow()

            scenario = DemoScenario(**scenario_data)
            logger.info(f"Retrieved scenario: {scenario_id}")
            return scenario
        except Exception as e:
            logger.error(f"Failed to create scenario {scenario_id}: {e}")
            return None

    def validate_custom_scenario(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate custom scenario input data.
        
        Args:
            data: Dictionary with custom scenario fields.
            
        Returns:
            Dictionary with 'valid' bool and 'errors' list.
        """
        errors = []
        
        # Required fields validation
        title = data.get("title", "").strip()
        if not title:
            errors.append("Title is required")
        elif len(title) < 5:
            errors.append("Title must be at least 5 characters")
        elif len(title) > 100:
            errors.append("Title must not exceed 100 characters")
        
        description = data.get("description", "").strip()
        if not description:
            errors.append("Description is required")
        elif len(description) < 20:
            errors.append("Description must be at least 20 characters")
        elif len(description) > 500:
            errors.append("Description must not exceed 500 characters")
        
        domain = data.get("domain", "").strip()
        if not domain:
            errors.append("Domain/Industry is required")
        elif len(domain) < 3:
            errors.append("Domain must be at least 3 characters")
        elif len(domain) > 50:
            errors.append("Domain must not exceed 50 characters")
        
        # Optional fields validation
        feature_description = data.get("feature_description", "").strip()
        if feature_description and len(feature_description) > 2000:
            errors.append("Feature description must not exceed 2000 characters")
        
        tech_stack = data.get("tech_stack", [])
        if tech_stack and not isinstance(tech_stack, list):
            errors.append("Tech stack must be a list")
        elif len(tech_stack) > 10:
            errors.append("Tech stack must not exceed 10 items")
        
        # Sanitize title for ID generation
        if title:
            # Check for valid characters
            sanitized = re.sub(r'[^a-zA-Z0-9\s-]', '', title)
            if sanitized != title.replace('_', ' '):
                logger.info("Title contains special characters that will be sanitized")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def create_custom_scenario(self, data: Dict[str, Any]) -> DemoScenario:
        """
        Create a custom scenario from user input.
        
        Args:
            data: Validated custom scenario data.
            
        Returns:
            Created DemoScenario object.
            
        Raises:
            ValueError: If validation fails.
        """
        # Validate first
        validation = self.validate_custom_scenario(data)
        if not validation["valid"]:
            raise ValueError(f"Validation failed: {', '.join(validation['errors'])}")
        
        # Generate unique ID
        title = data.get("title", "").strip()
        base_id = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        scenario_id = f"custom-{base_id}-{uuid.uuid4().hex[:6]}"
        
        # Create default workflow phases
        default_phases = [
            {
                "phase_name": "specify",
                "display_name": "Specification",
                "description": "Define the feature requirements and acceptance criteria",
                "talking_points": [
                    "Starting with clear requirements prevents scope creep",
                    "User stories help focus on outcomes, not implementation"
                ],
                "artifact_type": "spec",
                "duration_estimate_seconds": 45
            },
            {
                "phase_name": "clarify",
                "display_name": "Clarification",
                "description": "AI asks clarifying questions to refine the specification",
                "talking_points": [
                    "Clarifying questions reveal hidden assumptions",
                    "Better questions lead to better implementations"
                ],
                "artifact_type": "clarification",
                "duration_estimate_seconds": 30
            },
            {
                "phase_name": "plan",
                "display_name": "Planning",
                "description": "Generate the implementation plan with architecture decisions",
                "talking_points": [
                    "Constitution principles guide architectural decisions",
                    "The plan becomes the source of truth for implementation"
                ],
                "artifact_type": "plan",
                "duration_estimate_seconds": 60
            },
            {
                "phase_name": "tasks",
                "display_name": "Tasks",
                "description": "Break down the plan into actionable development tasks",
                "talking_points": [
                    "Tasks are small enough to complete in one session",
                    "Dependencies are clearly marked for parallel execution"
                ],
                "artifact_type": "tasks",
                "duration_estimate_seconds": 45
            },
            {
                "phase_name": "implement",
                "display_name": "Implementation",
                "description": "Execute tasks with AI-assisted code generation",
                "talking_points": [
                    "Each task is implemented following the established plan",
                    "Tests are written alongside implementation"
                ],
                "artifact_type": "implementation",
                "duration_estimate_seconds": 90
            }
        ]
        
        # Create the scenario
        scenario = DemoScenario(
            id=scenario_id,
            title=title,
            description=data.get("description", "").strip(),
            domain=data.get("domain", "Custom").strip(),
            complexity="medium",
            estimated_duration_minutes=15,
            created_at=datetime.utcnow(),
            feature_description=data.get("feature_description", "").strip() or None,
            tech_stack=data.get("tech_stack", []),
            workflow_phases=default_phases,
            is_custom=True
        )
        
        # Store in memory
        self._custom_scenarios[scenario_id] = scenario
        logger.info(f"Created custom scenario: {scenario_id}")
        
        return scenario

    def list_custom_scenarios(self) -> List[DemoScenario]:
        """
        Get all custom scenarios created in this session.
        
        Returns:
            List of custom DemoScenario objects.
        """
        return list(self._custom_scenarios.values())

    def delete_custom_scenario(self, scenario_id: str) -> bool:
        """
        Delete a custom scenario.
        
        Args:
            scenario_id: The custom scenario ID.
            
        Returns:
            True if deleted, False if not found.
        """
        if scenario_id in self._custom_scenarios:
            del self._custom_scenarios[scenario_id]
            logger.info(f"Deleted custom scenario: {scenario_id}")
            return True
        return False

    def clear_custom_scenarios(self) -> int:
        """Remove all custom scenarios created in this process.

        Returns:
            Number of custom scenarios removed.
        """
        removed = len(self._custom_scenarios)
        self._custom_scenarios.clear()
        if removed:
            logger.info(f"Cleared {removed} custom scenario(s)")
        return removed
