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
          this.showCustomScenarioForm = scenario.id === 'custom';
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
        const loaded = response.scenarios || [];

        // Add a synthetic "Custom" scenario tile that activates the custom-scenario creation flow.
        // This is a UI-only item (no backend scenario exists with id "custom").
        const customTile = {
          id: 'custom',
          title: 'Custom',
          description: 'Create your own scenario by entering a feature title, description, and domain.',
          domain: 'custom',
          is_custom: false
        };

        this.scenarios = [customTile, ...loaded.filter(s => s?.id !== 'custom')];
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
      // "Custom" is a UI-only tile that scrolls/focuses the custom scenario form.
      if (scenario?.id === 'custom') {
        this.selectedScenario = scenario;
        this.showCustomScenarioForm = true;
        stateManager.updateSession({
          selectedScenarioId: scenario.id,
          selectedAt: new Date().toISOString()
        });
        this.workflowState = null;
        this.currentArtifact = null;
        this.resetPhaseInputs();

        this.showStatus('Create a custom scenario below');

        // Scroll to the custom scenario section and focus the first field.
        requestAnimationFrame(() => {
          const section = document.getElementById('custom-scenario-section');
          section?.scrollIntoView({ behavior: 'smooth', block: 'start' });

          const firstInput = section?.querySelector('input, textarea, select, button');
          firstInput?.focus?.();
        });
        return;
      }

      this.showCustomScenarioForm = false;
      this.selectedScenario = scenario;
      stateManager.updateSession({ 
        selectedScenarioId: scenario.id,
        selectedAt: new Date().toISOString()
      });
      this.showStatus(`Selected scenario: ${scenario.title}`);
      console.log('Selected scenario:', scenario);
      
      // Initialize workflow for this scenario
      await this.initializeWorkflow(scenario.id);

      // For custom scenarios, prefill the first phase input so it "appears" immediately
      // (without requiring the user to manually copy the scenario prompt).
      if (this.isCustomScenario() && this.workflowState?.current_phase?.phase_name === 'specify') {
        const seed = (scenario.initial_prompt || scenario.feature_description || '').trim();
        if (seed && !this.phaseInputs?.specify && !this.currentPhaseInput?.trim()) {
          this.currentPhaseInput = seed;
        }
      }
    },

    /**
     * Initialize workflow for the selected scenario.
     * For demo scenarios, auto-generates the first phase artifact.
     * For custom scenarios, waits for user input.
     * @param {string} scenarioId - The scenario ID
     */
    async initializeWorkflow(scenarioId) {
      this.isLoading = true;
      try {
        const response = await apiClient.getWorkflow(scenarioId);
        this.workflowState = response;
        
        console.log('Workflow initialized:', response);
        
        // For demo scenarios, auto-generate the first phase artifact
        if (!this.isCustomScenario()) {
          await this.generateArtifact(response.current_phase.phase_name);
        }
      } catch (error) {
        this.showError('Failed to initialize workflow: ' + error.message);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Advance to the next workflow phase.
     * For demo scenarios: auto-generates the artifact for the new phase.
     * For custom scenarios: shows the input form for user to provide context.
     */
    async nextPhase() {
      if (!this.selectedScenario) return;

      const previousPhaseName = this.workflowState?.current_phase?.phase_name;
      
      this.isLoading = true;
      try {
        const response = await apiClient.advanceWorkflow(this.selectedScenario.id);
        this.workflowState = response;
        
        if (this.isCustomScenario()) {
          // Persist the previous phase output so it can be shown as context later.
          if (previousPhaseName && response.previous_phase_artifact) {
            this.phaseInputs[previousPhaseName] = {
              ...(this.phaseInputs[previousPhaseName] || {}),
              ...(response.previous_phase_input || {}),
              artifact: response.previous_phase_artifact,
              artifact_markdown: response.previous_phase_artifact?.content_markdown || '',
              submittedAt: (this.phaseInputs[previousPhaseName]?.submittedAt || new Date().toISOString())
            };
          }

          const currentPhaseName = response.current_phase?.phase_name;
          const submittedForCurrent = currentPhaseName ? this.phaseInputs[currentPhaseName] : null;

          // For the final step, show the wrap-up artifact automatically (it includes "What's Next?").
          if (currentPhaseName === 'implement') {
            await this.generateArtifact('implement');
            this.showStatus(`Advanced to: ${response.current_phase.display_name}`);
          } else if (submittedForCurrent?.artifact) {
            // If we've already generated an artifact for this phase, show it.
            this.currentArtifact = submittedForCurrent.artifact;
            this.showStatus(`Advanced to: ${response.current_phase.display_name}`);
          } else {
            // Otherwise prompt for input for this phase.
            this.currentArtifact = null;
            this.showStatus(`Advanced to: ${response.current_phase.display_name} - Enter your input to continue`);
          }
        } else {
          // Demo scenario: auto-generate artifact for this phase
          await this.generateArtifact(response.current_phase.phase_name);
          this.showStatus(`Advanced to: ${response.current_phase.display_name}`);
        }
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
        
        if (this.isCustomScenario()) {
          // Custom scenario: check if we have submitted input for this phase
          const submittedInput = this.phaseInputs[phaseName];
          if (submittedInput?.artifact) {
            this.currentArtifact = submittedInput.artifact;
          } else {
            // Clear artifact to prompt for input
            this.currentArtifact = null;
          }
          this.showStatus(`Jumped to: ${response.current_phase.display_name} - Enter your input to continue`);
        } else {
          // Demo scenario: auto-generate artifact for this phase
          await this.generateArtifact(response.current_phase.phase_name);
          this.showStatus(`Jumped to: ${response.current_phase.display_name}`);
        }
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

          // Persist the artifact so later phases can show previous outputs.
          this.phaseInputs[currentPhaseName].artifact = response.artifact;
          this.phaseInputs[currentPhaseName].artifact_markdown = response.artifact?.content_markdown || '';
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
     * Check if the current scenario is a custom scenario.
     * Custom scenarios require user input at each phase.
     * Demo scenarios show pre-built artifacts.
     * @returns {boolean} True if custom scenario
     */
    isCustomScenario() {
      return this.selectedScenario?.is_custom === true;
    },

    _truncateForContextPanel(text, maxChars = 1200) {
      const t = (text || '').toString().trim();
      if (!t) return '';
      if (t.length <= maxChars) return t;
      return t.slice(0, maxChars).trimEnd() + '\n\n…';
    },

    _formatClarificationsForContextPanel(clarifications) {
      if (!Array.isArray(clarifications) || clarifications.length === 0) return '';
      const answered = clarifications.filter(q => (q?.answer || '').toString().trim());
      if (answered.length === 0) return '';
      return answered
        .map((item, idx) => `Q${idx + 1}: ${item.question || ''}\nA${idx + 1}: ${item.answer || ''}`)
        .join('\n\n');
    },

    hasCustomPreviousContext() {
      if (!this.isCustomScenario()) return false;
      const current = this.workflowState?.current_phase?.phase_name;
      const order = ['specify', 'clarify', 'plan', 'tasks', 'implement'];
      const currentIndex = order.indexOf(current);
      if (currentIndex <= 0) return false;
      return order.slice(0, currentIndex).some(p => {
        const d = this.phaseInputs?.[p];
        return !!(d && ((d.artifact_markdown || d.artifact?.content_markdown) || d.input || (d.clarifications && d.clarifications.length)));
      });
    },

    getCustomPreviousContextText() {
      const current = this.workflowState?.current_phase?.phase_name;
      const order = ['specify', 'clarify', 'plan', 'tasks', 'implement'];
      const display = {
        specify: 'Specification',
        clarify: 'Clarification',
        plan: 'Planning',
        tasks: 'Tasks',
        implement: 'Implementation'
      };

      const currentIndex = order.indexOf(current);
      if (currentIndex <= 0) return 'No previous steps yet.';

      const blocks = [];
      for (const phase of order.slice(0, currentIndex)) {
        const data = this.phaseInputs?.[phase];
        if (!data) continue;

        const parts = [];
        const clar = this._formatClarificationsForContextPanel(data.clarifications);
        const input = (data.input || '').toString().trim();
        if (clar) parts.push(`Input:\n${this._truncateForContextPanel(clar, 800)}`);
        else if (input) parts.push(`Input:\n${this._truncateForContextPanel(input, 800)}`);

        const output = (data.artifact_markdown || data.artifact?.content_markdown || '').toString().trim();
        if (output) parts.push(`Output:\n${this._truncateForContextPanel(output, 1200)}`);

        if (parts.length) {
          blocks.push(`Step ${order.indexOf(phase) + 1}: ${display[phase] || phase}\n${parts.join('\n\n')}`);
        }
      }

      return blocks.length ? blocks.join('\n\n---\n\n') : 'No previous steps yet.';
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
     * Calls the backend to generate an artifact with context from all previous phases.
     * @param {string} phaseName - The phase name
     */
    async generateArtifact(phaseName) {
      // Check if we have submitted input for this phase
      const submittedInput = this.phaseInputs[phaseName];
      
      if (submittedInput && submittedInput.artifact) {
        // Use the artifact from the submitted input
        this.currentArtifact = submittedInput.artifact;
        return;
      }

      // Call backend to generate artifact with context from previous phases
      this.isGeneratingArtifact = true;
      try {
        const response = await apiClient.generateArtifactWithContext(
          this.selectedScenario.id,
          phaseName
        );
        
        if (response.artifact) {
          this.currentArtifact = response.artifact;
          console.log(`Generated artifact for ${phaseName} with context from:`, response.context_from_phases);
        }
      } catch (error) {
        console.error('Failed to generate artifact:', error);
        // Fallback to a simple prompt message
        this.currentArtifact = {
          artifact_type: phaseName === 'specify' ? 'spec' : phaseName,
          phase_name: phaseName,
          content_markdown: `# ${this.getPhaseInputTitle()}\n\nEnter your input above and click "Generate Artifact" to create a customized ${phaseName} document.`,
          content_html: `<h1>${this.getPhaseInputTitle()}</h1><p>Enter your input above and click "Generate Artifact" to create a customized ${phaseName} document.</p>`,
          generation_duration_ms: 0,
          tokens_used: 0
        };
      } finally {
        this.isGeneratingArtifact = false;
      }
      
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
     * Demo scenarios: show phase-specific simulated user input.
     * Step 1: initial prompt; Step 2: clarifying Q/A (if provided by scenario).
     */
    getDemoSimulatedInputDescription() {
      const phase = this.workflowState?.current_phase?.phase_name;
      if (phase === 'clarify') {
        return 'This demo scenario includes a simulated clarification round (example questions and answers):';
      }
      return 'This demo scenario uses the following predefined specification as the simulated user input:';
    },

    getDemoSimulatedInputTitle() {
      const phase = this.workflowState?.current_phase?.phase_name;
      if (phase === 'clarify') {
        return 'Clarifying Questions & Answers (Simulated Input)';
      }
      return 'Initial Specification (Simulated Input)';
    },

    getDemoSimulatedInputIcon() {
      const phase = this.workflowState?.current_phase?.phase_name;
      return phase === 'clarify' ? '💬' : '📝';
    },

    getDemoSimulatedInputText() {
      const phase = this.workflowState?.current_phase?.phase_name;
      if (phase === 'clarify') {
        const qa = this.selectedScenario?.demo_clarifications || [];
        if (!qa.length) return 'No clarifying Q/A defined for this scenario.';
        return qa
          .map((item, idx) => `Q${idx + 1}: ${item.question}\nA${idx + 1}: ${item.answer}`)
          .join('\n\n');
      }
      return this.selectedScenario?.initial_prompt || 'No initial prompt defined';
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
        this.showCustomScenarioForm = false;
        this.workflowState = null;
        this.currentArtifact = null;
        this.resetPhaseInputs();
        this.resetCustomScenarioForm();
        stateManager.clearSession();

        // Refresh scenario list to reflect cleared custom scenarios.
        await this.loadScenarios();

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

        // Reset the form (inline section stays visible)
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
