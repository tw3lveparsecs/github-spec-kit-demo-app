/**
 * Artifact Viewer Component
 * 
 * Alpine.js component for displaying generated artifacts (spec, plan, tasks)
 * with syntax highlighting and expand/collapse functionality.
 */

export function artifactViewer() {
    return {
        artifact: null,
        isExpanded: true,
        isLoading: false,
        artifactTypes: {
            spec: { display: 'Specification', icon: '📄', color: 'blue' },
            plan: { display: 'Implementation Plan', icon: '📋', color: 'green' },
            tasks: { display: 'Task Breakdown', icon: '☑️', color: 'purple' },
            implement: { display: 'Code Implementation', icon: '💻', color: 'orange' }
        },
        
        /**
         * Initialize the artifact viewer
         */
        init() {
            console.log('Artifact viewer initialized');
        },
        
        /**
         * Set the current artifact to display
         * @param {Object} artifact - The artifact object with type, content, etc.
         */
        setArtifact(artifact) {
            this.artifact = artifact;
            this.isExpanded = true;
            this.isLoading = false;
        },
        
        /**
         * Clear the current artifact
         */
        clearArtifact() {
            this.artifact = null;
            this.isExpanded = true;
        },
        
        /**
         * Toggle expand/collapse state
         */
        toggle() {
            this.isExpanded = !this.isExpanded;
        },
        
        /**
         * Show loading state
         */
        showLoading() {
            this.isLoading = true;
            this.artifact = null;
        },
        
        /**
         * Hide loading state
         */
        hideLoading() {
            this.isLoading = false;
        },
        
        /**
         * Get the display info for the current artifact type
         * @returns {Object} Display info with icon, title, color
         */
        getArtifactInfo() {
            if (!this.artifact) return null;
            
            const type = this.artifact.artifact_type || 'spec';
            return this.artifactTypes[type] || this.artifactTypes.spec;
        },
        
        /**
         * Check if artifact has content
         * @returns {boolean} True if artifact has markdown or HTML content
         */
        hasContent() {
            return this.artifact && 
                   (this.artifact.content_markdown || this.artifact.content_html);
        },
        
        /**
         * Get the HTML content to display
         * @returns {string} HTML content or empty string
         */
        getHtmlContent() {
            if (!this.artifact) return '';
            return this.artifact.content_html || this.escapeHtml(this.artifact.content_markdown || '');
        },
        
        /**
         * Get the markdown content
         * @returns {string} Markdown content or empty string
         */
        getMarkdownContent() {
            if (!this.artifact) return '';
            return this.artifact.content_markdown || '';
        },
        
        /**
         * Escape HTML for safe display
         * @param {string} text - Text to escape
         * @returns {string} Escaped HTML
         */
        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },
        
        /**
         * Format generation time for display
         * @returns {string} Formatted time string
         */
        getGenerationTime() {
            if (!this.artifact || !this.artifact.generation_duration_ms) return '';
            
            const ms = this.artifact.generation_duration_ms;
            if (ms < 1000) return `${ms}ms`;
            return `${(ms / 1000).toFixed(2)}s`;
        },
        
        /**
         * Format token count for display
         * @returns {string} Formatted token count
         */
        getTokenCount() {
            if (!this.artifact || !this.artifact.tokens_used) return '';
            return this.artifact.tokens_used.toLocaleString();
        }
    };
}

// Export for use in main.js
window.artifactViewer = artifactViewer;
