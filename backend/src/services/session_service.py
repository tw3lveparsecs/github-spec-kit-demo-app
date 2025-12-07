"""
SessionService for managing demo session state.
"""

import logging
from typing import Optional
from datetime import datetime

from models.session import DemoSession

logger = logging.getLogger(__name__)

# In-memory session storage (single presenter assumption)
_current_session: Optional[DemoSession] = None


class SessionService:
    """Service for managing demo session state."""

    def create_session(self) -> DemoSession:
        """
        Create a new demo session.

        Returns:
            New DemoSession object.
        """
        global _current_session

        session = DemoSession()
        _current_session = session

        logger.info(f"Created new session: {session.session_id}")
        return session

    def get_current_session(self) -> DemoSession:
        """
        Get the current demo session, creating one if it doesn't exist.

        Returns:
            Current DemoSession object.
        """
        global _current_session

        if _current_session is None:
            _current_session = self.create_session()

        return _current_session

    def reset_session(self) -> DemoSession:
        """
        Reset the demo session to initial state.

        Returns:
            New DemoSession object.
        """
        global _current_session

        old_session_id = _current_session.session_id if _current_session else "none"
        _current_session = DemoSession()

        logger.info(f"Reset session from {old_session_id} to {_current_session.session_id}")
        return _current_session

    def update_session(self, scenario_id: Optional[str] = None, phase_name: Optional[str] = None) -> DemoSession:
        """
        Update the current session with new state.

        Args:
            scenario_id: ID of the selected scenario (optional).
            phase_name: Name of the current phase (optional).

        Returns:
            Updated DemoSession object.
        """
        session = self.get_current_session()

        if scenario_id is not None:
            session.current_scenario_id = scenario_id
            session.log_action("scenario_select", f"Selected scenario: {scenario_id}")

        if phase_name is not None:
            session.current_phase_name = phase_name
            session.log_action("phase_advance", f"Moved to phase: {phase_name}")

        logger.info(f"Updated session: scenario={scenario_id}, phase={phase_name}")
        return session
