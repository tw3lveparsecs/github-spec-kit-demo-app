"""
WorkflowService for managing demo workflow progression.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from models.workflow_phase import WorkflowPhase
from models.demo_scenario import DemoScenario
from models.generated_artifact import GeneratedArtifact
from services.scenario_service import ScenarioService
from services.session_service import SessionService
from services.constitution_service import ConstitutionService
from services.artifact_generator import ArtifactGenerator

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service for managing workflow phase progression."""

    def __init__(self):
        """Initialize workflow service with dependencies."""
        self.scenario_service = ScenarioService()
        self.session_service = SessionService()
        self.constitution_service = ConstitutionService()
        self.artifact_generator = ArtifactGenerator()

    def initialize_workflow(self, scenario_id: str) -> Dict[str, Any]:
        """
        Initialize workflow for a scenario.

        Args:
            scenario_id: The scenario identifier.

        Returns:
            Dictionary with workflow state and first phase.

        Raises:
            ValueError: If scenario not found.
        """
        scenario = self.scenario_service.get_scenario_by_id(scenario_id)
        if scenario is None:
            raise ValueError(f"Scenario not found: {scenario_id}")

        # Update session with current scenario
        session = self.session_service.get_current_session()
        self.session_service.update_session(scenario_id, "specify")

        # Get first phase
        first_phase = scenario.workflow_phases[0] if scenario.workflow_phases else None

        logger.info(f"Initialized workflow for scenario: {scenario_id}")

        return {
            "scenario": scenario.to_dict(),
            "current_phase": first_phase if first_phase else None,
            "phase_index": 0,
            "total_phases": len(scenario.workflow_phases),
            "session_id": str(session.session_id),
        }

    def advance_phase(self, scenario_id: str) -> Dict[str, Any]:
        """
        Advance to the next workflow phase.

        Args:
            scenario_id: The scenario identifier.

        Returns:
            Dictionary with updated workflow state.

        Raises:
            ValueError: If scenario not found or already at last phase.
        """
        scenario = self.scenario_service.get_scenario_by_id(scenario_id)
        if scenario is None:
            raise ValueError(f"Scenario not found: {scenario_id}")

        session = self.session_service.get_current_session()
        current_phase = session.current_phase_name or "specify"

        # Find current phase index
        phase_names = [phase["phase_name"] for phase in scenario.workflow_phases]
        try:
            current_index = phase_names.index(current_phase)
        except ValueError:
            current_index = 0

        # Check if we can advance
        if current_index >= len(scenario.workflow_phases) - 1:
            raise ValueError("Already at final phase")

        # Advance to next phase
        next_index = current_index + 1
        next_phase = scenario.workflow_phases[next_index]
        next_phase_name = next_phase["phase_name"]

        # Generate artifact from previous phase's input (if any)
        previous_artifact = None
        phase_inputs = getattr(session, 'phase_inputs', {}) or {}
        if current_phase in phase_inputs:
            previous_artifact = self._generate_artifact_from_input(
                scenario, current_phase, phase_inputs
            )

        # Update session
        self.session_service.update_session(scenario_id, next_phase_name)
        session.log_action("phase_advance", f"Advanced to {next_phase_name}")

        logger.info(f"Advanced to phase {next_phase_name} for scenario {scenario_id}")

        # Run constitution check when leaving the plan phase
        constitution_check = None
        if current_phase == "plan":
            constitution_check = self._run_constitution_check_for_phase(scenario_id, current_phase)

        return {
            "scenario": scenario.to_dict(),
            "current_phase": next_phase,
            "phase_index": next_index,
            "total_phases": len(scenario.workflow_phases),
            "session_id": str(session.session_id),
            "constitution_check": constitution_check,
            "previous_phase_artifact": previous_artifact,
            "previous_phase_input": phase_inputs.get(current_phase),
        }

    def _generate_artifact_from_input(
        self, 
        scenario: DemoScenario, 
        phase_name: str, 
        phase_inputs: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate an artifact from the user's input for a specific phase.

        Args:
            scenario: The demo scenario.
            phase_name: The phase name.
            phase_inputs: Dictionary of all phase inputs.

        Returns:
            Dictionary with artifact data or None.
        """
        try:
            phase_data = phase_inputs.get(phase_name, {})
            user_input = phase_data.get("input", "")
            clarifications = phase_data.get("clarifications", [])

            # Build context
            context = self._build_artifact_context(
                scenario, phase_name, user_input, clarifications, phase_inputs
            )

            # Generate artifact
            artifact = self.artifact_generator.generate_with_context(
                phase_name, scenario, context
            )

            return artifact.to_dict() if hasattr(artifact, 'to_dict') else artifact
        except Exception as e:
            logger.warning(f"Failed to generate artifact from input: {e}")
            return None

    def _run_constitution_check_for_phase(
        self, scenario_id: str, phase_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Run constitution check for artifacts generated in a phase.

        Args:
            scenario_id: The scenario identifier.
            phase_name: The phase name to check.

        Returns:
            Dictionary with check results or None if no artifact found.
        """
        try:
            # Get the artifact for this phase
            artifact_id = f"{scenario_id}_{phase_name}"
            check_result = self.constitution_service.run_check(artifact_id)
            
            logger.info(f"Constitution check for {artifact_id}: {check_result.get('summary', {})}")
            return check_result
        except Exception as e:
            logger.warning(f"Failed to run constitution check: {e}")
            return None

    def jump_to_phase(self, scenario_id: str, target_phase: str) -> Dict[str, Any]:
        """
        Jump directly to a specific workflow phase.

        Args:
            scenario_id: The scenario identifier.
            target_phase: The phase name to jump to.

        Returns:
            Dictionary with updated workflow state.

        Raises:
            ValueError: If scenario or phase not found.
        """
        scenario = self.scenario_service.get_scenario_by_id(scenario_id)
        if scenario is None:
            raise ValueError(f"Scenario not found: {scenario_id}")

        # Find target phase
        phase_names = [phase["phase_name"] for phase in scenario.workflow_phases]
        try:
            target_index = phase_names.index(target_phase)
        except ValueError:
            raise ValueError(f"Phase not found: {target_phase}")

        target_phase_data = scenario.workflow_phases[target_index]

        # Update session
        session = self.session_service.get_current_session()
        self.session_service.update_session(scenario_id, target_phase)
        session.log_action("phase_jump", f"Jumped to {target_phase}")

        logger.info(f"Jumped to phase {target_phase} for scenario {scenario_id}")

        return {
            "scenario": scenario.to_dict(),
            "current_phase": target_phase_data,
            "phase_index": target_index,
            "total_phases": len(scenario.workflow_phases),
            "session_id": str(session.session_id),
        }

    def generate_artifact_with_input(
        self,
        scenario_id: str,
        phase_name: str,
        user_input: str,
        clarifications: List[Dict[str, str]] = None,
        all_phase_inputs: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate an artifact based on user input for a specific phase.

        This method creates context-aware artifacts that incorporate the user's
        input from the current phase and any previous phases.

        Args:
            scenario_id: The scenario identifier.
            phase_name: The current phase name.
            user_input: The user's input text for this phase.
            clarifications: List of Q&A pairs for clarify phase.
            all_phase_inputs: Dictionary of all inputs from previous phases.

        Returns:
            Dictionary with the generated artifact.

        Raises:
            ValueError: If scenario not found.
        """
        scenario = self.scenario_service.get_scenario_by_id(scenario_id)
        if scenario is None:
            raise ValueError(f"Scenario not found: {scenario_id}")

        if clarifications is None:
            clarifications = []
        if all_phase_inputs is None:
            all_phase_inputs = {}

        # Build context from all phase inputs
        context = self._build_artifact_context(
            scenario, phase_name, user_input, clarifications, all_phase_inputs
        )

        # Generate artifact based on phase
        artifact = self.artifact_generator.generate_with_context(
            phase_name, scenario, context
        )

        logger.info(f"Generated {phase_name} artifact with user input for {scenario_id}")

        return artifact.to_dict() if hasattr(artifact, 'to_dict') else artifact

    def generate_artifact_with_context(
        self,
        scenario_id: str,
        phase_name: str,
        all_phase_inputs: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate an artifact for a phase with context from all previous phases.

        This method creates context-aware artifacts that incorporate user inputs
        from all previous phases to provide continuity.

        Args:
            scenario_id: The scenario identifier.
            phase_name: The phase to generate artifact for.
            all_phase_inputs: Dictionary of all inputs from previous phases.

        Returns:
            Dictionary with the generated artifact.

        Raises:
            ValueError: If scenario not found.
        """
        scenario = self.scenario_service.get_scenario_by_id(scenario_id)
        if scenario is None:
            raise ValueError(f"Scenario not found: {scenario_id}")

        if all_phase_inputs is None:
            all_phase_inputs = {}

        # Get current phase input if any
        current_input = all_phase_inputs.get(phase_name, {})
        user_input = current_input.get("input", "")
        clarifications = current_input.get("clarifications", [])

        # Build context from all phase inputs
        context = self._build_artifact_context(
            scenario, phase_name, user_input, clarifications, all_phase_inputs
        )

        # Generate artifact based on phase
        artifact = self.artifact_generator.generate_with_context(
            phase_name, scenario, context
        )

        logger.info(f"Generated {phase_name} artifact with context for {scenario_id}")

        return artifact.to_dict() if hasattr(artifact, 'to_dict') else artifact

    def _build_artifact_context(
        self,
        scenario: DemoScenario,
        phase_name: str,
        user_input: str,
        clarifications: List[Dict[str, str]],
        all_phase_inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build context dictionary for artifact generation.

        Combines scenario data, user inputs from all phases, and current input
        to create a comprehensive context for artifact generation.
        """
        # Get previous phase inputs and (optionally) previously generated artifacts.
        # For demo scenarios, phases often have no explicit input, so we store and reuse
        # the artifact markdown as the contextual output of that phase.
        specify_input = all_phase_inputs.get("specify", {}).get("input", "")
        plan_input = all_phase_inputs.get("plan", {}).get("input", "")
        tasks_input = all_phase_inputs.get("tasks", {}).get("input", "")

        def _strip_previous_context_block(markdown: str) -> str:
            marker = "## 📋 Previous Context"
            if not markdown or marker not in markdown:
                return markdown

            start = markdown.find(marker)
            if start == -1:
                return markdown

            sep_start = markdown.find("\n---", start)
            if sep_start == -1:
                return markdown[:start].rstrip()

            sep_line_end = markdown.find("\n", sep_start + 1)
            if sep_line_end == -1:
                return markdown[:start].rstrip()

            before = markdown[:start].rstrip()
            after = markdown[sep_line_end + 1 :].lstrip()
            if before and after:
                return before + "\n\n" + after
            return before or after

        plan_artifact_markdown = _strip_previous_context_block(
            all_phase_inputs.get("plan", {}).get("artifact_markdown", "")
        )
        tasks_artifact_markdown = _strip_previous_context_block(
            all_phase_inputs.get("tasks", {}).get("artifact_markdown", "")
        )

        # Build formatted clarifications
        effective_clarifications = clarifications or []

        # For demo scenarios, allow preset clarifications to simulate the clarify phase
        # even when the user hasn't submitted any inputs.
        if (
            not scenario.is_custom
            and not effective_clarifications
            and getattr(scenario, "demo_clarifications", None)
            and phase_name in {"clarify", "plan", "tasks", "implement"}
        ):
            effective_clarifications = scenario.demo_clarifications

        formatted_clarifications = ""
        if effective_clarifications:
            qa_pairs = [
                f"**Q:** {c.get('question', '')}\n**A:** {c.get('answer', '')}"
                for c in effective_clarifications
                if c.get("answer")
            ]
            formatted_clarifications = "\n\n".join(qa_pairs)

        context = {
            "title": scenario.title,
            "description": scenario.description,
            "domain": scenario.domain,
            "initial_prompt": scenario.initial_prompt,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "current_phase": phase_name,
            "user_input": user_input,
            "specify_input": specify_input or scenario.initial_prompt,
            "clarifications": formatted_clarifications,
            "clarifications_list": effective_clarifications,
            # Prefer previous phase artifact output when available.
            "plan_input": plan_artifact_markdown or plan_input,
            "tasks_input": tasks_artifact_markdown or tasks_input,
            "tech_stack": ", ".join(getattr(scenario, 'tech_stack', []) or []),
        }

        return context
