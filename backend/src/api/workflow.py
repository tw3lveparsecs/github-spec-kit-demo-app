"""
API endpoints for workflow management.
"""

import logging
from datetime import datetime
from flask import jsonify, Response, request

from api import api_bp
from services.scenario_service import ScenarioService
from services.session_service import SessionService
from services.workflow_service import WorkflowService
from services.artifact_generator import ArtifactGenerator

logger = logging.getLogger(__name__)
session_service = SessionService()
scenario_service = ScenarioService()
workflow_service = WorkflowService()
artifact_generator = ArtifactGenerator()


@api_bp.route("/workflow/reset", methods=["POST"])
def reset_workflow() -> Response:
    """
    POST /api/workflow/reset - Reset the demo to initial state.

    Returns:
        JSON response with reset confirmation.
    """
    try:
        # Reset should restore the app to a clean slate, including removing any
        # custom scenarios created during the session.
        scenario_service.clear_custom_scenarios()
        session = session_service.reset_session()
        session.log_action("reset", "Demo reset to initial state")

        return jsonify(
            {"message": "Demo reset successfully", "timestamp": datetime.utcnow().isoformat() + "Z"}
        )
    except Exception as e:
        logger.error(f"Error resetting workflow: {e}")
        raise


@api_bp.route("/session", methods=["GET"])
def get_session() -> Response:
    """
    GET /api/session - Get the current demo session state.

    Returns:
        JSON response with session data.
    """
    try:
        session = session_service.get_current_session()
        return jsonify(session.to_dict())
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise


@api_bp.route("/workflow/<scenario_id>", methods=["GET"])
def get_workflow(scenario_id: str) -> Response:
    """
    GET /api/workflow/{scenarioId} - Get workflow state for a scenario.

    Args:
        scenario_id: The scenario identifier.

    Returns:
        JSON response with workflow state.
    """
    try:
        workflow_state = workflow_service.initialize_workflow(scenario_id)
        return jsonify(workflow_state)
    except ValueError as e:
        logger.warning(f"Workflow not found: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting workflow: {e}")
        raise


@api_bp.route("/workflow/<scenario_id>/step", methods=["POST"])
def advance_workflow(scenario_id: str) -> Response:
    """
    POST /api/workflow/{scenarioId}/step - Advance to next workflow phase.

    Args:
        scenario_id: The scenario identifier.

    Returns:
        JSON response with updated workflow state.
    """
    try:
        workflow_state = workflow_service.advance_phase(scenario_id)
        return jsonify(workflow_state)
    except ValueError as e:
        logger.warning(f"Cannot advance workflow: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error advancing workflow: {e}")
        raise


@api_bp.route("/workflow/<scenario_id>/jump", methods=["POST"])
def jump_workflow(scenario_id: str) -> Response:
    """
    POST /api/workflow/{scenarioId}/jump - Jump to specific workflow phase.

    Args:
        scenario_id: The scenario identifier.

    Request Body:
        {"phase": "specify|clarify|plan|tasks|implement"}

    Returns:
        JSON response with updated workflow state.
    """
    try:
        data = request.get_json()
        target_phase = data.get("phase")

        if not target_phase:
            return jsonify({"error": "Missing 'phase' in request body"}), 400

        workflow_state = workflow_service.jump_to_phase(scenario_id, target_phase)
        return jsonify(workflow_state)
    except ValueError as e:
        logger.warning(f"Cannot jump to phase: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error jumping to phase: {e}")
        raise


