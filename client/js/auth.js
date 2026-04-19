// Base URL for the FastAPI backend
const API_URL = 'http://localhost:8000';

// Helper function to show toasts
function showToast(message, type = 'success') {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    // Add icon based on type
    const icon = type === 'success' ? 'check_circle' : 'error';
    toast.innerHTML = `<i class="material-icons-round">${icon}</i><span>${message}</span>`;
    
    document.body.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Remove after 3s
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Check if already logged in
function checkAuthStatus() {
    const token = localStorage.getItem('spotter_token');
    const role = localStorage.getItem('spotter_role');
    
    if (token && role) {
        redirectToDashboard(role);
    }
}

// Redirect based on role
function redirectToDashboard(role) {
    if (role === 'student') window.location.href = 'student.html';
    else if (role === 'finder') window.location.href = 'finder.html';
    else if (role === 'faculty') window.location.href = 'faculty.html';
    else window.location.href = 'index.html';
}

// Handle Login
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('login-btn');
    const originalText = btn.innerHTML;
    
    btn.innerHTML = '<span>Signing in...</span>';
    btn.disabled = true;

    try {
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        // FastAPI OAuth2PasswordRequestForm expects form data (x-www-form-urlencoded)
        const formData = new URLSearchParams();
        formData.append('username', email); // OAuth2 expects 'username'
        formData.append('password', password);

        const response = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }

        // Store JWT and user data
        localStorage.setItem('spotter_token', data.access_token);
        
        // Fetch profile to get the role
        // Use role/name from login response directly
        localStorage.setItem('spotter_role', data.role);
        localStorage.setItem('spotter_name', data.full_name || '');
        const role = data.role;


        showToast('Login successful!');
        setTimeout(() => redirectToDashboard(role), 1000);

    } catch (error) {
        showToast(error.message, 'error');
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
});

// Handle Signup
document.getElementById('signup-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('signup-btn');
    const originalText = btn.innerHTML;
    
    btn.innerHTML = '<span>Creating Account...</span>';
    btn.disabled = true;

    try {
        const name = document.getElementById('signup-name').value;
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;
        const role = document.getElementById('signup-role').value;

        const response = await fetch(`${API_URL}/api/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email,
                password,
                full_name: name,
                role
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Signup failed');
        }

        showToast('Account created successfully! Please log in.');
        
        // Switch to login tab
        setTimeout(() => {
            document.querySelector('.auth-tab[data-tab="login"]').click();
            document.getElementById('login-email').value = email;
            document.getElementById('login-password').value = '';
            btn.innerHTML = originalText;
            btn.disabled = false;
        }, 1500);

    } catch (error) {
        showToast(error.message, 'error');
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
});

// Run check on load
document.addEventListener('DOMContentLoaded', checkAuthStatus);
