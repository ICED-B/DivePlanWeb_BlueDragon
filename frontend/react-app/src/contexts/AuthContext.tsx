// src/contexts/AuthContext.tsx
import { createContext, useContext, useEffect, useState } from 'react';
import { decodeToken } from '../lib/utils';

export type UserInfo = {
  login: string;
  first_name: string | null;
  last_name: string | null;
  email: string | null;
  phone: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  role: string;          // decoded from JWT token
};

type AuthContextType = {
  user: UserInfo | null;
  loading: boolean;
  isAdmin: boolean;
  reloadUser: () => Promise<void>;
  login: (token: string, refreshToken?: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  isAdmin: false,
  reloadUser: async () => {},
  login: () => {},
  logout: () => {},
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);

  const getRoleFromToken = (): string => {
    const token = sessionStorage.getItem('access_token');
    if (!token) return 'user';
    const payload = decodeToken(token);
    return (payload?.role as string) || (payload?.sub as { role?: string })?.role || 'user';
  };

  /** Call POST /auth/refresh with the stored refresh_token. Returns true on success. */
  const doRefresh = async (): Promise<boolean> => {
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
  };

  const logout = () => {
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    setUser(null);
  };

  const reloadUser = async () => {
    const token = sessionStorage.getItem('access_token');
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    // If token is already expired, try refresh before /auth/me
    try {
      const payload = decodeToken(token);
      if (payload && (payload.exp as number) * 1000 < Date.now()) {
        const ok = await doRefresh();
        if (!ok) {
          logout();
          setLoading(false);
          return;
        }
      }
    } catch {
      // ignore decode errors
    }

    const currentToken = sessionStorage.getItem('access_token')!;
    try {
      const res = await fetch('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${currentToken}` },
      });
      if (!res.ok) throw new Error('Unauthorized');
      const data = await res.json();
      const role = getRoleFromToken();
      setUser({ ...data, role });
    } catch {
      setUser(null);
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('refresh_token');
    } finally {
      setLoading(false);
    }
  };

  const login = (token: string, refreshToken?: string) => {
    sessionStorage.setItem('access_token', token);
    if (refreshToken) sessionStorage.setItem('refresh_token', refreshToken);
    reloadUser();
  };

  useEffect(() => {
    reloadUser();

    // Check token expiry every 30 s — auto logout if expired and refresh fails
    const intervalId = setInterval(async () => {
      const token = sessionStorage.getItem('access_token');
      if (!token) return;
      try {
        const payload = decodeToken(token);
        if (payload && (payload.exp as number) * 1000 < Date.now()) {
          const ok = await doRefresh();
          if (ok) {
            const role = getRoleFromToken();
            setUser((prev) => (prev ? { ...prev, role } : prev));
          } else {
            logout();
            window.location.href = '/login';
          }
        }
      } catch {
        // ignore
      }
    }, 30_000);

    return () => clearInterval(intervalId);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const isAdmin = user?.role === 'admin';

  return (
    <AuthContext.Provider value={{ user, loading, isAdmin, reloadUser, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
