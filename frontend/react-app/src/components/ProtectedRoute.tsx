import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]" style={{ color: 'var(--text-muted)' }}>
      <div className="text-center">
        <div
          className="w-8 h-8 border-2 rounded-full mx-auto mb-3"
          style={{
            borderColor: 'var(--border)',
            borderTopColor: 'var(--accent)',
            animation: 'spin 0.8s linear infinite',
          }}
        />
        <p className="text-sm">Načítám...</p>
      </div>
    </div>
  );
}

/** Přístup jen pro přihlášené uživatele */
export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <LoadingSpinner />;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

/** Přístup jen pro adminy */
export function AdminRoute({ children }: { children: React.ReactNode }) {
  const { user, loading, isAdmin } = useAuth();
  if (loading) return <LoadingSpinner />;
  if (!user) return <Navigate to="/login" replace />;
  if (!isAdmin) return <Navigate to="/" replace />;
  return <>{children}</>;
}
