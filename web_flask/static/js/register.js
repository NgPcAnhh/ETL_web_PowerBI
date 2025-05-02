document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.form');
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const username = document.querySelector('.input-mail').value.trim();
        const password = document.querySelector('.input-pwd').value.trim();
        const submitBtn = document.querySelector('.submit');
        const originalText = submitBtn.innerHTML;

        if (!username || !password) {
            showMessage('Please enter both username and password', 'error');
            return;
        }

        submitBtn.innerHTML = '<span class="sign-text">Registering...</span>';
        submitBtn.disabled = true;

        try {
            const res = await fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
                credentials: 'same-origin'
            });
            const data = await res.json();
            if (res.ok && data.success) {
                showMessage(data.message || 'Register successful!', 'success');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 1200);
            } else {
                showMessage(data.message || 'Register failed', 'error');
            }
        } catch (err) {
            showMessage('Connection error. Please try again later.', 'error');
        }
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });

    function showMessage(message, type) {
        let msgDiv = document.querySelector('.message-container');
        if (!msgDiv) {
            msgDiv = document.createElement('div');
            msgDiv.className = 'message-container';
            msgDiv.style.position = 'fixed';
            msgDiv.style.top = '30px';
            msgDiv.style.left = '50%';
            msgDiv.style.transform = 'translateX(-50%)';
            msgDiv.style.zIndex = '9999';
            msgDiv.style.padding = '12px 24px';
            msgDiv.style.borderRadius = '6px';
            msgDiv.style.fontWeight = 'bold';
            msgDiv.style.background = type === 'success' ? '#4caf50' : '#e53935';
            msgDiv.style.color = '#fff';
            document.body.appendChild(msgDiv);
        }
        msgDiv.textContent = message;
        msgDiv.style.display = 'block';
        setTimeout(() => { msgDiv.style.display = 'none'; }, 3500);
    }
});