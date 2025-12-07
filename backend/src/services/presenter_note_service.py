"""
Presenter Note Service - Loads and manages presenter notes for demo talking points.
"""

import json
import os
from typing import Dict, List, Optional
from functools import lru_cache

from models.presenter_note import PresenterNote


class PresenterNoteService:
    """Service for managing presenter notes by context."""

    def __init__(self, notes_directory: str = "data/presenter-notes"):
        """Initialize with notes directory path.
        
        Args:
            notes_directory: Path to the directory containing presenter notes JSON files.
        """
        self._notes_directory = notes_directory
        self._notes_cache: Dict[str, List[PresenterNote]] = {}
        self._load_all_notes()

    def _load_all_notes(self) -> None:
        """Load all presenter notes from JSON files."""
        if not os.path.exists(self._notes_directory):
            return

        for filename in os.listdir(self._notes_directory):
            if filename.endswith(".json"):
                filepath = os.path.join(self._notes_directory, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        notes = data.get("notes", [])
                        for note_data in notes:
                            note = PresenterNote(
                                note_id=note_data.get("note_id", ""),
                                title=note_data.get("title", ""),
                                content=note_data.get("content", ""),
                                context_type=note_data.get("context_type", ""),
                                context_id=note_data.get("context_id", ""),
                                timing=note_data.get("timing"),
                                tips=note_data.get("tips", []),
                                emphasis_level=note_data.get("emphasis_level", 1),
                            )
                            key = f"{note.context_type}:{note.context_id}"
                            if key not in self._notes_cache:
                                self._notes_cache[key] = []
                            self._notes_cache[key].append(note)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Warning: Failed to load notes from {filepath}: {e}")

    def get_notes_for_context(
        self, context_type: str, context_id: str, timing: Optional[str] = None
    ) -> List[PresenterNote]:
        """Get presenter notes for a specific context.
        
        Args:
            context_type: Type of context (phase, scenario, feature).
            context_id: ID of the specific context item.
            timing: Optional timing filter (before, during, after).
            
        Returns:
            List of matching presenter notes.
        """
        key = f"{context_type}:{context_id}"
        notes = self._notes_cache.get(key, [])
        
        if timing:
            notes = [n for n in notes if n.timing == timing]
        
        return sorted(notes, key=lambda n: n.emphasis_level, reverse=True)

    def get_all_notes(self) -> List[PresenterNote]:
        """Get all presenter notes.
        
        Returns:
            List of all presenter notes.
        """
        all_notes = []
        for notes_list in self._notes_cache.values():
            all_notes.extend(notes_list)
        return all_notes

    def get_notes_by_type(self, context_type: str) -> List[PresenterNote]:
        """Get all notes for a specific context type.
        
        Args:
            context_type: Type of context (phase, scenario, feature).
            
        Returns:
            List of matching presenter notes.
        """
        matching_notes = []
        for key, notes in self._notes_cache.items():
            if key.startswith(f"{context_type}:"):
                matching_notes.extend(notes)
        return sorted(matching_notes, key=lambda n: n.emphasis_level, reverse=True)

    def get_note_by_id(self, note_id: str) -> Optional[PresenterNote]:
        """Get a specific presenter note by ID.
        
        Args:
            note_id: The unique ID of the note.
            
        Returns:
            The presenter note if found, None otherwise.
        """
        for notes_list in self._notes_cache.values():
            for note in notes_list:
                if note.note_id == note_id:
                    return note
        return None

    def reload_notes(self) -> None:
        """Reload all notes from disk."""
        self._notes_cache.clear()
        self._load_all_notes()


# Global service instance
_presenter_note_service: Optional[PresenterNoteService] = None


def get_presenter_note_service() -> PresenterNoteService:
    """Get the global presenter note service instance.
    
    Returns:
        The singleton PresenterNoteService instance.
    """
    global _presenter_note_service
    if _presenter_note_service is None:
        _presenter_note_service = PresenterNoteService()
    return _presenter_note_service
