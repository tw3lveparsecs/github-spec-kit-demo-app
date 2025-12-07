"""
API endpoints for workflow management.
"""

import logging
from datetime import datetime
from flask import jsonify, Response, request

from api import api_bp
from services.session_service import SessionService
from services.workflow_service import WorkflowService

logger = logging.getLogger(__name__)
session_service = SessionService()
workflow_service = WorkflowService()


@api_bp.route("/workflow/reset", methods=["POST"])
def reset_workflow() -> Response:
    """
    POST /api/workflow/reset - Reset the demo to initial state.

    Returns:
        JSON response with reset confirmation.
    """
    try:
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
