import axios from 'axios';
import { decodeToken } from './utils';

// Allow _retry flag on request config to prevent infinite loops
declare module 'axios' {
  interface InternalAxiosRequestConfig {
    _retry?: boolean;
  }
}

/** Central axios instance with auth header */
const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

/** Try to reload access token witch refresh token. true is for success */
async function tryRefresh(): Promise<boolean> {
  const rt = sessionStorage.getItem('refresh_token');
  if (!rt) return false;
  try {
    const res = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      headers: { Authorization: `Bearer ${rt}` },
    });
    if (!res.ok) return false;
    const data = await res.json();
    sessionStorage.setItem('access_token', data.access_token);
    sessionStorage.setItem('refresh_token', data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

// Request interceptor — add bearer token, proactive refresh if it might runout in < 5 min
api.interceptors.request.use(async (config) => {
  let token = sessionStorage.getItem('access_token');
  if (token) {
    try {
      const payload = decodeToken(token);
      const expiresAt = (payload?.exp as number) * 1000;
      const timeLeft = expiresAt - Date.now();
      // Pokud token vyprší za méně než 5 minut, obnov ho před odesláním
      if (timeLeft < 5 * 60 * 1000 && timeLeft > 0) {
        const ok = await tryRefresh();
        if (ok) {
          token = sessionStorage.getItem('access_token');
        }
      }
    } catch {
      // ignore decode errors, proceed with original token
    }
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor — on 401 try refresh token, then logout
api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config;
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true;
      const ok = await tryRefresh();
      if (ok) {
        const newToken = sessionStorage.getItem('access_token');
        original.headers.Authorization = `Bearer ${newToken}`;
        return api(original);
      }
      // Refresh failed
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('refresh_token');
      const publicPaths = ['/', '/login', '/register', '/planner', '/stats'];
      const isPublic = publicPaths.some((p) => window.location.pathname.startsWith(p));
      if (!isPublic) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(err);
  }
);

export default api;
