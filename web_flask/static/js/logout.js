document.addEventListener('DOMContentLoaded', function() {
    // Get the login link
    const loginLink = document.querySelector('.login-link');
    
    if (loginLink) {
        loginLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Send a request to the server to ensure the session is cleared
            fetch('/logout', {
                method: 'GET',
                credentials: 'same-origin'
            }).then(() => {
                // Redirect to login page
                window.location.href = '/login';
            }).catch(error => {
                console.error('Logout error:', error);
                // Redirect anyway if there's an error
                window.location.href = '/login';
            });
        });
    }
});