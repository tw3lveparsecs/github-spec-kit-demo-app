"""
API endpoints for scenario management.
"""

import logging
from flask import jsonify, Response, request
from werkzeug.exceptions import NotFound, BadRequest

from api import api_bp
from services.scenario_service import ScenarioService

logger = logging.getLogger(__name__)
scenario_service = ScenarioService()


@api_bp.route("/scenarios", methods=["GET"])
def list_scenarios() -> Response:
    """
    GET /api/scenarios - List all demo scenarios.

    Returns:
        JSON response with list of scenarios.
    """
    try:
        scenarios = scenario_service.list_scenarios()
        custom_scenarios = scenario_service.list_custom_scenarios()
        all_scenarios = scenarios + custom_scenarios
        return jsonify(
            {"scenarios": [scenario.to_dict() for scenario in all_scenarios], "total": len(all_scenarios)}
        )
    except Exception as e:
        logger.error(f"Error listing scenarios: {e}")
        raise


@api_bp.route("/scenarios/<scenario_id>", methods=["GET"])
def get_scenario(scenario_id: str) -> Response:
    """
    GET /api/scenarios/{scenarioId} - Get a specific scenario.

    Args:
        scenario_id: The scenario identifier.

    Returns:
        JSON response with scenario details.

    Raises:
        NotFound: If scenario doesn't exist.
    """
    try:
        scenario = scenario_service.get_scenario_by_id(scenario_id)

        if scenario is None:
            raise NotFound(f"Scenario not found: {scenario_id}")

        return jsonify(scenario.to_dict())
    except NotFound:
        raise
    except Exception as e:
        logger.error(f"Error getting scenario {scenario_id}: {e}")
        raise


@api_bp.route("/scenarios/custom", methods=["POST"])
def create_custom_scenario() -> Response:
    """
    POST /api/scenarios/custom - Create a custom demo scenario.
    
    Request Body:
        {
            "title": "Feature Title",
            "description": "Feature description (20-500 chars)",
            "domain": "Industry/Domain",
            "feature_description": "Optional detailed description",
            "tech_stack": ["Python", "Flask"]
        }
    
    Returns:
        JSON response with created scenario.
        
    Raises:
        BadRequest: If validation fails.
    """
    try:
        data = request.get_json()
        
        if not data:
            raise BadRequest("Request body is required")
        
        # Validate the input
        validation = scenario_service.validate_custom_scenario(data)
        if not validation["valid"]:
            return jsonify({
                "error": "Validation failed",
                "errors": validation["errors"]
            }), 400
        
        # Create the scenario
        scenario = scenario_service.create_custom_scenario(data)
        
        logger.info(f"Created custom scenario: {scenario.id}")
        
        return jsonify({
            "scenario": scenario.to_dict(),
            "message": "Custom scenario created successfully"
        }), 201
        
    except ValueError as e:
        logger.warning(f"Validation error creating custom scenario: {e}")
        raise BadRequest(str(e))
    except Exception as e:
        logger.error(f"Error creating custom scenario: {e}")
        raise


@api_bp.route("/scenarios/custom/validate", methods=["POST"])
def validate_custom_scenario() -> Response:
    """
    POST /api/scenarios/custom/validate - Validate custom scenario data.
    
    Request Body:
        Same as POST /api/scenarios/custom
    
    Returns:
        JSON response with validation result.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "valid": False,
                "errors": ["Request body is required"]
            })
        
        validation = scenario_service.validate_custom_scenario(data)
        return jsonify(validation)
        
    except Exception as e:
        logger.error(f"Error validating custom scenario: {e}")
        return jsonify({
            "valid": False,
            "errors": [str(e)]
        })


@api_bp.route("/scenarios/custom/<scenario_id>", methods=["DELETE"])
def delete_custom_scenario(scenario_id: str) -> Response:
    """
    DELETE /api/scenarios/custom/{scenarioId} - Delete a custom scenario.
    
    Args:
        scenario_id: The custom scenario identifier.
    
    Returns:
        JSON response with deletion status.
        
    Raises:
        NotFound: If custom scenario doesn't exist.
    """
    try:
        deleted = scenario_service.delete_custom_scenario(scenario_id)
        
        if not deleted:
            raise NotFound(f"Custom scenario not found: {scenario_id}")
        
        return jsonify({
            "message": "Custom scenario deleted successfully",
            "scenario_id": scenario_id
        })
        
    except NotFound:
        raise
    except Exception as e:
        logger.error(f"Error deleting custom scenario {scenario_id}: {e}")
        raise
