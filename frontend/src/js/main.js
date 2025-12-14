/**
 * Main application logic using Alpine.js.
 */

// Register Service Worker for offline capability
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(registration => {
        console.log('ServiceWorker registered:', registration.scope);
      })
      .catch(error => {
        console.warn('ServiceWorker registration failed:', error);
      });
  });
}

function demoApp() {
  return {
    scenarios: [],
    selectedScenario: null,
    workflowState: null,
    currentArtifact: null,
    artifactExpanded: true,
    isGeneratingArtifact: false,
    isLoading: false,
    statusMessage: '',
    errorMessage: '',
    
    // Custom scenario form state
    showCustomScenarioForm: false,
    isCreatingScenario: false,
    customScenarioError: '',
    customScenarioErrors: {},
    customScenarioData: {
      title: '',
      description: '',
      domain: '',
      feature_description: '',
      tech_stack: []
    },
    techStackInput: '',

    // Phase input state
    phaseInputs: {},
    currentPhaseInput: '',
    clarifyQuestions: [
      { question: 'What are the primary user personas for this feature?', answer: '' },
      { question: 'Are there any specific technical constraints or requirements?', answer: '' },
      { question: 'What is the expected timeline for delivery?', answer: '' },
      { question: 'Are there any integration requirements with existing systems?', answer: '' }
    ],
    isSubmittingInput: false,

    /**
     * Initialize the application.
     */
    async init() {
      console.log('Initializing GitHub Spec Kit Demo Application');
      
      // Check backend health
      try {
        const health = await apiClient.healthCheck();
        console.log('Backend health check:', health);
      } catch (error) {
        this.showError('Failed to connect to backend. Please ensure the server is running.');
        return;
      }

      // Load scenarios
      await this.loadScenarios();

      // Restore session state if available
      const savedSession = stateManager.loadSession();
      if (savedSession && savedSession.selectedScenarioId) {
        const scenario = this.scenarios.find(s => s.id === savedSession.selectedScenarioId);
        if (scenario) {
          this.selectedScenario = scenario;
        }
      }
    },

    /**
     * Load all demo scenarios from the backend.
     */
    async loadScenarios() {
      this.isLoading = true;
      this.errorMessage = '';

      try {
        const response = await apiClient.getScenarios();
        this.scenarios = response.scenarios || [];
        console.log(`Loaded ${this.scenarios.length} scenarios`);
      } catch (error) {
        this.showError('Failed to load scenarios: ' + error.message);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Select a demo scenario.
     * @param {object} scenario - The scenario to select
     */
    async selectScenario(scenario) {
      this.selectedScenario = scenario;
      stateManager.updateSession({ 
        selectedScenarioId: scenario.id,
        selectedAt: new Date().toISOString()
      });
      this.showStatus(`Selected scenario: ${scenario.title}`);
      console.log('Selected scenario:', scenario);
      
      // Initialize workflow for this scenario
      await this.initializeWorkflow(scenario.id);
    },

    /**
     * Initialize workflow for the selected scenario.
     * @param {string} scenarioId - The scenario ID
     */
    async initializeWorkflow(scenarioId) {
      this.isLoading = true;
      try {
        const response = await apiClient.getWorkflow(scenarioId);
        this.workflowState = response;
        
        console.log('Workflow initialized:', response);
      } catch (error) {
        this.showError('Failed to initialize workflow: ' + error.message);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Advance to the next workflow phase.
     */
    async nextPhase() {
      if (!this.selectedScenario) return;
      
      this.isLoading = true;
      try {
        const response = await apiClient.advanceWorkflow(this.selectedScenario.id);
        this.workflowState = response;
        
        // Generate artifact for this phase
        await this.generateArtifact(response.current_phase.phase_name);
        
        this.showStatus(`Advanced to: ${response.current_phase.display_name}`);
      } catch (error) {
        this.showError('Failed to advance phase: ' + error.message);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Go back to the previous workflow phase.
     */
    async previousPhase() {
      if (!this.workflowState || this.workflowState.phase_index === 0) return;
      
      const targetPhase = this.workflowState.scenario.workflow_phases[this.workflowState.phase_index - 1];
      await this.jumpToPhase(targetPhase.phase_name);
    },

    /**
     * Jump to a specific workflow phase.
     * @param {string} phaseName - The phase name to jump to
     */
    async jumpToPhase(phaseName) {
      if (!this.selectedScenario || !phaseName) return;
      
      this.isLoading = true;
      try {
        const response = await apiClient.jumpToPhase(this.selectedScenario.id, phaseName);
        this.workflowState = response;
        
        // Generate artifact for this phase
        await this.generateArtifact(response.current_phase.phase_name);
        
        this.showStatus(`Jumped to: ${response.current_phase.display_name}`);
      } catch (error) {
        this.showError('Failed to jump to phase: ' + error.message);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Submit user input for the current phase.
     * This sends the user's input to the backend and generates a context-aware artifact.
     */
    async submitPhaseInput() {
      if (!this.selectedScenario || !this.workflowState) return;
      
      const currentPhaseName = this.workflowState.current_phase?.phase_name;
      if (!currentPhaseName) return;

      this.isSubmittingInput = true;
      this.isGeneratingArtifact = true;

      try {
        // Prepare clarifications if in clarify phase
        const clarifications = currentPhaseName === 'clarify' 
          ? this.clarifyQuestions.filter(q => q.answer.trim())
          : [];

        // Submit input to backend
        const response = await apiClient.submitPhaseInput(
          this.selectedScenario.id,
          currentPhaseName,
          this.currentPhaseInput,
          clarifications
        );

        // Store the input
        this.phaseInputs[currentPhaseName] = {
          input: this.currentPhaseInput,
          clarifications: clarifications,
          submittedAt: new Date().toISOString()
        };

        // Update artifact from response
        if (response.artifact) {
          this.currentArtifact = response.artifact;
        }

        this.showStatus(`Input submitted for ${currentPhaseName} phase`);
        console.log('Phase input submitted:', response);

        // Clear current input after submission
        this.currentPhaseInput = '';

      } catch (error) {
        this.showError('Failed to submit input: ' + error.message);
      } finally {
        this.isSubmittingInput = false;
        this.isGeneratingArtifact = false;
      }
    },

    /**
     * Get placeholder text for the current phase input.
     * @returns {string} Placeholder text
     */
    getPhaseInputPlaceholder() {
      const placeholders = {
        'specify': 'Describe the feature you want to build. Include user stories, requirements, and any specific functionality...',
        'clarify': 'Add any additional context or clarifications here...',
        'plan': 'Provide any technical preferences, constraints, or architectural considerations...',
        'tasks': 'Add any specific tasks or requirements you want included in the task breakdown...',
        'implement': 'Add any implementation notes, code preferences, or specific instructions...'
      };
      return placeholders[this.workflowState?.current_phase?.phase_name] || 'Enter your input...';
    },

    /**
     * Get the title for the current phase input section.
     * @returns {string} Section title
     */
    getPhaseInputTitle() {
      const titles = {
        'specify': 'Define Your Feature',
        'clarify': 'Clarify Requirements',
        'plan': 'Refine the Plan',
        'tasks': 'Customize Tasks',
        'implement': 'Implementation Notes'
      };
      return titles[this.workflowState?.current_phase?.phase_name] || 'Your Input';
    },

    /**
     * Get the icon for the current phase.
     * @returns {string} Icon emoji
     */
    getPhaseInputIcon() {
      const icons = {
        'specify': '📝',
        'clarify': '💬',
        'plan': '🗺️',
        'tasks': '✅',
        'implement': '⚙️'
      };
      return icons[this.workflowState?.current_phase?.phase_name] || '📄';
    },

    /**
     * Check if current phase has been submitted.
     * @returns {boolean} True if input has been submitted for current phase
     */
    hasSubmittedInput() {
      const currentPhase = this.workflowState?.current_phase?.phase_name;
      return currentPhase && !!this.phaseInputs[currentPhase];
    },

    /**
     * Get submitted input for current phase.
     * @returns {object|null} Submitted input data
     */
    getSubmittedInput() {
      const currentPhase = this.workflowState?.current_phase?.phase_name;
      return currentPhase ? this.phaseInputs[currentPhase] : null;
    },

    /**
     * Reset phase inputs when demo is reset.
     */
    resetPhaseInputs() {
      this.phaseInputs = {};
      this.currentPhaseInput = '';
      this.clarifyQuestions = this.clarifyQuestions.map(q => ({ ...q, answer: '' }));
    },

    /**
     * Generate artifact for the current phase.
     * @param {string} phaseName - The phase name
     */
    async generateArtifact(phaseName) {
      // Check if we have submitted input for this phase
      const submittedInput = this.phaseInputs[phaseName];
      
      if (submittedInput) {
        // Use the artifact from the submitted input
        // It was already generated when input was submitted
        return;
      }

      // For demo purposes, create a mock artifact if no input was submitted
      // In a real implementation, this would call the backend
      const artifactTypes = {
        'specify': 'spec',
        'clarify': 'clarify',
        'plan': 'plan',
        'tasks': 'tasks',
        'implement': 'implement'
      };
      
      const artifactContent = {
        'spec': '# Feature Specification\n\n## Overview\nThis is a detailed specification...\n\n*Submit your input above to generate a customized specification.*',
        'clarify': '# Clarification Summary\n\n## Questions\nAnswer the questions above to refine the specification...\n\n*Submit your answers to generate clarification notes.*',
        'plan': '# Implementation Plan\n\n## Architecture\nHigh-level architecture...\n\n*Submit your technical preferences to customize the plan.*',
        'tasks': '# Task Breakdown\n\n## Phase 1: Setup\n- [ ] Task 1\n- [ ] Task 2\n\n*Submit additional requirements to customize the task list.*',
        'implement': '# Implementation\n\n```python\ndef example():\n    pass\n```\n\n*Submit implementation notes to finalize.*'
      };
      
      this.currentArtifact = {
        artifact_type: artifactTypes[phaseName] || 'spec',
        phase_name: phaseName,
        content_markdown: artifactContent[artifactTypes[phaseName]] || '',
        content_html: `<div>${artifactContent[artifactTypes[phaseName]] || ''}</div>`,
        generation_duration_ms: 250,
        tokens_used: 150
      };
      
      // Update artifact viewer
      const viewer = this.$refs.artifactViewer;
      if (viewer) {
        viewer.setArtifact(this.currentArtifact);
      }
    },

    /**
     * Get artifact icon based on type.
     * @returns {string} Icon emoji
     */
    getArtifactIcon() {
      const icons = {
        spec: '📄',
        plan: '📋',
        tasks: '☑️',
        implement: '💻'
      };
      return icons[this.currentArtifact?.artifact_type] || '📄';
    },

    /**
     * Get artifact title based on type.
     * @returns {string} Display title
     */
    getArtifactTitle() {
      const titles = {
        spec: 'Specification',
        plan: 'Implementation Plan',
        tasks: 'Task Breakdown',
        implement: 'Code Implementation'
      };
      return titles[this.currentArtifact?.artifact_type] || 'Artifact';
    },

    /**
     * Reset the demo to initial state.
     */
    async resetDemo() {
      if (!confirm('Are you sure you want to reset the demo? This will clear all progress.')) {
        return;
      }

      this.isLoading = true;
      this.errorMessage = '';

      try {
        await apiClient.resetDemo();
        this.selectedScenario = null;
        this.workflowState = null;
        this.currentArtifact = null;
        this.resetPhaseInputs();
        stateManager.clearSession();
        this.showStatus('Demo reset successfully');
        console.log('Demo reset');
      } catch (error) {
        this.showError('Failed to reset demo: ' + error.message);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Show a status message.
     * @param {string} message - Message to display
     */
    showStatus(message) {
      this.statusMessage = message;
      this.errorMessage = '';
      setTimeout(() => {
        this.statusMessage = '';
      }, 5000);
    },

    /**
     * Show an error message.
     * @param {string} message - Error message to display
     */
    showError(message) {
      this.errorMessage = message;
      this.statusMessage = '';
      setTimeout(() => {
        this.errorMessage = '';
      }, 5000);
    },

    /**
     * Reset the custom scenario form to initial state.
     */
    resetCustomScenarioForm() {
      this.customScenarioData = {
        title: '',
        description: '',
        domain: '',
        feature_description: '',
        tech_stack: []
      };
      this.techStackInput = '';
      this.customScenarioError = '';
      this.customScenarioErrors = {};
    },

    /**
     * Add a technology to the tech stack.
     */
    addTechStack() {
      const tech = this.techStackInput.trim();
      if (tech && !this.customScenarioData.tech_stack.includes(tech)) {
        if (this.customScenarioData.tech_stack.length < 10) {
          this.customScenarioData.tech_stack.push(tech);
        }
      }
      this.techStackInput = '';
    },

    /**
     * Remove a technology from the tech stack.
     * @param {number} index - Index of the technology to remove
     */
    removeTechStack(index) {
      this.customScenarioData.tech_stack.splice(index, 1);
    },

    /**
     * Validate custom scenario form data.
     * @returns {boolean} True if valid
     */
    validateCustomScenarioForm() {
      this.customScenarioErrors = {};
      let valid = true;

      // Title validation
      if (!this.customScenarioData.title.trim()) {
        this.customScenarioErrors.title = 'Title is required';
        valid = false;
      } else if (this.customScenarioData.title.length < 5) {
        this.customScenarioErrors.title = 'Title must be at least 5 characters';
        valid = false;
      }

      // Description validation
      if (!this.customScenarioData.description.trim()) {
        this.customScenarioErrors.description = 'Description is required';
        valid = false;
      } else if (this.customScenarioData.description.length < 20) {
        this.customScenarioErrors.description = 'Description must be at least 20 characters';
        valid = false;
      }

      // Domain validation
      if (!this.customScenarioData.domain.trim()) {
        this.customScenarioErrors.domain = 'Domain/Industry is required';
        valid = false;
      } else if (this.customScenarioData.domain.length < 3) {
        this.customScenarioErrors.domain = 'Domain must be at least 3 characters';
        valid = false;
      }

      return valid;
    },

    /**
     * Create a custom scenario from form data.
     */
    async createCustomScenario() {
      // Clear previous errors
      this.customScenarioError = '';
      
      // Validate form
      if (!this.validateCustomScenarioForm()) {
        this.customScenarioError = 'Please fix the errors above';
        return;
      }

      this.isCreatingScenario = true;

      try {
        const response = await fetch('/api/scenarios/custom', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.customScenarioData)
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || data.errors?.join(', ') || 'Failed to create scenario');
        }

        // Add the new scenario to the list
        this.scenarios.push(data.scenario);
        
        // Select the new scenario
        await this.selectScenario(data.scenario);

        // Close the form and reset
        this.showCustomScenarioForm = false;
        this.resetCustomScenarioForm();

        this.showStatus(`Created custom scenario: ${data.scenario.title}`);
        console.log('Created custom scenario:', data.scenario);

      } catch (error) {
        console.error('Error creating custom scenario:', error);
        this.customScenarioError = error.message;
      } finally {
        this.isCreatingScenario = false;
      }
    }
  };
}

// Initialize when DOM is ready
document.addEventListener('alpine:init', () => {
  console.log('Alpine.js initialized');
});
