// API Base URL
const API_URL = window.location.origin;

// Работа с токенами
function getAccessToken() {
    return localStorage.getItem('access_token');
}

function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}

function setTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
}

// API запрос с автоматическим refresh токена
async function apiRequest(url, options = {}) {
    const token = getAccessToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
    };

    let response = await fetch(url, { ...options, headers });

    // Если 401 — пробуем refresh
    if (response.status === 401) {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
            // Повторяем запрос с новым токеном
            const newToken = getAccessToken();
            headers['Authorization'] = `Bearer ${newToken}`;
            response = await fetch(url, { ...options, headers });
        } else {
            logout();
            return null;
        }
    }

    return response;
}

// Refresh токена
async function refreshAccessToken() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) return false;

    try {
        const res = await fetch(`${API_URL}/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken })
        });

        if (res.ok) {
            const data = await res.json();
            setTokens(data.access_token, data.refresh_token);
            return true;
        }
    } catch (e) {
        console.error('Refresh failed:', e);
    }
    return false;
}

// Проверка авторизации
function requireAuth() {
    if (!getAccessToken()) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// Форматирование даты
function formatDate(dateString) {
    return new Date(dateString).toLocaleString('ru-RU');
}