@api_bp.route("/workflow/<scenario_id>/input", methods=["POST"])
def submit_phase_input(scenario_id: str) -> Response:
    """
    POST /api/workflow/{scenarioId}/input - Submit user input for current phase.

    This endpoint accepts user input for the current workflow phase and generates
    an artifact based on that input. The input is stored in the session and used
    to create context-aware artifacts.

    Args:
        scenario_id: The scenario identifier.

    Request Body:
        {
            "phase": "specify|clarify|plan|tasks|implement",
            "input": "User's input text for this phase",
            "clarifications": [{"question": "...", "answer": "..."}]  // For clarify phase
        }

    Returns:
        JSON response with generated artifact and updated workflow state.
    """
    try:
        data = request.get_json()
        phase_name = data.get("phase")
        user_input = data.get("input", "")
        clarifications = data.get("clarifications", [])

        if not phase_name:
            return jsonify({"error": "Missing 'phase' in request body"}), 400

        # Store user input in session
        session = session_service.get_current_session()
        
        # Add input to session's phase inputs
        if not hasattr(session, 'phase_inputs') or session.phase_inputs is None:
            session.phase_inputs = {}
        
        session.phase_inputs[phase_name] = {
            "input": user_input,
            "clarifications": clarifications,
            "submitted_at": datetime.utcnow().isoformat() + "Z"
        }
        
        session.log_action("phase_input", f"User input submitted for {phase_name}")

        # Generate artifact based on phase and input
        artifact = workflow_service.generate_artifact_with_input(
            scenario_id, 
            phase_name, 
            user_input,
            clarifications,
            session.phase_inputs
        )

        # Persist the generated artifact for later phases to reference as context
        try:
            session.phase_inputs.setdefault(phase_name, {})
            session.phase_inputs[phase_name]["artifact"] = artifact
            session.phase_inputs[phase_name]["artifact_markdown"] = artifact.get("content_markdown", "")
        except Exception as e:
            logger.warning(f"Failed to persist artifact in session for {phase_name}: {e}")

        logger.info(f"Generated artifact for phase {phase_name} with user input")

        return jsonify({
            "artifact": artifact,
            "phase": phase_name,
            "input_received": True,
            "session_id": str(session.session_id)
        })

    except ValueError as e:
        logger.warning(f"Cannot process phase input: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error processing phase input: {e}")
        raise


@api_bp.route("/workflow/<scenario_id>/artifact/<phase_name>", methods=["GET"])
def generate_artifact_for_phase(scenario_id: str, phase_name: str) -> Response:
    """
    GET /api/workflow/{scenarioId}/artifact/{phaseName} - Generate artifact for a phase.

    Generates an artifact for the specified phase, incorporating context from
    all previous phases including user inputs.

    Args:
        scenario_id: The scenario identifier.
        phase_name: The phase name (specify, clarify, plan, tasks, implement).

    Returns:
        JSON response with generated artifact including previous context.
    """
    try:
        session = session_service.get_current_session()
        phase_inputs = getattr(session, 'phase_inputs', {}) or {}
        
        artifact = workflow_service.generate_artifact_with_context(
            scenario_id, phase_name, phase_inputs
        )

        # Persist the generated artifact for later phases to reference as context.
        # This is important for demo scenarios where phases advance without explicit POSTed input.
        if not hasattr(session, 'phase_inputs') or session.phase_inputs is None:
            session.phase_inputs = {}
        session.phase_inputs.setdefault(phase_name, {})
        session.phase_inputs[phase_name].setdefault("clarifications", phase_inputs.get(phase_name, {}).get("clarifications", []))
        session.phase_inputs[phase_name].setdefault("input", phase_inputs.get(phase_name, {}).get("input", ""))
        session.phase_inputs[phase_name]["artifact"] = artifact
        session.phase_inputs[phase_name]["artifact_markdown"] = artifact.get("content_markdown", "")

        logger.info(f"Generated artifact for phase {phase_name} with context")

        return jsonify({
            "artifact": artifact,
            "phase": phase_name,
            "context_from_phases": list(phase_inputs.keys()),
            "session_id": str(session.session_id)
        })

    except ValueError as e:
        logger.warning(f"Cannot generate artifact: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error generating artifact: {e}")
        raise


@api_bp.route("/workflow/<scenario_id>/inputs", methods=["GET"])
def get_phase_inputs(scenario_id: str) -> Response:
    """
    GET /api/workflow/{scenarioId}/inputs - Get all user inputs for the workflow.

    Returns all inputs submitted by the user across all phases for this scenario.

    Args:
        scenario_id: The scenario identifier.

    Returns:
        JSON response with all phase inputs.
    """
    try:
        session = session_service.get_current_session()
        phase_inputs = getattr(session, 'phase_inputs', {}) or {}
        
        return jsonify({
            "scenario_id": scenario_id,
            "phase_inputs": phase_inputs,
            "session_id": str(session.session_id)
        })
    except Exception as e:
        logger.error(f"Error getting phase inputs: {e}")
        raise
