import { useEffect, useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Users, Plus } from 'lucide-react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input, Select } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, EmptyTableRow } from '../../components/ui/table';
import { Dialog, DialogHeader, DialogContent, DialogFooter } from '../../components/ui/dialog';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';

interface AppUser {
  user_id: number;
  login: string;
  email: string | null;
  first_name: string | null;
  last_name: string | null;
  phone: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
}

const emptyForm = () => ({
  login: '', password: '', email: '', first_name: '', last_name: '',
  phone: '', role: 'user', is_active: 'true',
});

export default function AdminUsersPage() {
  const { t } = useTranslation();
  const [users, setUsers] = useState<AppUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [editItem, setEditItem] = useState<AppUser | null>(null);
  const [form, setForm] = useState(emptyForm());
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');
  const [confirmTarget, setConfirmTarget] = useState<{ user: AppUser; action: 'deactivate' | 'activate' } | null>(null);

  const ROLE_OPTIONS = useMemo(() => [
    { value: 'user',  label: t('admin.role_user') },
    { value: 'admin', label: t('admin.role_admin') },
  ], [t]);

  const ACTIVE_OPTIONS = useMemo(() => [
    { value: 'true',  label: t('admin.active') },
    { value: 'false', label: t('admin.inactive') },
  ], [t]);

  useEffect(() => { load(); }, []);

  const load = () => {
    setLoading(true);
    api.get('/app-users/')
      .then(r => setUsers(r.data))
      .catch(() => setError(t('common.error')))
      .finally(() => setLoading(false));
  };

  const openCreate = () => {
    setEditItem(null);
    setForm(emptyForm());
    setFormError('');
    setShowDialog(true);
  };

  const openEdit = (u: AppUser) => {
    setEditItem(u);
    setForm({
      login: u.login,
      password: '',
      email: u.email || '',
      first_name: u.first_name || '',
      last_name: u.last_name || '',
      phone: u.phone || '',
      role: u.role,
      is_active: u.is_active ? 'true' : 'false',
    });
    setFormError('');
    setShowDialog(true);
  };

  const closeDialog = () => { setShowDialog(false); setEditItem(null); };

  const handleSave = async () => {
    setSaving(true); setFormError('');
    try {
      if (editItem) {
        // Build payload — only include password if not empty
        const payload: Record<string, unknown> = {
          login: form.login,
          email: form.email || null,
          first_name: form.first_name || null,
          last_name: form.last_name || null,
          phone: form.phone || null,
          role: form.role,
          is_active: form.is_active === 'true',
        };
        if (form.password) payload.password = form.password;
        const r = await api.patch(`/app-users/${editItem.user_id}`, payload);
        setUsers(prev => prev.map(u => u.user_id === editItem.user_id ? r.data : u));
      } else {
        const payload: Record<string, unknown> = {
          login: form.login,
          password: form.password,
          email: form.email || null,
          first_name: form.first_name || null,
          last_name: form.last_name || null,
          phone: form.phone || null,
          role: form.role,
          is_active: form.is_active === 'true',
        };
        const r = await api.post('/app-users/', payload);
        setUsers(prev => [...prev, r.data]);
      }
      closeDialog();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setFormError(err.response?.data?.message || t('common.error'));
    } finally { setSaving(false); }
  };

  const handleToggleActive = async (u: AppUser) => {
    try {
      const r = await api.patch(`/app-users/${u.user_id}`, { is_active: !u.is_active });
      setUsers(prev => prev.map(x => x.user_id === u.user_id ? r.data : x));
    } catch {
      setError(t('common.error'));
    }
    setConfirmTarget(null);
  };

  const upd = (k: string, v: string) => setForm(prev => ({ ...prev, [k]: v }));

  return (
    <PageContainer>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3" style={{ color: 'var(--text)' }}>
          <Users style={{ color: 'var(--accent)' }} size={28} />
          {t('admin.users_title')}
        </h1>
        <Button onClick={openCreate}><Plus size={16} /> {t('admin.new_user')}</Button>
      </div>

      {error && <p className="mb-4" style={{ color: 'var(--danger)' }}>{error}</p>}
      {loading ? (
        <p style={{ color: 'var(--text-muted)' }}>{t('common.loading')}</p>
      ) : (
        <Card className="p-0 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>{t('admin.col_user')}</TableHead>
                <TableHead>{t('admin.col_name')}</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>{t('admin.col_role')}</TableHead>
                <TableHead>{t('admin.col_active')}</TableHead>
                <TableHead>{t('admin.col_created')}</TableHead>
                <TableHead>{t('admin.col_actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.length === 0 ? (
                <EmptyTableRow colSpan={8} message={t('admin.no_users')} />
              ) : (
                users.map(u => (
                  <TableRow key={u.user_id}>
                    <TableCell style={{ color: 'var(--text-muted)' }}>{u.user_id}</TableCell>
                    <TableCell className="font-medium" style={{ color: 'var(--text)' }}>{u.login}</TableCell>
                    <TableCell style={{ color: 'var(--text-muted)' }}>
                      {[u.first_name, u.last_name].filter(Boolean).join(' ') || '—'}
                    </TableCell>
                    <TableCell style={{ color: 'var(--text-muted)' }}>{u.email || '—'}</TableCell>
                    <TableCell>
                      <Badge variant={u.role === 'admin' ? 'accent' : 'muted'}>{u.role}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={u.is_active ? 'success' : 'danger'}>
                        {u.is_active ? t('admin.active') : t('admin.inactive')}
                      </Badge>
                    </TableCell>
                    <TableCell style={{ color: 'var(--text-muted)' }}>{u.created_at}</TableCell>
                    <TableCell>
                      <div className="flex gap-2 flex-wrap">
                        <Button size="sm" variant="outline" onClick={() => openEdit(u)}>
                          {t('common.edit')}
                        </Button>
                        {u.is_active ? (
                          <Button size="sm" variant="danger" onClick={() => setConfirmTarget({ user: u, action: 'deactivate' })}>
                            {t('admin.deactivate')}
                          </Button>
                        ) : (
                          <Button size="sm" variant="outline" onClick={() => setConfirmTarget({ user: u, action: 'activate' })}>
                            {t('admin.activate')}
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </Card>
      )}

      {/* Create / Edit Dialog */}
      <Dialog open={showDialog} onClose={closeDialog} size="lg">
        <DialogHeader title={editItem ? t('admin.edit_user') : t('admin.new_user')} onClose={closeDialog} />
        <DialogContent>
          {formError && <p className="mb-4 text-sm" style={{ color: 'var(--danger)' }}>{formError}</p>}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label={`${t('admin.field_login')} *`}
              value={form.login}
              onChange={e => upd('login', e.target.value)}
              required
              autoFocus={!editItem}
            />
            <Input
              label={editItem
                ? `${t('admin.field_password')} ${t('admin.field_password_hint')}`
                : `${t('admin.field_password')} *`}
              type="password"
              value={form.password}
              onChange={e => upd('password', e.target.value)}
              required={!editItem}
              autoComplete="new-password"
            />
            <Input
              label={t('admin.field_first_name')}
              value={form.first_name}
              onChange={e => upd('first_name', e.target.value)}
            />
            <Input
              label={t('admin.field_last_name')}
              value={form.last_name}
              onChange={e => upd('last_name', e.target.value)}
            />
            <Input
              label={t('admin.field_email')}
              type="email"
              value={form.email}
              onChange={e => upd('email', e.target.value)}
            />
            <Input
              label={t('admin.field_phone')}
              type="tel"
              value={form.phone}
              onChange={e => upd('phone', e.target.value)}
            />
            <Select
              label={t('admin.field_role')}
              value={form.role}
              onChange={e => upd('role', e.target.value)}
              options={ROLE_OPTIONS}
            />
            <Select
              label={t('admin.field_is_active')}
              value={form.is_active}
              onChange={e => upd('is_active', e.target.value)}
              options={ACTIVE_OPTIONS}
            />
          </div>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={closeDialog}>{t('common.cancel')}</Button>
          <Button loading={saving} onClick={handleSave}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      {/* Deactivate / Activate Confirm Dialog */}
      <Dialog open={confirmTarget !== null} onClose={() => setConfirmTarget(null)} size="sm">
        <DialogHeader
          title={confirmTarget?.action === 'deactivate' ? t('admin.deactivate') : t('admin.activate')}
          onClose={() => setConfirmTarget(null)}
        />
        <DialogContent>
          <p style={{ color: 'var(--text)' }}>
            {confirmTarget?.action === 'deactivate'
              ? t('admin.deactivate_confirm')
              : t('admin.activate_confirm')}
          </p>
          {confirmTarget && (
            <p className="mt-2 text-sm font-medium" style={{ color: 'var(--accent)' }}>
              {confirmTarget.user.login}
            </p>
          )}
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setConfirmTarget(null)}>{t('common.cancel')}</Button>
          <Button
            variant={confirmTarget?.action === 'deactivate' ? 'danger' : 'primary'}
            onClick={() => confirmTarget && handleToggleActive(confirmTarget.user)}
          >
            {confirmTarget?.action === 'deactivate' ? t('admin.deactivate') : t('admin.activate')}
          </Button>
        </DialogFooter>
      </Dialog>
    </PageContainer>
  );
}
