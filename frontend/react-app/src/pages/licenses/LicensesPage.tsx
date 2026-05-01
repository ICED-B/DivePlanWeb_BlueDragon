import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Award, Plus } from 'lucide-react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input, Textarea } from '../../components/ui/input';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, EmptyTableRow } from '../../components/ui/table';
import { Dialog, DialogHeader, DialogContent, DialogFooter } from '../../components/ui/dialog';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';

interface License {
  license_id: number;
  agency: string | null;
  certification: string | null;
  level: string | null;
  number: string | null;
  issued_on: string | null;
  expires_on: string | null;
  note: string | null;
}

const emptyForm = () => ({
  agency: '', certification: '', level: '', number: '', issued_on: '', expires_on: '', note: '',
});

export default function LicensesPage() {
  const { t } = useTranslation();
  const [items, setItems] = useState<License[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [editItem, setEditItem] = useState<License | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyForm());
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');

  useEffect(() => { load(); }, []);

  const load = () => {
    setLoading(true);
    api.get('/licenses/').then(r => setItems(r.data)).catch(() => setError(t('common.error'))).finally(() => setLoading(false));
  };

  const openCreate = () => { setEditItem(null); setForm(emptyForm()); setFormError(''); setShowDialog(true); };
  const openEdit = (item: License) => {
    setEditItem(item);
    setForm({
      agency: item.agency || '', certification: item.certification || '', level: item.level || '',
      number: item.number || '', issued_on: item.issued_on || '', expires_on: item.expires_on || '',
      note: item.note || '',
    });
    setFormError(''); setShowDialog(true);
  };
  const closeDialog = () => { setShowDialog(false); setEditItem(null); };

  const buildPayload = () => ({
    agency: form.agency || null,
    certification: form.certification || null,
    level: form.level || null,
    number: form.number || null,
    issued_on: form.issued_on || null,
    expires_on: form.expires_on || null,
    note: form.note || null,
  });

  const handleSave = async () => {
    setSaving(true); setFormError('');
    try {
      if (editItem) {
        const r = await api.patch(`/licenses/${editItem.license_id}`, buildPayload());
        setItems(prev => prev.map(i => i.license_id === editItem.license_id ? r.data : i));
      } else {
        const r = await api.post('/licenses/', buildPayload());
        setItems(prev => [...prev, r.data]);
      }
      closeDialog();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setFormError(err.response?.data?.message || t('common.error'));
    } finally { setSaving(false); }
  };

  const handleDelete = async (id: number) => {
    try { await api.delete(`/licenses/${id}`); setItems(prev => prev.filter(i => i.license_id !== id)); }
    catch { setError(t('common.error')); }
    setDeleteId(null);
  };

  const upd = (k: string, v: string) => setForm(prev => ({ ...prev, [k]: v }));

  return (
    <PageContainer>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3" style={{ color: 'var(--text)' }}>
          <Award style={{ color: 'var(--accent)' }} size={28} />
          {t('licenses.title')}
        </h1>
        <Button onClick={openCreate}><Plus size={16} /> {t('licenses.new')}</Button>
      </div>

      {error && <p className="mb-4" style={{ color: 'var(--danger)' }}>{error}</p>}
      {loading ? <p style={{ color: 'var(--text-muted)' }}>{t('common.loading')}</p> : (
        <Card className="p-0 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('licenses.col_agency')}</TableHead>
                <TableHead>{t('licenses.col_cert')}</TableHead>
                <TableHead>{t('licenses.col_level')}</TableHead>
                <TableHead>{t('licenses.col_issued')}</TableHead>
                <TableHead>{t('licenses.col_expires')}</TableHead>
                <TableHead>{t('common.actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.length === 0 ? (
                <EmptyTableRow colSpan={6} message={t('licenses.no_licenses')} />
              ) : items.map(item => (
                <TableRow key={item.license_id}>
                  <TableCell className="font-medium" style={{ color: 'var(--text)' }}>{item.agency || '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text)' }}>{item.certification || '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{item.level || '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{item.issued_on || '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{item.expires_on || '—'}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => openEdit(item)}>{t('common.edit')}</Button>
                      <Button size="sm" variant="danger" onClick={() => setDeleteId(item.license_id)}>{t('common.delete')}</Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}

      <Dialog open={showDialog} onClose={closeDialog} size="md">
        <DialogHeader title={editItem ? t('licenses.edit') : t('licenses.new')} onClose={closeDialog} />
        <DialogContent>
          {formError && <p className="mb-4 text-sm" style={{ color: 'var(--danger)' }}>{formError}</p>}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label={t('licenses.field_agency')} value={form.agency} onChange={e => upd('agency', e.target.value)} />
            <Input label={t('licenses.field_cert')} value={form.certification} onChange={e => upd('certification', e.target.value)} />
            <Input label={t('licenses.field_level')} value={form.level} onChange={e => upd('level', e.target.value)} />
            <Input label={t('licenses.field_number')} value={form.number} onChange={e => upd('number', e.target.value)} />
            <Input label={t('licenses.field_issued')} type="date" value={form.issued_on} onChange={e => upd('issued_on', e.target.value)} />
            <Input label={t('licenses.field_expires')} type="date" value={form.expires_on} onChange={e => upd('expires_on', e.target.value)} />
          </div>
          <div className="mt-4">
            <Textarea label={t('licenses.field_note')} value={form.note} onChange={e => upd('note', e.target.value)} rows={2} />
          </div>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={closeDialog}>{t('common.cancel')}</Button>
          <Button loading={saving} onClick={handleSave}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      <Dialog open={deleteId !== null} onClose={() => setDeleteId(null)} size="sm">
        <DialogHeader title={t('licenses.delete')} onClose={() => setDeleteId(null)} />
        <DialogContent><p style={{ color: 'var(--text)' }}>{t('licenses.delete_confirm')}</p></DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setDeleteId(null)}>{t('common.cancel')}</Button>
          <Button variant="danger" onClick={() => handleDelete(deleteId!)}>{t('common.delete')}</Button>
        </DialogFooter>
      </Dialog>
    </PageContainer>
  );
}
