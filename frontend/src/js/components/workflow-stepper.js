/**
 * Workflow Stepper Component
 * 
 * Alpine.js component for displaying and navigating through the 5-phase workflow:
 * 1. Specification
 * 2. Clarification
 * 3. Planning
 * 4. Tasks
 * 5. Implementation
 */

export function workflowStepper() {
    return {
        phases: [
            { name: 'specify', display: 'Specification', icon: '📝', order: 0 },
            { name: 'clarify', display: 'Clarification', icon: '💬', order: 1 },
            { name: 'plan', display: 'Planning', icon: '🗺️', order: 2 },
            { name: 'tasks', display: 'Tasks', icon: '✅', order: 3 },
            { name: 'implement', display: 'Implementation', icon: '⚙️', order: 4 }
        ],
        currentPhase: 'specify',
        currentIndex: 0,
        totalPhases: 5,
        
        /**
         * Initialize the stepper component
         */
        init() {
            console.log('Workflow stepper initialized');
        },
        
        /**
         * Update the current phase
         * @param {string} phaseName - The phase name to set as current
         * @param {number} index - The phase index (0-4)
         */
        updatePhase(phaseName, index) {
            this.currentPhase = phaseName;
            this.currentIndex = index;
        },
        
        /**
         * Check if a phase is completed
         * @param {number} index - The phase index
         * @returns {boolean} True if the phase is completed
         */
        isCompleted(index) {
            return index < this.currentIndex;
        },
        
        /**
         * Check if a phase is the current active phase
         * @param {number} index - The phase index
         * @returns {boolean} True if this is the current phase
         */
        isCurrent(index) {
            return index === this.currentIndex;
        },
        
        /**
         * Check if a phase is not yet started
         * @param {number} index - The phase index
         * @returns {boolean} True if the phase hasn't been reached yet
         */
        isUpcoming(index) {
            return index > this.currentIndex;
        },
        
        /**
         * Get progress percentage
         * @returns {number} Progress as percentage (0-100)
         */
        getProgress() {
            return Math.round((this.currentIndex / (this.totalPhases - 1)) * 100);
        },
        
        /**
         * Get CSS classes for a phase step
         * @param {number} index - The phase index
         * @returns {string} CSS class names
         */
        getPhaseClasses(index) {
            if (this.isCompleted(index)) return 'phase-completed';
            if (this.isCurrent(index)) return 'phase-current';
            return 'phase-upcoming';
        }
    };
}

// Export for use in main.js
window.workflowStepper = workflowStepper;
