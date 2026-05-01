import { useState, FormEvent, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Button } from '../../components/ui/button';
import { PageContainer } from '../../components/Layout';
import { User, Mail, Phone, Calendar, Shield, Edit2, X } from 'lucide-react';
import api from '../../lib/api';

type ProfileData = {
  login: string;
  first_name: string | null;
  last_name: string | null;
  email: string | null;
  phone: string | null;
  created_at: string;
  updated_at: string;
};

export default function ProfilePage() {
  const { t } = useTranslation();
  const { user, reloadUser, isAdmin } = useAuth();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ login: '', first_name: '', last_name: '', email: '', phone: '' });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get<ProfileData>('/app-users/me').then((res) => setProfile(res.data)).catch(() => {});
  }, []);

  if (!user) return null;

  const data = profile ?? user;

  const startEdit = () => {
    setForm({
      login: data.login,
      first_name: data.first_name || '',
      last_name: data.last_name || '',
      email: data.email || '',
      phone: data.phone || '',
    });
    setError('');
    setEditing(true);
  };

  const handleSave = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const res = await api.patch<ProfileData>('/app-users/me', form);
      setProfile(res.data);
      await reloadUser();
      setEditing(false);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message;
      setError(msg || t('common.error'));
    } finally {
      setSaving(false);
    }
  };

  const set = (f: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((p) => ({ ...p, [f]: e.target.value }));

  const fields = [
    { icon: <User size={16} />, label: t('auth.login_field'),        value: data.login },
    { icon: <User size={16} />, label: t('auth.first_name'),         value: data.first_name || '—' },
    { icon: <User size={16} />, label: t('auth.last_name'),          value: data.last_name || '—' },
    { icon: <Mail size={16} />, label: t('auth.email'),              value: data.email || '—' },
    { icon: <Phone size={16} />, label: t('auth.phone'),             value: data.phone || '—' },
    { icon: <Calendar size={16} />, label: t('profile.member_since'), value: data.created_at },
    { icon: <Calendar size={16} />, label: t('profile.last_updated'), value: data.updated_at },
    { icon: <Shield size={16} />, label: 'Role',                     value: isAdmin ? 'Admin' : 'User' },
  ];

  return (
    <PageContainer>
      <h1 className="text-3xl font-bold mb-8 flex items-center gap-3" style={{ color: 'var(--text)' }}>
        <User style={{ color: 'var(--accent)' }} size={28} />
        {t('profile.title')}
      </h1>

      <Card className="max-w-xl">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>{t('profile.my_info')}</CardTitle>
            {!editing && (
              <Button variant="outline" size="sm" onClick={startEdit}>
                <Edit2 size={14} />
                {t('profile.edit')}
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {editing ? (
            <form onSubmit={handleSave} className="space-y-4">
              <Input label={t('auth.login_field')} value={form.login} onChange={set('login')} required />
              <div className="grid grid-cols-2 gap-3">
                <Input label={t('auth.first_name')} value={form.first_name} onChange={set('first_name')} />
                <Input label={t('auth.last_name')} value={form.last_name} onChange={set('last_name')} />
              </div>
              <Input label={t('auth.email')} type="email" value={form.email} onChange={set('email')} />
              <Input label={t('auth.phone')} type="tel" value={form.phone} onChange={set('phone')} />
              {error && <p className="text-sm" style={{ color: 'var(--danger)' }}>{error}</p>}
              <div className="flex gap-2">
                <Button type="submit" loading={saving}>{t('profile.save')}</Button>
                <Button type="button" variant="ghost" onClick={() => setEditing(false)}>
                  <X size={14} />
                  {t('profile.cancel')}
                </Button>
              </div>
            </form>
          ) : (
            <dl className="space-y-1">
              {fields.map(({ icon, label, value }) => (
                <div
                  key={label}
                  className="flex items-center gap-3 py-2"
                  style={{ borderBottom: '1px solid var(--border-muted)' }}
                >
                  <span style={{ color: 'var(--text-muted)' }}>{icon}</span>
                  <span className="text-sm w-36 flex-shrink-0" style={{ color: 'var(--text-muted)' }}>{label}</span>
                  <span className="text-sm font-medium" style={{ color: 'var(--text)' }}>{value}</span>
                </div>
              ))}
            </dl>
          )}
        </CardContent>
      </Card>
    </PageContainer>
  );
}
