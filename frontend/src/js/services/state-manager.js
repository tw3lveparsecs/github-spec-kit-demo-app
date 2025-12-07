/**
 * State Manager for handling localStorage and session state.
 */

const STORAGE_KEY = 'speckit_demo_session';

/**
 * State Manager object for persisting demo state.
 */
const stateManager = {
  /**
   * Save session state to localStorage.
   * @param {object} state - Session state to save
   */
  saveSession(state) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (error) {
      console.error('Failed to save session to localStorage:', error);
    }
  },

  /**
   * Load session state from localStorage.
   * @returns {object|null} Saved session state or null
   */
  loadSession() {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Failed to load session from localStorage:', error);
      return null;
    }
  },

  /**
   * Clear session state from localStorage.
   */
  clearSession() {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('Failed to clear session from localStorage:', error);
    }
  },

  /**
   * Update specific fields in the session state.
   * @param {object} updates - Fields to update
   */
  updateSession(updates) {
    const currentState = this.loadSession() || {};
    const newState = { ...currentState, ...updates };
    this.saveSession(newState);
  }
};

// Export for use in other modules
if (typeof window !== 'undefined') {
  window.stateManager = stateManager;
}
