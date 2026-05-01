import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Cpu, Plus } from 'lucide-react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input, Textarea } from '../../components/ui/input';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, EmptyTableRow } from '../../components/ui/table';
import { Dialog, DialogHeader, DialogContent, DialogFooter } from '../../components/ui/dialog';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';

interface Device {
  device_id: number;
  brand: string | null;
  model: string | null;
  serial_number: string | null;
  firmware: string | null;
  battery_v: number | null;
  notes: string | null;
  hw_model_display: string | null;
  bt_mac: string | null;
}

const emptyForm = () => ({
  brand: '', model: '', serial_number: '', firmware: '',
  battery_v: '', notes: '', hw_model_display: '', bt_mac: '',
});

export default function DevicesPage() {
  const { t } = useTranslation();
  const [items, setItems] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [editItem, setEditItem] = useState<Device | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyForm());
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');

  useEffect(() => { load(); }, []);

  const load = () => {
    setLoading(true);
    api.get('/devices/').then(r => setItems(r.data)).catch(() => setError(t('common.error'))).finally(() => setLoading(false));
  };

  const openCreate = () => { setEditItem(null); setForm(emptyForm()); setFormError(''); setShowDialog(true); };
  const openEdit = (item: Device) => {
    setEditItem(item);
    setForm({
      brand: item.brand || '', model: item.model || '', serial_number: item.serial_number || '',
      firmware: item.firmware || '', battery_v: item.battery_v?.toString() || '',
      notes: item.notes || '', hw_model_display: item.hw_model_display || '', bt_mac: item.bt_mac || '',
    });
    setFormError(''); setShowDialog(true);
  };
  const closeDialog = () => { setShowDialog(false); setEditItem(null); };

  const buildPayload = () => ({
    brand: form.brand || null,
    model: form.model || null,
    serial_number: form.serial_number || null,
    firmware: form.firmware || null,
    battery_v: form.battery_v ? +form.battery_v : null,
    notes: form.notes || null,
    hw_model_display: form.hw_model_display || null,
    bt_mac: form.bt_mac || null,
  });

  const handleSave = async () => {
    setSaving(true); setFormError('');
    try {
      if (editItem) {
        const r = await api.patch(`/devices/${editItem.device_id}`, buildPayload());
        setItems(prev => prev.map(i => i.device_id === editItem.device_id ? r.data : i));
      } else {
        const r = await api.post('/devices/', buildPayload());
        setItems(prev => [...prev, r.data]);
      }
      closeDialog();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setFormError(err.response?.data?.message || t('common.error'));
    } finally { setSaving(false); }
  };

  const handleDelete = async (id: number) => {
    try { await api.delete(`/devices/${id}`); setItems(prev => prev.filter(i => i.device_id !== id)); }
    catch { setError(t('common.error')); }
    setDeleteId(null);
  };

  const upd = (k: string, v: string) => setForm(prev => ({ ...prev, [k]: v }));

  return (
    <PageContainer>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3" style={{ color: 'var(--text)' }}>
          <Cpu style={{ color: 'var(--accent)' }} size={28} />
          {t('devices.title')}
        </h1>
        <Button onClick={openCreate}><Plus size={16} /> {t('devices.new')}</Button>
      </div>

      {error && <p className="mb-4" style={{ color: 'var(--danger)' }}>{error}</p>}
      {loading ? <p style={{ color: 'var(--text-muted)' }}>{t('common.loading')}</p> : (
        <Card className="p-0 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('devices.col_brand')}</TableHead>
                <TableHead>{t('devices.col_model')}</TableHead>
                <TableHead>{t('devices.col_sn')}</TableHead>
                <TableHead>{t('devices.col_firmware')}</TableHead>
                <TableHead>{t('common.actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.length === 0 ? (
                <EmptyTableRow colSpan={5} message={t('devices.no_devices')} />
              ) : items.map(item => (
                <TableRow key={item.device_id}>
                  <TableCell className="font-medium" style={{ color: 'var(--text)' }}>{item.brand || '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text)' }}>{item.model || '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{item.serial_number || '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{item.firmware || '—'}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => openEdit(item)}>{t('common.edit')}</Button>
                      <Button size="sm" variant="danger" onClick={() => setDeleteId(item.device_id)}>{t('common.delete')}</Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}

      <Dialog open={showDialog} onClose={closeDialog} size="lg">
        <DialogHeader title={editItem ? t('devices.edit') : t('devices.new')} onClose={closeDialog} />
        <DialogContent>
          {formError && <p className="mb-4 text-sm" style={{ color: 'var(--danger)' }}>{formError}</p>}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label={t('devices.field_brand')} value={form.brand} onChange={e => upd('brand', e.target.value)} />
            <Input label={t('devices.field_model')} value={form.model} onChange={e => upd('model', e.target.value)} />
            <Input label={t('devices.field_sn')} value={form.serial_number} onChange={e => upd('serial_number', e.target.value)} />
            <Input label={t('devices.field_firmware')} value={form.firmware} onChange={e => upd('firmware', e.target.value)} />
            <Input label={t('devices.field_battery')} type="number" value={form.battery_v} onChange={e => upd('battery_v', e.target.value)} step="0.01" />
            <Input label={t('devices.field_bt_mac')} value={form.bt_mac} onChange={e => upd('bt_mac', e.target.value)} />
            <Input label={t('devices.field_hw_model')} value={form.hw_model_display} onChange={e => upd('hw_model_display', e.target.value)} />
          </div>
          <div className="mt-4">
            <Textarea label={t('devices.field_notes')} value={form.notes} onChange={e => upd('notes', e.target.value)} rows={2} />
          </div>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={closeDialog}>{t('common.cancel')}</Button>
          <Button loading={saving} onClick={handleSave}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      <Dialog open={deleteId !== null} onClose={() => setDeleteId(null)} size="sm">
        <DialogHeader title={t('devices.delete')} onClose={() => setDeleteId(null)} />
        <DialogContent><p style={{ color: 'var(--text)' }}>{t('devices.delete_confirm')}</p></DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setDeleteId(null)}>{t('common.cancel')}</Button>
          <Button variant="danger" onClick={() => handleDelete(deleteId!)}>{t('common.delete')}</Button>
        </DialogFooter>
      </Dialog>
    </PageContainer>
  );
}
