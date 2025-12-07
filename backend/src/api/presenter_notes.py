"""
Presenter Notes API endpoints.

Provides endpoints for retrieving presenter notes for demo talking points.
"""

from flask import Response, jsonify, request

from api import api_bp
from services.presenter_note_service import get_presenter_note_service


@api_bp.route("/presenter-notes", methods=["GET"])
def list_presenter_notes() -> Response:
    """List all presenter notes.
    
    Query Parameters:
        context_type: Optional filter by context type (phase, scenario, feature).
        
    Returns:
        JSON array of presenter notes.
    """
    service = get_presenter_note_service()
    context_type = request.args.get("context_type")
    
    if context_type:
        notes = service.get_notes_by_type(context_type)
    else:
        notes = service.get_all_notes()
    
    return jsonify([note.to_dict() for note in notes])


@api_bp.route("/presenter-notes/<context_type>/<context_id>", methods=["GET"])
def get_presenter_notes_for_context(context_type: str, context_id: str) -> Response:
    """Get presenter notes for a specific context.
    
    Args:
        context_type: Type of context (phase, scenario, feature).
        context_id: ID of the specific context item.
        
    Query Parameters:
        timing: Optional timing filter (before, during, after).
        
    Returns:
        JSON array of presenter notes for the specified context.
    """
    service = get_presenter_note_service()
    timing = request.args.get("timing")
    
    notes = service.get_notes_for_context(context_type, context_id, timing)
    
    return jsonify([note.to_dict() for note in notes])


@api_bp.route("/presenter-notes/note/<note_id>", methods=["GET"])
def get_presenter_note(note_id: str) -> Response:
    """Get a specific presenter note by ID.
    
    Args:
        note_id: The unique ID of the note.
        
    Returns:
        JSON object with the presenter note or 404 if not found.
    """
    service = get_presenter_note_service()
    note = service.get_note_by_id(note_id)
    
    if note is None:
        return jsonify({"error": "Presenter note not found"}), 404
    
    return jsonify(note.to_dict())
