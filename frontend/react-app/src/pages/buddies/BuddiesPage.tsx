import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { UserCheck, Plus } from 'lucide-react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input, Textarea } from '../../components/ui/input';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, EmptyTableRow } from '../../components/ui/table';
import { Dialog, DialogHeader, DialogContent, DialogFooter } from '../../components/ui/dialog';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';

interface Buddy {
  buddy_id: number;
  name: string;
  email: string | null;
  phone: string | null;
  note: string | null;
}

const emptyForm = () => ({ name: '', email: '', phone: '', note: '' });

export default function BuddiesPage() {
  const { t } = useTranslation();
  const [buddies, setBuddies] = useState<Buddy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [editItem, setEditItem] = useState<Buddy | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyForm());
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');

  useEffect(() => { load(); }, []);

  const load = () => {
    setLoading(true);
    api.get('/buddies/').then(r => setBuddies(r.data)).catch(() => setError(t('common.error'))).finally(() => setLoading(false));
  };

  const openCreate = () => { setEditItem(null); setForm(emptyForm()); setFormError(''); setShowDialog(true); };
  const openEdit = (b: Buddy) => {
    setEditItem(b);
    setForm({ name: b.name, email: b.email || '', phone: b.phone || '', note: b.note || '' });
    setFormError(''); setShowDialog(true);
  };
  const closeDialog = () => { setShowDialog(false); setEditItem(null); };

  const buildPayload = () => ({
    name: form.name,
    email: form.email || null,
    phone: form.phone || null,
    note: form.note || null,
  });

  const handleSave = async () => {
    setSaving(true); setFormError('');
    try {
      if (editItem) {
        const r = await api.patch(`/buddies/${editItem.buddy_id}`, buildPayload());
        setBuddies(prev => prev.map(b => b.buddy_id === editItem.buddy_id ? r.data : b));
      } else {
        const r = await api.post('/buddies/', buildPayload());
        setBuddies(prev => [...prev, r.data]);
      }
      closeDialog();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setFormError(err.response?.data?.message || t('common.error'));
    } finally { setSaving(false); }
  };

  const handleDelete = async (id: number) => {
    try { await api.delete(`/buddies/${id}`); setBuddies(prev => prev.filter(b => b.buddy_id !== id)); }
    catch { setError(t('common.error')); }
    setDeleteId(null);
  };

  const upd = (k: string, v: string) => setForm(prev => ({ ...prev, [k]: v }));

  return (
    <PageContainer>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3" style={{ color: 'var(--text)' }}>
          <UserCheck style={{ color: 'var(--accent)' }} size={28} />
          {t('nav.buddies')}
        </h1>
        <Button onClick={openCreate}><Plus size={16} /> {t('buddies.new')}</Button>
      </div>

      {error && <p className="mb-4" style={{ color: 'var(--danger)' }}>{error}</p>}
      {loading ? <p style={{ color: 'var(--text-muted)' }}>{t('common.loading')}</p> : (
        <Card className="p-0 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('buddies.col_name')}</TableHead>
                <TableHead>{t('buddies.col_email')}</TableHead>
                <TableHead>{t('buddies.col_phone')}</TableHead>
                <TableHead>{t('common.actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {buddies.length === 0 ? (
                <EmptyTableRow colSpan={4} message={t('buddies.no_buddies')} />
              ) : buddies.map(b => (
                <TableRow key={b.buddy_id}>
                  <TableCell className="font-medium" style={{ color: 'var(--text)' }}>{b.name}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{b.email || '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{b.phone || '—'}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => openEdit(b)}>{t('common.edit')}</Button>
                      <Button size="sm" variant="danger" onClick={() => setDeleteId(b.buddy_id)}>{t('common.delete')}</Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}

      <Dialog open={showDialog} onClose={closeDialog} size="md">
        <DialogHeader title={editItem ? t('buddies.edit') : t('buddies.new')} onClose={closeDialog} />
        <DialogContent>
          {formError && <p className="mb-4 text-sm" style={{ color: 'var(--danger)' }}>{formError}</p>}
          <div className="flex flex-col gap-4">
            <Input label={t('buddies.field_name')} value={form.name} onChange={e => upd('name', e.target.value)} required />
            <Input label={t('buddies.field_email')} type="email" value={form.email} onChange={e => upd('email', e.target.value)} />
            <Input label={t('buddies.field_phone')} type="tel" value={form.phone} onChange={e => upd('phone', e.target.value)} />
            <Textarea label={t('buddies.field_note')} value={form.note} onChange={e => upd('note', e.target.value)} rows={2} />
          </div>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={closeDialog}>{t('common.cancel')}</Button>
          <Button loading={saving} onClick={handleSave}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      <Dialog open={deleteId !== null} onClose={() => setDeleteId(null)} size="sm">
        <DialogHeader title={t('buddies.delete')} onClose={() => setDeleteId(null)} />
        <DialogContent><p style={{ color: 'var(--text)' }}>{t('buddies.delete_confirm')}</p></DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setDeleteId(null)}>{t('common.cancel')}</Button>
          <Button variant="danger" onClick={() => handleDelete(deleteId!)}>{t('common.delete')}</Button>
        </DialogFooter>
      </Dialog>
    </PageContainer>
  );
}
