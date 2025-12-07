/**
 * Animation Helpers
 * 
 * Utility functions for animations including typing effect, transitions, and loading states.
 */

/**
 * Typing animation for text content
 * @param {HTMLElement} element - The element to animate
 * @param {string} text - The text to type out
 * @param {number} speed - Typing speed in milliseconds per character (default: 20)
 * @returns {Promise} Resolves when animation is complete
 */
export function typeText(element, text, speed = 20) {
    return new Promise((resolve) => {
        let index = 0;
        element.textContent = '';
        element.style.display = 'inline-block';
        
        const interval = setInterval(() => {
            if (index < text.length) {
                element.textContent += text.charAt(index);
                index++;
            } else {
                clearInterval(interval);
                resolve();
            }
        }, speed);
    });
}

/**
 * Fade in animation
 * @param {HTMLElement} element - The element to fade in
 * @param {number} duration - Animation duration in milliseconds (default: 300)
 * @returns {Promise} Resolves when animation is complete
 */
export function fadeIn(element, duration = 300) {
    return new Promise((resolve) => {
        element.style.opacity = '0';
        element.style.display = 'block';
        element.style.transition = `opacity ${duration}ms ease-in-out`;
        
        // Force reflow
        element.offsetHeight;
        
        element.style.opacity = '1';
        
        setTimeout(() => {
            element.style.transition = '';
            resolve();
        }, duration);
    });
}

/**
 * Fade out animation
 * @param {HTMLElement} element - The element to fade out
 * @param {number} duration - Animation duration in milliseconds (default: 300)
 * @returns {Promise} Resolves when animation is complete
 */
export function fadeOut(element, duration = 300) {
    return new Promise((resolve) => {
        element.style.opacity = '1';
        element.style.transition = `opacity ${duration}ms ease-in-out`;
        
        element.style.opacity = '0';
        
        setTimeout(() => {
            element.style.display = 'none';
            element.style.transition = '';
            resolve();
        }, duration);
    });
}

/**
 * Slide in animation from top
 * @param {HTMLElement} element - The element to slide in
 * @param {number} duration - Animation duration in milliseconds (default: 400)
 * @returns {Promise} Resolves when animation is complete
 */
export function slideInDown(element, duration = 400) {
    return new Promise((resolve) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(-20px)';
        element.style.display = 'block';
        element.style.transition = `opacity ${duration}ms ease-out, transform ${duration}ms ease-out`;
        
        // Force reflow
        element.offsetHeight;
        
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
        
        setTimeout(() => {
            element.style.transition = '';
            element.style.transform = '';
            resolve();
        }, duration);
    });
}

/**
 * Slide in animation from right
 * @param {HTMLElement} element - The element to slide in
 * @param {number} duration - Animation duration in milliseconds (default: 400)
 * @returns {Promise} Resolves when animation is complete
 */
export function slideInRight(element, duration = 400) {
    return new Promise((resolve) => {
        element.style.opacity = '0';
        element.style.transform = 'translateX(30px)';
        element.style.display = 'block';
        element.style.transition = `opacity ${duration}ms ease-out, transform ${duration}ms ease-out`;
        
        // Force reflow
        element.offsetHeight;
        
        element.style.opacity = '1';
        element.style.transform = 'translateX(0)';
        
        setTimeout(() => {
            element.style.transition = '';
            element.style.transform = '';
            resolve();
        }, duration);
    });
}

/**
 * Show loading spinner
 * @param {HTMLElement} container - Container element for the spinner
 * @returns {HTMLElement} The spinner element
 */
export function showLoadingSpinner(container) {
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    spinner.innerHTML = `
        <div class="spinner-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <circle class="spinner-circle" cx="12" cy="12" r="10" stroke="currentColor" 
                        stroke-width="3" fill="none" stroke-linecap="round" />
            </svg>
        </div>
        <span class="spinner-text">Loading...</span>
    `;
    
    container.appendChild(spinner);
    return spinner;
}

/**
 * Hide and remove loading spinner
 * @param {HTMLElement} spinner - The spinner element to remove
 * @param {number} delay - Delay before removal in milliseconds (default: 0)
 */
export function hideLoadingSpinner(spinner, delay = 0) {
    setTimeout(() => {
        if (spinner && spinner.parentNode) {
            fadeOut(spinner, 200).then(() => {
                spinner.remove();
            });
        }
    }, delay);
}

/**
 * Pulse animation for emphasis
 * @param {HTMLElement} element - The element to pulse
 * @param {number} count - Number of pulses (default: 2)
 * @returns {Promise} Resolves when animation is complete
 */
export function pulse(element, count = 2) {
    return new Promise((resolve) => {
        element.style.animation = `pulse 0.5s ease-in-out ${count}`;
        
        setTimeout(() => {
            element.style.animation = '';
            resolve();
        }, count * 500);
    });
}

/**
 * Progress bar animation
 * @param {HTMLElement} progressBar - The progress bar element
 * @param {number} targetPercent - Target percentage (0-100)
 * @param {number} duration - Animation duration in milliseconds (default: 500)
 * @returns {Promise} Resolves when animation is complete
 */
export function animateProgress(progressBar, targetPercent, duration = 500) {
    return new Promise((resolve) => {
        const start = parseFloat(progressBar.style.width) || 0;
        const end = Math.min(100, Math.max(0, targetPercent));
        const diff = end - start;
        const startTime = performance.now();
        
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Ease-out animation
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            const current = start + (diff * easeProgress);
            
            progressBar.style.width = `${current}%`;
            
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                resolve();
            }
        }
        
        requestAnimationFrame(update);
    });
}

// Export all functions as a single object
export const animations = {
    typeText,
    fadeIn,
    fadeOut,
    slideInDown,
    slideInRight,
    showLoadingSpinner,
    hideLoadingSpinner,
    pulse,
    animateProgress
};

// Make available globally
window.animations = animations;
