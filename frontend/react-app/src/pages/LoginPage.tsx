import { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { LogIn } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const { t } = useTranslation();
  const { login } = useAuth();
  const navigate = useNavigate();

  const [loginOrEmail, setLoginOrEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login_nebo_email: loginOrEmail, heslo: password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.message || t('auth.error_invalid'));
        return;
      }

      login(data.access_token, data.refresh_token);
      navigate('/dives');
    } catch {
      setError(t('auth.error_generic'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-56px)] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">

        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 mb-4">
            <img src="/blue_dragon_outline.svg" alt="logo" style={{ height: '56px', width: 'auto' }} />
          </div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text)' }}>{t('auth.login_title')}</h1>
          <p className="mt-1 text-sm" style={{ color: 'var(--text-muted)' }}>{t('auth.login_subtitle')}</p>
        </div>

        {/* Card */}
        <div className="card p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              label={t('auth.login_or_email')}
              type="text"
              value={loginOrEmail}
              onChange={(e) => setLoginOrEmail(e.target.value)}
              placeholder={t('auth.login_placeholder')}
              required
              autoFocus
            />
            <Input
              label={t('auth.password')}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />

            {error && (
              <div className="px-4 py-3 rounded-lg text-sm" style={{
                backgroundColor: 'color-mix(in srgb, var(--danger) 15%, transparent)',
                color: 'var(--danger)',
                border: '1px solid color-mix(in srgb, var(--danger) 30%, transparent)',
              }}>
                {error}
              </div>
            )}

            <Button type="submit" className="w-full gap-2" loading={loading}>
              <LogIn size={16} />
              {t('auth.login_button')}
            </Button>
          </form>
        </div>

        <p className="text-center mt-6 text-sm" style={{ color: 'var(--text-muted)' }}>
          {t('auth.login_link')}{' '}
          <Link to="/register" style={{ color: 'var(--accent)' }} className="font-medium hover:underline">
            {t('auth.login_link_register')}
          </Link>
        </p>
      </div>
    </div>
  );
}
