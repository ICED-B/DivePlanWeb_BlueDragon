import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Format a number to fixed decimal places, trimming trailing zeros */
export function fmt(value: number | null | undefined, decimals = 1): string {
  if (value == null) return '—';
  return parseFloat(value.toFixed(decimals)).toString();
}

/** Format depth with unit */
export function fmtDepth(value: number | null | undefined, unit: 'm' | 'ft' = 'm'): string {
  if (value == null) return '—';
  return `${fmt(value, 1)} ${unit}`;
}

/** Format duration in minutes */
export function fmtDuration(minutes: number | null | undefined): string {
  if (minutes == null) return '—';
  const h = Math.floor(minutes / 60);
  const m = Math.round(minutes % 60);
  if (h > 0) return `${h}h ${m}min`;
  return `${m} min`;
}

/** Get Authorization header from localStorage token */
export function authHeader(): Record<string, string> {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/** Get user role from JWT token payload */
export function getRoleFromToken(): string | null {
  const token = localStorage.getItem('access_token');
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.role || payload.sub?.role || null;
  } catch {
    return null;
  }
}

/** Check if JWT token is expired */
export function isTokenExpired(): boolean {
  const token = localStorage.getItem('access_token');
  if (!token) return true;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

/** Decode JWT payload */
export function decodeToken(token: string): Record<string, unknown> | null {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch {
    return null;
  }
}
