/**
 * Constitution Panel Component
 * 
 * Alpine.js component for displaying constitution principles and check results.
 * Shows the 4 core principles and their evaluation status during the workflow.
 */

function constitutionPanel() {
    return {
        principles: [],
        checks: [],
        expandedPrinciples: {},
        isLoading: false,
        lastCheckTime: null,
        
        /**
         * Initialize the constitution panel
         */
        async init() {
            console.log('Constitution panel initialized');
        },
        
        /**
         * Load constitution principles from the API
         */
        async loadPrinciples() {
            this.isLoading = true;
            try {
                const response = await fetch('/api/constitution');
                if (response.ok) {
                    const data = await response.json();
                    this.principles = data.principles || [];
                    console.log('Loaded principles:', this.principles);
                }
            } catch (error) {
                console.error('Failed to load constitution principles:', error);
            } finally {
                this.isLoading = false;
            }
        },
        
        /**
         * Run constitution checks for an artifact
         * @param {string} artifactId - The artifact ID to check
         */
        async runConstitutionCheck(artifactId) {
            if (!artifactId) {
                console.warn('No artifact ID provided for constitution check');
                return;
            }
            
            this.isLoading = true;
            try {
                const response = await fetch(`/api/constitution/check/${artifactId}`);
                if (response.ok) {
                    const data = await response.json();
                    this.checks = data.checks || [];
                    this.lastCheckTime = new Date().toLocaleTimeString();
                    console.log('Constitution check results:', this.checks);
                }
            } catch (error) {
                console.error('Failed to run constitution checks:', error);
            } finally {
                this.isLoading = false;
            }
        },
        
        /**
         * Toggle principle expansion
         * @param {string} principleId - The principle ID to toggle
         */
        togglePrinciple(principleId) {
            this.expandedPrinciples[principleId] = !this.expandedPrinciples[principleId];
        },
        
        /**
         * Get check result for a specific principle
         * @param {string} principleId - The principle ID
         * @returns {Object|null} The check result or null
         */
        getCheckForPrinciple(principleId) {
            return this.checks.find(c => c.principle_id === principleId) || null;
        },
        
        /**
         * Get summary of all checks
         * @returns {Object} Summary with passed, failed, warning counts
         */
        getCheckSummary() {
            const summary = {
                passed: 0,
                failed: 0,
                warning: 0,
                pending: 0
            };
            
            for (const check of this.checks) {
                if (check.status === 'passed') summary.passed++;
                else if (check.status === 'failed') summary.failed++;
                else if (check.status === 'warning') summary.warning++;
                else summary.pending++;
            }
            
            return summary;
        },
        
        /**
         * Get icon for principle category
         * @param {string} category - The category
         * @returns {string} Icon emoji
         */
        getPrincipleIcon(category) {
            const icons = {
                'performance': '⚡',
                'security': '🔒',
                'maintainability': '🔧',
                'user_experience': '👤',
                'technical': '⚙️'
            };
            return icons[category] || '📋';
        },
        
        /**
         * Get check status class for styling
         * @param {string} status - The check status
         * @returns {string} CSS class
         */
        getCheckStatusClass(status) {
            const classes = {
                'passed': 'check-badge--passed',
                'failed': 'check-badge--failed',
                'warning': 'check-badge--warning',
                'pending': 'check-badge--pending'
            };
            return classes[status] || 'check-badge--pending';
        }
    };
}

// Export for use in Alpine.js
window.constitutionPanel = constitutionPanel;
