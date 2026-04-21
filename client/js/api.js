// Shared API helper for authenticated dashboard pages — uses current origin
const API_URL = window.location.origin;

function getToken() {
    return localStorage.getItem('spotter_token');
}

function getUserRole() {
    return localStorage.getItem('spotter_role');
}

function getUserName() {
    return localStorage.getItem('spotter_name') || 'User';
}

function logout() {
    localStorage.removeItem('spotter_token');
    localStorage.removeItem('spotter_role');
    localStorage.removeItem('spotter_name');
    window.location.href = 'index.html';
}

// Guard: redirect to login if not authenticated
function requireAuth(allowedRoles = []) {
    const token = getToken();
    const role = getUserRole();
    if (!token) {
        window.location.href = 'index.html';
        return false;
    }
    if (allowedRoles.length > 0 && !allowedRoles.includes(role)) {
        window.location.href = 'index.html';
        return false;
    }
    return true;
}

// Authenticated fetch wrapper
async function apiFetch(endpoint, options = {}) {
    const token = getToken();
    const defaultHeaders = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
    };
    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers: { ...defaultHeaders, ...options.headers },
    });

    if (response.status === 401) {
        logout();
        return null;
    }

    return response;
}

// Toast notification
function showToast(message, type = 'success') {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icon = type === 'success' ? 'check_circle' : 'error';
    toast.innerHTML = `<i class="material-icons-round">${icon}</i><span>${message}</span>`;
    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Format date strings
function formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

// Status badge helper
function statusBadge(status) {
    const colors = {
        reported: '#f59e0b',
        found: '#10b981',
        reserved: '#6366f1',
        claimed: '#ec4899',
        closed: '#64748b',
        pending: '#f59e0b',
        approved: '#10b981',
        rejected: '#ef4444',
        expired: '#64748b',
    };
    const color = colors[status] || '#94a3b8';
    return `<span class="status-badge" style="--badge-color: ${color}">${status}</span>`;
}
