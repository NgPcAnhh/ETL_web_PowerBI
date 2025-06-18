class SessionTimeout {
    constructor(options = {}) {
        this.options = {
            inactivityTime: 5 * 60 * 1000, // 5 minutes in milliseconds
            logoutUrl: '/logout',
            redirectUrl: '/login',
            warningTime: 1 * 60 * 1000, // Show warning 1 minute before timeout
            ...options
        };
        
        this.timer = null;
        this.warningTimer = null;
        this.warningShown = false;
        
        this.init();
    }
    
    init() {
        // Don't initialize on login or logout pages
        if (window.location.pathname === '/login' || 
            window.location.pathname === '/logout') {
            return;
        }
        
        // Start tracking inactivity
        this.resetTimer();
        
        // Monitor user activity
        document.addEventListener('mousemove', () => this.resetTimer());
        document.addEventListener('mousedown', () => this.resetTimer());
        document.addEventListener('keypress', () => this.resetTimer());
        document.addEventListener('touchmove', () => this.resetTimer());
        document.addEventListener('scroll', () => this.resetTimer());
        
        console.log('Session timeout monitoring initialized');
    }
    
    resetTimer() {
        // Clear existing timers
        clearTimeout(this.timer);
        clearTimeout(this.warningTimer);
        
        // Hide warning if shown
        if (this.warningShown) {
            this.hideWarningMessage();
        }
        
        // Set warning timer
        this.warningTimer = setTimeout(() => {
            this.showWarningMessage();
        }, this.options.inactivityTime - this.options.warningTime);
        
        // Set logout timer
        this.timer = setTimeout(() => {
            this.logout();
        }, this.options.inactivityTime);
    }
    
    showWarningMessage() {
        this.warningShown = true;
        
        // Create warning message element if it doesn't exist
        let warningEl = document.getElementById('session-timeout-warning');
        if (!warningEl) {
            warningEl = document.createElement('div');
            warningEl.id = 'session-timeout-warning';
            warningEl.style.position = 'fixed';
            warningEl.style.top = '20px';
            warningEl.style.right = '20px';
            warningEl.style.backgroundColor = '#ff9800';
            warningEl.style.color = 'white';
            warningEl.style.padding = '15px';
            warningEl.style.borderRadius = '5px';
            warningEl.style.zIndex = '10000';
            warningEl.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
            document.body.appendChild(warningEl);
        }
        
        // Calculate minutes remaining
        const minutesRemaining = Math.ceil(this.options.warningTime / 60000);
        
        // Set warning message content
        warningEl.innerHTML = `
            <div>
                <strong>Session Timeout Warning</strong>
                <p>Your session will expire in ${minutesRemaining} minute(s) due to inactivity.</p>
                <button id="session-continue-btn" style="background: #4CAF50; border: none; color: white; padding: 5px 10px; border-radius: 3px; cursor: pointer; margin-right: 10px;">Continue Session</button>
                <button id="session-logout-btn" style="background: #F44336; border: none; color: white; padding: 5px 10px; border-radius: 3px; cursor: pointer;">Logout Now</button>
            </div>
        `;
        
        // Add event listeners to buttons
        document.getElementById('session-continue-btn').addEventListener('click', () => {
            this.resetTimer();
        });
        
        document.getElementById('session-logout-btn').addEventListener('click', () => {
            this.logout();
        });
    }
    
    hideWarningMessage() {
        this.warningShown = false;
        const warningEl = document.getElementById('session-timeout-warning');
        if (warningEl) {
            warningEl.remove();
        }
    }
    
    logout() {
        // Send logout request to the server
        fetch(this.options.logoutUrl, {
            method: 'GET',
            credentials: 'same-origin'
        }).finally(() => {
            // Redirect to login page
            window.location.href = this.options.redirectUrl;
        });
    }
}

// Initialize session timeout
document.addEventListener('DOMContentLoaded', () => {
    new SessionTimeout();
});