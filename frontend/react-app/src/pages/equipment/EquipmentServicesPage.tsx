import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Wrench, Plus } from 'lucide-react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input, Select, Textarea } from '../../components/ui/input';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, EmptyTableRow } from '../../components/ui/table';
import { Dialog, DialogHeader, DialogContent, DialogFooter } from '../../components/ui/dialog';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';

interface EquipRef { equipment_id: number; category: string; brand: string | null; model: string | null; }

interface EquipmentService {
  service_id: number;
  equipment_id: number | null;
  service_type: string | null;
  frequency_months: number | null;
  last_service: string | null;
  next_service: string | null;
  workshop: string | null;
  document_url: string | null;
  note: string | null;
}

const emptyForm = () => ({
  equipment_id: '', service_type: '', frequency_months: '',
  last_service: '', next_service: '', workshop: '', document_url: '', note: '',
});

export default function EquipmentServicesPage() {
  const { t } = useTranslation();
  const [allEquip, setAllEquip] = useState<EquipRef[]>([]);
  const [items, setItems] = useState<EquipmentService[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [editItem, setEditItem] = useState<EquipmentService | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyForm());
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');

  useEffect(() => {
    api.get('/equipment-items/').then(r => setAllEquip(r.data)).catch(() => {});
    load();
  }, []);

  const load = () => {
    setLoading(true);
    api.get('/equipment-services/').then(r => setItems(r.data)).catch(() => setError(t('common.error'))).finally(() => setLoading(false));
  };

  const openCreate = () => { setEditItem(null); setForm(emptyForm()); setFormError(''); setShowDialog(true); };
  const openEdit = (item: EquipmentService) => {
    setEditItem(item);
    setForm({
      equipment_id: item.equipment_id?.toString() || '',
      service_type: item.service_type || '',
      frequency_months: item.frequency_months?.toString() || '',
      last_service: item.last_service || '',
      next_service: item.next_service || '',
      workshop: item.workshop || '',
      document_url: item.document_url || '',
      note: item.note || '',
    });
    setFormError(''); setShowDialog(true);
  };
  const closeDialog = () => { setShowDialog(false); setEditItem(null); };

  const buildPayload = () => ({
    equipment_id: form.equipment_id ? +form.equipment_id : null,
    service_type: form.service_type || null,
    frequency_months: form.frequency_months ? +form.frequency_months : null,
    last_service: form.last_service || null,
    next_service: form.next_service || null,
    workshop: form.workshop || null,
    document_url: form.document_url || null,
    note: form.note || null,
  });

  const handleSave = async () => {
    setSaving(true); setFormError('');
    try {
      if (editItem) {
        const r = await api.patch(`/equipment-services/${editItem.service_id}`, buildPayload());
        setItems(prev => prev.map(i => i.service_id === editItem.service_id ? r.data : i));
      } else {
        const r = await api.post('/equipment-services/', buildPayload());
        setItems(prev => [...prev, r.data]);
      }
      closeDialog();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setFormError(err.response?.data?.message || t('common.error'));
    } finally { setSaving(false); }
  };

  const handleDelete = async (id: number) => {
    try { await api.delete(`/equipment-services/${id}`); setItems(prev => prev.filter(i => i.service_id !== id)); }
    catch { setError(t('common.error')); }
    setDeleteId(null);
  };

  const upd = (k: string, v: string) => setForm(prev => ({ ...prev, [k]: v }));

  return (
    <PageContainer>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3" style={{ color: 'var(--text)' }}>
          <Wrench style={{ color: 'var(--accent)' }} size={28} />
          {t('services.title')}
        </h1>
        <Button onClick={openCreate}><Plus size={16} /> {t('services.new')}</Button>
      </div>

      {error && <p className="mb-4" style={{ color: 'var(--danger)' }}>{error}</p>}
      {loading ? <p style={{ color: 'var(--text-muted)' }}>{t('common.loading')}</p> : (
        <Card className="p-0 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('services.col_equipment')}</TableHead>
                <TableHead>{t('services.col_type')}</TableHead>
                <TableHead>{t('services.col_last')}</TableHead>
                <TableHead>{t('services.col_next')}</TableHead>
                <TableHead>{t('common.actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.length === 0 ? (
                <EmptyTableRow colSpan={5} message={t('services.no_services')} />
              ) : items.map(item => (
                <TableRow key={item.service_id}>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{(() => { const eq = allEquip.find(e => e.equipment_id === item.equipment_id); return eq ? [eq.category, eq.brand, eq.model].filter(Boolean).join(' ') : (item.equipment_id ?? '—'); })()}</TableCell>
                  <TableCell className="font-medium" style={{ color: 'var(--text)' }}>{item.service_type || '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{item.last_service || '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{item.next_service || '—'}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => openEdit(item)}>{t('common.edit')}</Button>
                      <Button size="sm" variant="danger" onClick={() => setDeleteId(item.service_id)}>{t('common.delete')}</Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}

      <Dialog open={showDialog} onClose={closeDialog} size="lg">
        <DialogHeader title={editItem ? t('services.edit') : t('services.new')} onClose={closeDialog} />
        <DialogContent>
          {formError && <p className="mb-4 text-sm" style={{ color: 'var(--danger)' }}>{formError}</p>}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Select
              label={t('services.field_equipment_id')}
              value={form.equipment_id}
              onChange={e => upd('equipment_id', e.target.value)}
              options={[{ value: '', label: '—' }, ...allEquip.map(eq => ({ value: eq.equipment_id.toString(), label: [eq.category, eq.brand, eq.model].filter(Boolean).join(' ') || `#${eq.equipment_id}` }))]}
            />
            <Input label={t('services.field_type')} value={form.service_type} onChange={e => upd('service_type', e.target.value)} />
            <Input label={t('services.field_freq')} type="number" value={form.frequency_months} onChange={e => upd('frequency_months', e.target.value)} min="1" step="1" />
            <Input label={t('services.field_workshop')} value={form.workshop} onChange={e => upd('workshop', e.target.value)} />
            <Input label={t('services.field_last')} type="date" value={form.last_service} onChange={e => upd('last_service', e.target.value)} />
            <Input label={t('services.field_next')} type="date" value={form.next_service} onChange={e => upd('next_service', e.target.value)} />
            <Input label={t('services.field_document_url')} value={form.document_url} onChange={e => upd('document_url', e.target.value)} className="sm:col-span-2" />
          </div>
          <div className="mt-4">
            <Textarea label={t('services.field_note')} value={form.note} onChange={e => upd('note', e.target.value)} rows={2} />
          </div>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={closeDialog}>{t('common.cancel')}</Button>
          <Button loading={saving} onClick={handleSave}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      <Dialog open={deleteId !== null} onClose={() => setDeleteId(null)} size="sm">
        <DialogHeader title={t('services.delete')} onClose={() => setDeleteId(null)} />
        <DialogContent><p style={{ color: 'var(--text)' }}>{t('services.delete_confirm')}</p></DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setDeleteId(null)}>{t('common.cancel')}</Button>
          <Button variant="danger" onClick={() => handleDelete(deleteId!)}>{t('common.delete')}</Button>
        </DialogFooter>
      </Dialog>
    </PageContainer>
  );
}
