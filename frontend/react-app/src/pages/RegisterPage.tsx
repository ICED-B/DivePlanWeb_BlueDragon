import { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { UserPlus } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { useAuth } from '../contexts/AuthContext';

function checkPassword(pw: string, t: (k: string) => string): string {
  if (pw.length < 12) return t('auth.pw_err_length');
  if (!/\d/.test(pw)) return t('auth.pw_err_digit');
  if (!/[a-z]/.test(pw)) return t('auth.pw_err_lower');
  if (!/[A-Z]/.test(pw)) return t('auth.pw_err_upper');
  if (!/[^\w\s]/.test(pw)) return t('auth.pw_err_special');
  return '';
}

export default function RegisterPage() {
  const { t } = useTranslation();
  const { login } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    login: '', heslo: '', first_name: '', last_name: '', email: '', phone: '',
  });
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((p) => ({ ...p, [field]: e.target.value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    const pwErr = checkPassword(form.heslo, t);
    if (pwErr) { setError(pwErr); return; }
    if (!termsAccepted) { setError(t('auth.terms_required')); return; }
    setLoading(true);

    try {
      const res = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });

      const data = await res.json();
      if (!res.ok) {
        setError(data.message || t('auth.error_generic'));
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

        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 mb-4">
            <img src="/blue_dragon_outline.svg" alt="logo" style={{ height: '56px', width: 'auto' }} />
          </div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text)' }}>{t('auth.register_title')}</h1>
          <p className="mt-1 text-sm" style={{ color: 'var(--text-muted)' }}>{t('auth.register_subtitle')}</p>
        </div>

        <div className="card p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label={t('auth.login_field')}
              type="text"
              value={form.login}
              onChange={set('login')}
              placeholder={t('auth.login_placeholder')}
              required
              autoFocus
            />
            <div className="grid grid-cols-2 gap-3">
              <Input
                label={t('auth.first_name')}
                type="text"
                value={form.first_name}
                onChange={set('first_name')}
              />
              <Input
                label={t('auth.last_name')}
                type="text"
                value={form.last_name}
                onChange={set('last_name')}
              />
            </div>
            <Input
              label={t('auth.email')}
              type="email"
              value={form.email}
              onChange={set('email')}
              placeholder="email@example.com"
            />
            <Input
              label={t('auth.phone')}
              type="tel"
              value={form.phone}
              onChange={set('phone')}
              placeholder="+420 123 456 789"
            />
            <Input
              label={t('auth.password')}
              type="password"
              value={form.heslo}
              onChange={set('heslo')}
              placeholder="••••••••"
              hint={t('auth.pass_hint')}
              required
            />

            {/* Terms consent */}
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={termsAccepted}
                onChange={e => setTermsAccepted(e.target.checked)}
                className="mt-0.5 flex-shrink-0"
                style={{ accentColor: 'var(--accent)', width: '16px', height: '16px' }}
              />
              <span className="text-sm" style={{ color: 'var(--text-muted)' }}>
                {t('auth.terms_consent', {
                  terms: '',
                  privacy: '',
                }).split('{terms}')[0]}
                <Link to="/terms" target="_blank" style={{ color: 'var(--accent)' }} className="hover:underline">
                  {t('auth.terms_consent_terms')}
                </Link>
                {t('auth.terms_consent', {
                  terms: '',
                  privacy: '',
                }).split('{terms}')[1]?.split('{privacy}')[0]}
                <Link to="/privacy" target="_blank" style={{ color: 'var(--accent)' }} className="hover:underline">
                  {t('auth.terms_consent_privacy')}
                </Link>
              </span>
            </label>

            {error && (
              <div className="px-4 py-3 rounded-lg text-sm" style={{
                backgroundColor: 'color-mix(in srgb, var(--danger) 15%, transparent)',
                color: 'var(--danger)',
                border: '1px solid color-mix(in srgb, var(--danger) 30%, transparent)',
              }}>
                {error}
              </div>
            )}

            <Button type="submit" className="w-full gap-2 mt-2" loading={loading}>
              <UserPlus size={16} />
              {t('auth.register_button')}
            </Button>
          </form>
        </div>

        <p className="text-center mt-6 text-sm" style={{ color: 'var(--text-muted)' }}>
          {t('auth.register_link')}{' '}
          <Link to="/login" style={{ color: 'var(--accent)' }} className="font-medium hover:underline">
            {t('auth.register_link_login')}
          </Link>
        </p>
      </div>
    </div>
  );
}
