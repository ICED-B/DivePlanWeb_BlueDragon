import { useState, FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Lock } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Button } from '../../components/ui/button';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';

function checkPassword(pw: string, t: (k: string) => string): string {
  if (pw.length < 12) return t('auth.pw_err_length');
  if (!/\d/.test(pw)) return t('auth.pw_err_digit');
  if (!/[a-z]/.test(pw)) return t('auth.pw_err_lower');
  if (!/[A-Z]/.test(pw)) return t('auth.pw_err_upper');
  if (!/[^\w\s]/.test(pw)) return t('auth.pw_err_special');
  return '';
}

export default function ChangePasswordPage() {
  const { t } = useTranslation();
  const [form, setForm] = useState({ stare_heslo: '', nove_heslo: '', nove_heslo_kontrola: '' });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const set = (f: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((p) => ({ ...p, [f]: e.target.value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(''); setSuccess('');
    if (form.nove_heslo !== form.nove_heslo_kontrola) {
      setError(t('auth.pw_err_mismatch'));
      return;
    }
    const pwErr = checkPassword(form.nove_heslo, t);
    if (pwErr) { setError(pwErr); return; }
    setLoading(true);
    try {
      await api.post('/auth/change-password', form);
      setSuccess(t('auth.change_password_success'));
      setForm({ stare_heslo: '', nove_heslo: '', nove_heslo_kontrola: '' });
    } catch (err: unknown) {
      const e2 = err as { response?: { data?: { message?: string } } };
      setError(e2?.response?.data?.message || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageContainer>
      <h1 className="text-3xl font-bold mb-8 flex items-center gap-3" style={{ color: 'var(--text)' }}>
        <Lock style={{ color: 'var(--accent)' }} size={28} />
        {t('auth.change_password')}
      </h1>
      <Card className="max-w-md">
        <CardHeader><CardTitle>{t('auth.change_password')}</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input label={t('auth.old_password')} type="password" value={form.stare_heslo} onChange={set('stare_heslo')} required />
            <Input label={t('auth.new_password')} type="password" value={form.nove_heslo} onChange={set('nove_heslo')} hint={t('auth.pass_hint')} required />
            <Input label={t('auth.confirm_password')} type="password" value={form.nove_heslo_kontrola} onChange={set('nove_heslo_kontrola')} required />
            {error && <p className="text-sm" style={{ color: 'var(--danger)' }}>{error}</p>}
            {success && <p className="text-sm" style={{ color: 'var(--success)' }}>{success}</p>}
            <Button type="submit" loading={loading}>{t('auth.change_password')}</Button>
          </form>
        </CardContent>
      </Card>
    </PageContainer>
  );
}
