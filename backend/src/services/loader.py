"""
File-based scenario loader utility for the demo application.

This module provides functionality to load demo scenarios from JSON files
in the backend/data/scenarios/ directory.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ScenarioLoader:
    """Loads demo scenarios from JSON files."""

    def __init__(self, scenarios_dir: Optional[Path] = None) -> None:
        """
        Initialize the scenario loader.

        Args:
            scenarios_dir: Path to the scenarios directory. If None, uses default location.
        """
        if scenarios_dir is None:
            # Default to backend/data/scenarios/ relative to this file
            base_dir = Path(__file__).parent.parent.parent
            self.scenarios_dir = base_dir / "data" / "scenarios"
        else:
            self.scenarios_dir = scenarios_dir

        logger.info(f"ScenarioLoader initialized with directory: {self.scenarios_dir}")

    def load_scenario(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a single scenario by ID from its JSON file.

        Args:
            scenario_id: The scenario identifier (e.g., "user-authentication").

        Returns:
            Dictionary containing the scenario data, or None if not found.
        """
        scenario_file = self.scenarios_dir / f"{scenario_id}.json"

        if not scenario_file.exists():
            logger.warning(f"Scenario file not found: {scenario_file}")
            return None

        try:
            with open(scenario_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"Loaded scenario: {scenario_id}")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse scenario file {scenario_file}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading scenario {scenario_id}: {e}")
            return None

    def load_all_scenarios(self) -> List[Dict[str, Any]]:
        """
        Load all scenario files from the scenarios directory.

        Returns:
            List of scenario dictionaries.
        """
        scenarios = []

        if not self.scenarios_dir.exists():
            logger.warning(f"Scenarios directory does not exist: {self.scenarios_dir}")
            return scenarios

        for scenario_file in self.scenarios_dir.glob("*.json"):
            scenario_id = scenario_file.stem
            scenario_data = self.load_scenario(scenario_id)
            if scenario_data:
                scenarios.append(scenario_data)

        logger.info(f"Loaded {len(scenarios)} scenarios")
        return scenarios

    def scenario_exists(self, scenario_id: str) -> bool:
        """
        Check if a scenario file exists.

        Args:
            scenario_id: The scenario identifier to check.

        Returns:
            True if the scenario file exists, False otherwise.
        """
        scenario_file = self.scenarios_dir / f"{scenario_id}.json"
        return scenario_file.exists()
