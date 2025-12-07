/**
 * Presenter Notes Component
 * 
 * Displays context-specific talking points for demo presenters.
 * Shows notes based on current workflow phase, scenario, or feature context.
 */

function presenterNotes() {
  return {
    // State
    notes: [],
    isLoading: false,
    isPanelVisible: false,
    currentContext: {
      type: 'phase',
      id: 'specify'
    },
    expandedNotes: {},
    
    /**
     * Initialize the presenter notes component.
     */
    init() {
      // Listen for context changes
      window.addEventListener('workflow-phase-changed', (e) => {
        this.updateContext('phase', e.detail.phase);
      });
      
      window.addEventListener('scenario-selected', (e) => {
        this.updateContext('scenario', e.detail.scenarioId);
      });
    },
    
    /**
     * Toggle the presenter notes panel visibility.
     */
    togglePanel() {
      this.isPanelVisible = !this.isPanelVisible;
      if (this.isPanelVisible && this.notes.length === 0) {
        this.loadNotes();
      }
    },
    
    /**
     * Update the context and reload notes.
     * @param {string} type - Context type (phase, scenario, feature)
     * @param {string} id - Context ID
     */
    updateContext(type, id) {
      this.currentContext = { type, id };
      if (this.isPanelVisible) {
        this.loadNotes();
      }
    },
    
    /**
     * Load notes for the current context.
     */
    async loadNotes() {
      this.isLoading = true;
      
      try {
        const { type, id } = this.currentContext;
        const response = await fetch(`/api/presenter-notes/${type}/${id}`);
        
        if (!response.ok) {
          throw new Error(`Failed to load notes: ${response.status}`);
        }
        
        this.notes = await response.json();
      } catch (error) {
        console.error('Error loading presenter notes:', error);
        this.notes = [];
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * Load all notes.
     */
    async loadAllNotes() {
      this.isLoading = true;
      
      try {
        const response = await fetch('/api/presenter-notes');
        
        if (!response.ok) {
          throw new Error(`Failed to load notes: ${response.status}`);
        }
        
        this.notes = await response.json();
      } catch (error) {
        console.error('Error loading presenter notes:', error);
        this.notes = [];
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * Toggle a note's expanded state.
     * @param {string} noteId - The note ID to toggle
     */
    toggleNote(noteId) {
      this.expandedNotes[noteId] = !this.expandedNotes[noteId];
    },
    
    /**
     * Check if a note is expanded.
     * @param {string} noteId - The note ID to check
     * @returns {boolean}
     */
    isNoteExpanded(noteId) {
      return this.expandedNotes[noteId] || false;
    },
    
    /**
     * Get emphasis class for a note.
     * @param {number} level - Emphasis level (1-3)
     * @returns {string} CSS class
     */
    getEmphasisClass(level) {
      const classes = {
        1: 'emphasis-low',
        2: 'emphasis-medium',
        3: 'emphasis-high'
      };
      return classes[level] || 'emphasis-low';
    },
    
    /**
     * Get timing badge class.
     * @param {string} timing - Timing value (before, during, after)
     * @returns {string} CSS class
     */
    getTimingClass(timing) {
      const classes = {
        'before': 'timing-before',
        'during': 'timing-during',
        'after': 'timing-after'
      };
      return classes[timing] || '';
    },
    
    /**
     * Get timing display text.
     * @param {string} timing - Timing value
     * @returns {string} Display text
     */
    getTimingText(timing) {
      const texts = {
        'before': 'Before',
        'during': 'During',
        'after': 'After'
      };
      return texts[timing] || '';
    },
    
    /**
     * Get context type icon.
     * @param {string} type - Context type
     * @returns {string} Icon class
     */
    getContextIcon(type) {
      const icons = {
        'phase': 'play-circle',
        'scenario': 'file-text',
        'feature': 'star'
      };
      return icons[type] || 'info';
    },
    
    /**
     * Get notes filtered by timing.
     * @param {string} timing - Timing filter
     * @returns {Array} Filtered notes
     */
    getNotesByTiming(timing) {
      return this.notes.filter(note => note.timing === timing);
    },
    
    /**
     * Check if there are any notes.
     * @returns {boolean}
     */
    hasNotes() {
      return this.notes.length > 0;
    },
    
    /**
     * Get the current context display text.
     * @returns {string}
     */
    getContextDisplay() {
      const { type, id } = this.currentContext;
      return `${type}: ${id}`;
    }
  };
}

// Export for use in Alpine.js
window.presenterNotes = presenterNotes;
