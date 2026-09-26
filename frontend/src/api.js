const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, { method = 'GET', body, token } = {}) {
  const headers = {};
  if (body) headers['Content-Type'] = 'application/json';
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch {
      /* response wasn't JSON */
    }
    throw new ApiError(detail, res.status);
  }

  if (res.status === 204) return null;
  return res.json();
}

export async function login(email, password) {
  const form = new URLSearchParams();
  form.set('username', email);
  form.set('password', password);

  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new ApiError(data.detail || 'Login failed', res.status);
  }
  return res.json(); // { access_token, token_type }
}

export const api = {
  dashboardSummary: (token) => request('/dashboard/summary', { token }),
  listTransactions: (token, { skip = 0, limit = 50 } = {}) =>
    request(`/transactions?skip=${skip}&limit=${limit}`, { token }),
  createTransaction: (token, payload) =>
    request('/transactions', { method: 'POST', body: payload, token }),
  createRefund: (token, payload) =>
    request('/refunds', { method: 'POST', body: payload, token }),
  listRefunds: (token) => request('/refunds', { token }),
};

export { ApiError };
