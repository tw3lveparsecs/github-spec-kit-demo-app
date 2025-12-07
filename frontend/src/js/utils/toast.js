/**
 * Toast Notification Utility
 * 
 * Provides user feedback through toast notifications.
 */

const ToastManager = {
  container: null,
  defaultDuration: 3000,
  
  /**
   * Initialize the toast container.
   */
  init() {
    if (this.container) return;
    
    this.container = document.createElement('div');
    this.container.id = 'toast-container';
    this.container.className = 'toast-container';
    document.body.appendChild(this.container);
  },
  
  /**
   * Show a toast notification.
   * @param {string} message - The message to display
   * @param {string} type - Type of toast: 'success', 'error', 'warning', 'info'
   * @param {number} duration - How long to show the toast (ms)
   */
  show(message, type = 'info', duration = null) {
    this.init();
    
    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    
    const icon = this.getIcon(type);
    
    toast.innerHTML = `
      <span class="toast-icon">${icon}</span>
      <span class="toast-message">${this.escapeHtml(message)}</span>
      <button class="toast-close" aria-label="Close notification">×</button>
    `;
    
    // Add close handler
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => this.dismiss(toast));
    
    // Add to container
    this.container.appendChild(toast);
    
    // Trigger animation
    requestAnimationFrame(() => {
      toast.classList.add('toast--visible');
    });
    
    // Auto dismiss
    const dismissDuration = duration || this.defaultDuration;
    setTimeout(() => this.dismiss(toast), dismissDuration);
    
    return toast;
  },
  
  /**
   * Show success toast.
   * @param {string} message - The message
   * @param {number} duration - Duration in ms
   */
  success(message, duration) {
    return this.show(message, 'success', duration);
  },
  
  /**
   * Show error toast.
   * @param {string} message - The message
   * @param {number} duration - Duration in ms
   */
  error(message, duration = 5000) {
    return this.show(message, 'error', duration);
  },
  
  /**
   * Show warning toast.
   * @param {string} message - The message
   * @param {number} duration - Duration in ms
   */
  warning(message, duration) {
    return this.show(message, 'warning', duration);
  },
  
  /**
   * Show info toast.
   * @param {string} message - The message
   * @param {number} duration - Duration in ms
   */
  info(message, duration) {
    return this.show(message, 'info', duration);
  },
  
  /**
   * Dismiss a toast.
   * @param {HTMLElement} toast - The toast element to dismiss
   */
  dismiss(toast) {
    if (!toast || !toast.parentNode) return;
    
    toast.classList.remove('toast--visible');
    toast.classList.add('toast--hiding');
    
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  },
  
  /**
   * Get icon for toast type.
   * @param {string} type - Toast type
   * @returns {string} Icon SVG or emoji
   */
  getIcon(type) {
    const icons = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ'
    };
    return icons[type] || icons.info;
  },
  
  /**
   * Escape HTML to prevent XSS.
   * @param {string} text - Text to escape
   * @returns {string} Escaped text
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
};

// Export for use
window.Toast = ToastManager;
