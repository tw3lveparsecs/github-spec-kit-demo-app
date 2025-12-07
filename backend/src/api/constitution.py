"""
API endpoints for constitution showcase feature.
"""

import logging
from flask import jsonify, Response

from api import api_bp
from services.constitution_service import ConstitutionService

logger = logging.getLogger(__name__)

# Initialize constitution service
constitution_service = ConstitutionService()


@api_bp.route("/constitution", methods=["GET"])
def get_constitution() -> Response:
    """
    GET /api/constitution - Get all constitution principles.

    Returns:
        JSON response with list of constitution principles.
    """
    try:
        principles = constitution_service.get_principles()
        
        # Convert to dictionaries for JSON serialization
        principles_data = [p.to_dict() for p in principles]
        
        return jsonify({
            "principles": principles_data,
            "total": len(principles_data)
        })
    except Exception as e:
        logger.error(f"Error getting constitution principles: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/constitution/check/<artifact_id>", methods=["GET"])
def check_constitution(artifact_id: str) -> Response:
    """
    GET /api/constitution/check/{artifactId} - Check an artifact against constitution.

    Args:
        artifact_id: The artifact identifier (format: {scenarioId}-{artifactType}).

    Returns:
        JSON response with constitution check results.
    """
    try:
        # Parse artifact_id to get type (e.g., "user-authentication-plan")
        parts = artifact_id.rsplit("-", 1)
        if len(parts) == 2:
            scenario_id, artifact_type = parts
        else:
            artifact_type = "plan"  # Default to plan
            scenario_id = artifact_id
        
        # Validate artifact type
        valid_types = ["spec", "plan", "tasks", "implement"]
        if artifact_type not in valid_types:
            artifact_type = "plan"
        
        # Perform constitution checks (uses simulated content for demo)
        checks = constitution_service.evaluate_checks(
            artifact_content="",  # Content not needed for demo simulation
            artifact_type=artifact_type
        )
        
        # Get check summary
        summary = constitution_service.get_check_summary(checks)
        
        # Convert checks to dictionaries (BaseModel.to_dict handles nested violations)
        checks_data = [check.to_dict() for check in checks]
        
        return jsonify({
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "checks": checks_data,
            "summary": summary
        })
    except Exception as e:
        logger.error(f"Error checking constitution for artifact {artifact_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/constitution/principles/<principle_id>", methods=["GET"])
def get_principle(principle_id: str) -> Response:
    """
    GET /api/constitution/principles/{principleId} - Get a specific principle.

    Args:
        principle_id: The principle identifier (e.g., "performance", "security").

    Returns:
        JSON response with principle details.
    """
    try:
        principles = constitution_service.get_principles()
        
        # Find the requested principle
        principle = next((p for p in principles if p.principle_id == principle_id), None)
        
        if not principle:
            return jsonify({"error": f"Principle '{principle_id}' not found"}), 404
        
        return jsonify(principle.to_dict())
    except Exception as e:
        logger.error(f"Error getting principle {principle_id}: {e}")
        return jsonify({"error": str(e)}), 500
