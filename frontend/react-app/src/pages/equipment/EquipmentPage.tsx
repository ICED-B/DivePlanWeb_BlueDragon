import { useEffect, useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Package, Plus } from 'lucide-react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input, Select, Textarea } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, EmptyTableRow } from '../../components/ui/table';
import { Dialog, DialogHeader, DialogContent, DialogFooter } from '../../components/ui/dialog';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';

interface EquipmentItem {
  equipment_id: number;
  category: string;
  brand: string | null;
  model: string | null;
  serial_number: string | null;
  bought_on: string | null;
  price: number | null;
  state: string | null;
  note: string | null;
  volume_l: number | null;
  work_pressure_bar: number | null;
  valve: string | null;
  material: string | null;
}

const STATE_VARIANTS: Record<string, 'success' | 'warning' | 'danger' | 'muted'> = {
  ok: 'success', service: 'warning', damaged: 'danger', retired: 'muted',
};

const emptyForm = () => ({
  category: '', brand: '', model: '', serial_number: '', bought_on: '',
  price: '', state: '', note: '', volume_l: '', work_pressure_bar: '', valve: '', material: '',
});

export default function EquipmentPage() {
  const { t } = useTranslation();
  const [items, setItems] = useState<EquipmentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [editItem, setEditItem] = useState<EquipmentItem | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyForm());
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');

  const STATE_OPTIONS = useMemo(() => [
    { value: '', label: t('equipment.state_none') },
    { value: 'ok', label: t('equipment.state_ok') },
    { value: 'service', label: t('equipment.state_service') },
    { value: 'damaged', label: t('equipment.state_damaged') },
    { value: 'retired', label: t('equipment.state_retired') },
  ], [t]);

  useEffect(() => { load(); }, []);

  const load = () => {
    setLoading(true);
    api.get('/equipment-items/').then(r => setItems(r.data)).catch(() => setError(t('common.error'))).finally(() => setLoading(false));
  };

  const openCreate = () => { setEditItem(null); setForm(emptyForm()); setFormError(''); setShowDialog(true); };
  const openEdit = (item: EquipmentItem) => {
    setEditItem(item);
    setForm({
      category: item.category, brand: item.brand || '', model: item.model || '',
      serial_number: item.serial_number || '', bought_on: item.bought_on || '',
      price: item.price?.toString() || '', state: item.state || '', note: item.note || '',
      volume_l: item.volume_l?.toString() || '', work_pressure_bar: item.work_pressure_bar?.toString() || '',
      valve: item.valve || '', material: item.material || '',
    });
    setFormError(''); setShowDialog(true);
  };
  const closeDialog = () => { setShowDialog(false); setEditItem(null); };

  const buildPayload = () => ({
    category: form.category,
    brand: form.brand || null, model: form.model || null,
    serial_number: form.serial_number || null,
    bought_on: form.bought_on || null,
    price: form.price ? +form.price : null,
    state: form.state || null,
    note: form.note || null,
    volume_l: form.volume_l ? +form.volume_l : null,
    work_pressure_bar: form.work_pressure_bar ? +form.work_pressure_bar : null,
    valve: form.valve || null,
    material: form.material || null,
  });

  const handleSave = async () => {
    setSaving(true); setFormError('');
    try {
      if (editItem) {
        const r = await api.patch(`/equipment-items/${editItem.equipment_id}`, buildPayload());
        setItems(prev => prev.map(i => i.equipment_id === editItem.equipment_id ? r.data : i));
      } else {
        const r = await api.post('/equipment-items/', buildPayload());
        setItems(prev => [...prev, r.data]);
      }
      closeDialog();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setFormError(err.response?.data?.message || t('common.error'));
    } finally { setSaving(false); }
  };

  const handleDelete = async (id: number) => {
    try { await api.delete(`/equipment-items/${id}`); setItems(prev => prev.filter(i => i.equipment_id !== id)); }
    catch { setError(t('common.error')); }
    setDeleteId(null);
  };

  const upd = (k: string, v: string) => setForm(prev => ({ ...prev, [k]: v }));

  return (
    <PageContainer>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3" style={{ color: 'var(--text)' }}>
          <Package style={{ color: 'var(--accent)' }} size={28} />
          {t('equipment.title')}
        </h1>
        <Button onClick={openCreate}><Plus size={16} /> {t('equipment.new_item')}</Button>
      </div>

      {error && <p className="mb-4" style={{ color: 'var(--danger)' }}>{error}</p>}
      {loading ? <p style={{ color: 'var(--text-muted)' }}>{t('common.loading')}</p> : (
        <Card className="p-0 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('equipment.col_category')}</TableHead>
                <TableHead>{t('equipment.col_brand')}</TableHead>
                <TableHead>{t('equipment.col_model')}</TableHead>
                <TableHead>S/N</TableHead>
                <TableHead>{t('equipment.col_state')}</TableHead>
                <TableHead>{t('common.actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.length === 0 ? (
                <EmptyTableRow colSpan={6} message={t('equipment.no_items')} />
              ) : items.map(item => (
                <TableRow key={item.equipment_id}>
                  <TableCell className="font-medium" style={{ color: 'var(--text)' }}>{item.category}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{item.brand || '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{item.model || '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{item.serial_number || '—'}</TableCell>
                  <TableCell>
                    {item.state
                      ? <Badge variant={STATE_VARIANTS[item.state] || 'muted'}>{t(`equipment.state_${item.state}`)}</Badge>
                      : <span style={{ color: 'var(--text-muted)' }}>—</span>
                    }
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => openEdit(item)}>{t('common.edit')}</Button>
                      <Button size="sm" variant="danger" onClick={() => setDeleteId(item.equipment_id)}>{t('common.delete')}</Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}

      <Dialog open={showDialog} onClose={closeDialog} size="lg">
        <DialogHeader title={editItem ? t('equipment.edit_item') : t('equipment.new_item')} onClose={closeDialog} />
        <DialogContent>
          {formError && <p className="mb-4 text-sm" style={{ color: 'var(--danger)' }}>{formError}</p>}
          <div className="grid grid-cols-2 gap-4">
            <Input label={`${t('equipment.field_category')} *`} value={form.category} onChange={e => upd('category', e.target.value)} placeholder="Mask, Fins, BCD..." required />
            <Input label={t('equipment.col_brand')} value={form.brand} onChange={e => upd('brand', e.target.value)} />
            <Input label={t('equipment.field_model')} value={form.model} onChange={e => upd('model', e.target.value)} />
            <Input label={t('equipment.field_serial')} value={form.serial_number} onChange={e => upd('serial_number', e.target.value)} />
            <Input label={t('equipment.field_bought_on')} type="date" value={form.bought_on} onChange={e => upd('bought_on', e.target.value)} />
            <Input label={t('equipment.field_price')} type="number" value={form.price} onChange={e => upd('price', e.target.value)} min="0" step="1" />
            <Select label={t('equipment.field_state')} value={form.state} onChange={e => upd('state', e.target.value)} options={STATE_OPTIONS} />
            <Input label={t('equipment.field_material')} value={form.material} onChange={e => upd('material', e.target.value)} />
            <Input label={t('equipment.field_volume')} type="number" value={form.volume_l} onChange={e => upd('volume_l', e.target.value)} min="0" step="0.5" />
            <Input label={t('equipment.field_work_pressure')} type="number" value={form.work_pressure_bar} onChange={e => upd('work_pressure_bar', e.target.value)} min="0" step="10" />
            <Input label={t('equipment.field_valve')} value={form.valve} onChange={e => upd('valve', e.target.value)} className="col-span-2" />
          </div>
          <div className="mt-4">
            <Textarea label={t('equipment.field_note')} value={form.note} onChange={e => upd('note', e.target.value)} rows={2} />
          </div>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={closeDialog}>{t('common.cancel')}</Button>
          <Button loading={saving} onClick={handleSave}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      <Dialog open={deleteId !== null} onClose={() => setDeleteId(null)} size="sm">
        <DialogHeader title={t('common.delete')} onClose={() => setDeleteId(null)} />
        <DialogContent><p style={{ color: 'var(--text)' }}>{t('equipment.delete_confirm')}</p></DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setDeleteId(null)}>{t('common.cancel')}</Button>
          <Button variant="danger" onClick={() => handleDelete(deleteId!)}>{t('common.delete')}</Button>
        </DialogFooter>
      </Dialog>
    </PageContainer>
  );
}
