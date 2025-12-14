/**
 * API Client for communicating with the Flask backend.
 */

const API_BASE_URL = '/api';

/**
 * Generic API request handler with error handling.
 * @param {string} endpoint - API endpoint (e.g., '/scenarios')
 * @param {object} options - Fetch options (method, body, etc.)
 * @returns {Promise<any>} Response data
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Request failed:', error);
    throw error;
  }
}

/**
 * API Client object with methods for each endpoint.
 */
const apiClient = {
  /**
   * Health check endpoint.
   * @returns {Promise<object>} Health status
   */
  async healthCheck() {
    return apiRequest('/health');
  },

  /**
   * Get all demo scenarios.
   * @returns {Promise<object>} List of scenarios
   */
  async getScenarios() {
    return apiRequest('/scenarios');
  },

  /**
   * Get a specific scenario by ID.
   * @param {string} scenarioId - Scenario identifier
   * @returns {Promise<object>} Scenario details
   */
  async getScenario(scenarioId) {
    return apiRequest(`/scenarios/${scenarioId}`);
  },

  /**
   * Reset the demo to initial state.
   * @returns {Promise<object>} Reset confirmation
   */
  async resetDemo() {
    return apiRequest('/workflow/reset', { method: 'POST' });
  },

  /**
   * Get workflow state for a scenario.
   * @param {string} scenarioId - Scenario identifier
   * @returns {Promise<object>} Workflow state with current phase and progress
   */
  async getWorkflow(scenarioId) {
    return apiRequest(`/workflow/${scenarioId}`);
  },

  /**
   * Advance to the next workflow phase.
   * @param {string} scenarioId - Scenario identifier
   * @returns {Promise<object>} Updated workflow state
   */
  async advanceWorkflow(scenarioId) {
    return apiRequest(`/workflow/${scenarioId}/step`, { method: 'POST' });
  },

  /**
   * Jump to a specific workflow phase.
   * @param {string} scenarioId - Scenario identifier
   * @param {string} phaseName - Phase name (specify, clarify, plan, tasks, implement)
   * @returns {Promise<object>} Updated workflow state
   */
  async jumpToPhase(scenarioId, phaseName) {
    return apiRequest(`/workflow/${scenarioId}/jump`, {
      method: 'POST',
      body: JSON.stringify({ phase: phaseName })
    });
  },

  /**
   * Submit user input for a workflow phase.
   * @param {string} scenarioId - Scenario identifier
   * @param {string} phaseName - Phase name
   * @param {string} userInput - User's input text
   * @param {Array} clarifications - Optional array of {question, answer} pairs
   * @returns {Promise<object>} Generated artifact and workflow state
   */
  async submitPhaseInput(scenarioId, phaseName, userInput, clarifications = []) {
    return apiRequest(`/workflow/${scenarioId}/input`, {
      method: 'POST',
      body: JSON.stringify({
        phase: phaseName,
        input: userInput,
        clarifications: clarifications
      })
    });
  },

  /**
   * Get all phase inputs for a scenario.
   * @param {string} scenarioId - Scenario identifier
   * @returns {Promise<object>} All phase inputs
   */
  async getPhaseInputs(scenarioId) {
    return apiRequest(`/workflow/${scenarioId}/inputs`);
  }
};

// Export for use in other modules
if (typeof window !== 'undefined') {
  window.apiClient = apiClient;
}
