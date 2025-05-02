document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('.form');
    
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault(); // Prevent default form submission
        
        // Get input values
        const username = document.querySelector('.input-mail').value;
        const password = document.querySelector('.input-pwd').value;
        
        // Validate input
        if (!username || !password) {
            showMessage('Please enter both username and password', 'error');
            return;
        }
        
        // Create loading state
        const submitButton = document.querySelector('.submit');
        const originalButtonText = submitButton.innerHTML;
        submitButton.innerHTML = '<span class="sign-text">Loading...</span>';
        submitButton.disabled = true;
        
        try {
            // Send login request to backend
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                }),
                credentials: 'same-origin' // Include cookies in the request
            });
            
            const data = await response.json();

            if (response.ok) {
                // Login successful
                showMessage(data.message || 'Login successful! Redirecting...', 'success');
                setTimeout(() => {
                    if (data.status === 7) {
                        window.location.href = '/admin';
                    } else {
                        window.location.href = '/main';
                    }
                }, 1000);
            } else {
                // Login failed
                showMessage(data.message || 'Invalid username or password', 'error');
                submitButton.innerHTML = originalButtonText;
                submitButton.disabled = false;
            }
        } catch (error) {
            console.error('Login error:', error);
            showMessage('Connection error. Please try again later.', 'error');
            submitButton.innerHTML = originalButtonText;
            submitButton.disabled = false;
        }
    });
    
    // Function to show messages to the user
    function showMessage(message, type) {
        // Check if message container exists, create if not
        let messageContainer = document.querySelector('.message-container');
        if (!messageContainer) {
            messageContainer = document.createElement('div');
            messageContainer.className = 'message-container';
            loginForm.insertAdjacentElement('beforebegin', messageContainer);
        }
        
        // Create and style message element
        messageContainer.innerHTML = `<div class="message ${type}">${message}</div>`;
        
        // Auto-remove message after 5 seconds
        setTimeout(() => {
            messageContainer.innerHTML = '';
        }, 5000);
    }
});


