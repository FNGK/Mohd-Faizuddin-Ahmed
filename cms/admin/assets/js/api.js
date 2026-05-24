const API_BASE = '/api/v1';

export function getTokens() {
  return {
    access: localStorage.getItem('cms_access') || '',
    refresh: localStorage.getItem('cms_refresh') || '',
  };
}

export function setTokens(access, refresh) {
  localStorage.setItem('cms_access', access);
  localStorage.setItem('cms_refresh', refresh);
}

export function clearTokens() {
  localStorage.removeItem('cms_access');
  localStorage.removeItem('cms_refresh');
  localStorage.removeItem('cms_user');
}

export function setUser(user) {
  localStorage.setItem('cms_user', JSON.stringify(user));
}

export function getUser() {
  try {
    return JSON.parse(localStorage.getItem('cms_user') || 'null');
  } catch {
    return null;
  }
}

async function refreshAccess() {
  const { refresh } = getTokens();
  if (!refresh) throw new Error('No refresh token');
  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refresh }),
  });
  if (!res.ok) throw new Error('Session expired');
  const data = await res.json();
  setTokens(data.access_token, data.refresh_token);
  return data.access_token;
}

export async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  let { access } = getTokens();
  if (access) headers.set('Authorization', `Bearer ${access}`);

  let res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (res.status === 401 && getTokens().refresh) {
    access = await refreshAccess();
    headers.set('Authorization', `Bearer ${access}`);
    res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  }
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { detail: text };
  }
  if (!res.ok) {
    const msg = data?.detail?.errors?.join?.(' ') || data?.detail || data?.message || res.statusText;
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
  }
  return data;
}

export const Auth = {
  login: async (email, password, totpCode, totpToken) => {
    if (totpCode && totpToken) {
      const data = await api('/auth/login/totp', {
        method: 'POST',
        body: JSON.stringify({ totp_token: totpToken, code: totpCode }),
      });
      setTokens(data.access_token, data.refresh_token);
      return data;
    }
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Login failed');
    if (data.requires_totp) return data;
    setTokens(data.access_token, data.refresh_token);
    return data;
  },
  me: () => api('/auth/me'),
  logout: () => {
    const { refresh } = getTokens();
    return api('/auth/logout', { method: 'POST', body: JSON.stringify({ refresh_token: refresh }) }).catch(
      () => {}
    );
  },
};
