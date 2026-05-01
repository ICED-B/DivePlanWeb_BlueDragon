import { useEffect, useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Wind, Plus } from 'lucide-react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input, Select, Textarea } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../../components/ui/tabs';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, EmptyTableRow } from '../../components/ui/table';
import { Dialog, DialogHeader, DialogContent, DialogFooter } from '../../components/ui/dialog';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';

// GAS MIXES

interface GasMix {
  gas_mix_id: number;
  gas_type: string;
  o2_percent: number | null;
  he_percent: number | null;
  name: string | null;
  active: boolean;
}

const emptyMixForm = () => ({ gas_type: 'nitrox', o2_percent: '32', he_percent: '0', name: '', active: 'true' });

function GasMixesTab() {
  const { t } = useTranslation();
  const [mixes, setMixes] = useState<GasMix[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [editItem, setEditItem] = useState<GasMix | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyMixForm());
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');

  const GAS_TYPES = useMemo(() => [
    { value: 'air',    label: t('gas.gas_type_air') },
    { value: 'nitrox', label: t('gas.gas_type_nitrox') },
    { value: 'trimix', label: t('gas.gas_type_trimix') },
    { value: 'heliox', label: t('gas.gas_type_heliox') },
    { value: 'other',  label: t('gas.gas_type_other') },
  ], [t]);

  useEffect(() => { load(); }, []);

  const load = () => {
    setLoading(true);
    api.get('/gases/').then(r => setMixes(r.data)).catch(() => setError(t('common.error'))).finally(() => setLoading(false));
  };

  const openCreate = () => { setEditItem(null); setForm(emptyMixForm()); setFormError(''); setShowDialog(true); };
  const openEdit = (m: GasMix) => {
    setEditItem(m);
    setForm({ gas_type: m.gas_type, o2_percent: m.o2_percent?.toString() || '', he_percent: m.he_percent?.toString() || '0', name: m.name || '', active: m.active.toString() });
    setFormError(''); setShowDialog(true);
  };
  const closeDialog = () => { setShowDialog(false); setEditItem(null); };

  const buildPayload = () => ({
    gas_type: form.gas_type,
    o2_percent: form.o2_percent ? +form.o2_percent : null,
    he_percent: form.he_percent ? +form.he_percent : null,
    name: form.name || null,
    active: form.active === 'true',
  });

  const handleSave = async () => {
    setSaving(true); setFormError('');
    try {
      if (editItem) {
        const r = await api.patch(`/gases/${editItem.gas_mix_id}`, buildPayload());
        setMixes(prev => prev.map(m => m.gas_mix_id === editItem.gas_mix_id ? r.data : m));
      } else {
        const r = await api.post('/gases/', buildPayload());
        setMixes(prev => [...prev, r.data]);
      }
      closeDialog();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setFormError(err.response?.data?.message || t('common.error'));
    } finally { setSaving(false); }
  };

  const handleDelete = async (id: number) => {
    try { await api.delete(`/gases/${id}`); setMixes(prev => prev.filter(m => m.gas_mix_id !== id)); }
    catch { setError(t('common.error')); }
    setDeleteId(null);
  };

  const upd = (k: string, v: string) => setForm(prev => ({ ...prev, [k]: v }));

  return (
    <>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{mixes.length}</p>
        <Button size="sm" onClick={openCreate}><Plus size={14} /> {t('gas.new_mix')}</Button>
      </div>

      {error && <p className="mb-4" style={{ color: 'var(--danger)' }}>{error}</p>}
      {loading ? <p style={{ color: 'var(--text-muted)' }}>{t('common.loading')}</p> : (
        <Card className="p-0 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('gas.col_name')}</TableHead>
                <TableHead>{t('gas.col_type')}</TableHead>
                <TableHead>{t('gas.col_o2')}</TableHead>
                <TableHead>{t('gas.col_he')}</TableHead>
                <TableHead>{t('gas.col_status')}</TableHead>
                <TableHead>{t('common.actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mixes.length === 0 ? (
                <EmptyTableRow colSpan={6} message={t('gas.no_mixes')} />
              ) : mixes.map(m => (
                <TableRow key={m.gas_mix_id}>
                  <TableCell className="font-medium" style={{ color: 'var(--text)' }}>{m.name || '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{m.gas_type}</TableCell>
                  <TableCell style={{ color: 'var(--text)' }}>{m.o2_percent != null ? `${m.o2_percent} %` : '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{m.he_percent != null ? `${m.he_percent} %` : '—'}</TableCell>
                  <TableCell>
                    <Badge variant={m.active ? 'success' : 'muted'}>{m.active ? t('gas.active') : t('gas.inactive')}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => openEdit(m)}>{t('common.edit')}</Button>
                      <Button size="sm" variant="danger" onClick={() => setDeleteId(m.gas_mix_id)}>{t('common.delete')}</Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}

      <Dialog open={showDialog} onClose={closeDialog} size="md">
        <DialogHeader title={editItem ? t('gas.edit_mix') : t('gas.new_mix')} onClose={closeDialog} />
        <DialogContent>
          {formError && <p className="mb-4 text-sm" style={{ color: 'var(--danger)' }}>{formError}</p>}
          <div className="flex flex-col gap-4">
            <Input label={t('gas.field_name')} value={form.name} onChange={e => upd('name', e.target.value)} placeholder="EAN32, Trimix 21/35..." />
            <Select label={t('gas.field_gas_type')} value={form.gas_type} onChange={e => upd('gas_type', e.target.value)} options={GAS_TYPES} />
            <div className="grid grid-cols-2 gap-4">
              <Input label={t('gas.col_o2')} type="number" value={form.o2_percent} onChange={e => upd('o2_percent', e.target.value)} min="0" max="100" step="1" />
              <Input label={t('gas.col_he')} type="number" value={form.he_percent} onChange={e => upd('he_percent', e.target.value)} min="0" max="100" step="1" />
            </div>
            <Select
              label={t('gas.field_status')}
              value={form.active}
              onChange={e => upd('active', e.target.value)}
              options={[{ value: 'true', label: t('gas.active') }, { value: 'false', label: t('gas.inactive') }]}
            />
          </div>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={closeDialog}>{t('common.cancel')}</Button>
          <Button loading={saving} onClick={handleSave}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      <Dialog open={deleteId !== null} onClose={() => setDeleteId(null)} size="sm">
        <DialogHeader title={t('common.delete')} onClose={() => setDeleteId(null)} />
        <DialogContent><p style={{ color: 'var(--text)' }}>{t('gas.delete_mix_confirm')}</p></DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setDeleteId(null)}>{t('common.cancel')}</Button>
          <Button variant="danger" onClick={() => handleDelete(deleteId!)}>{t('common.delete')}</Button>
        </DialogFooter>
      </Dialog>
    </>
  );
}

// TANKS

interface Tank {
  tank_id: number;
  volume_l: number | null;
  work_pressure_bar: number | null;
  material: string | null;
  serial_number: string | null;
  valve: string | null;
  note: string | null;
}

const emptyTankForm = () => ({ volume_l: '', work_pressure_bar: '', material: '', serial_number: '', valve: '', note: '' });

function TanksTab() {
  const { t } = useTranslation();
  const [tanks, setTanks] = useState<Tank[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [editItem, setEditItem] = useState<Tank | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyTankForm());
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');

  useEffect(() => { load(); }, []);

  const load = () => {
    setLoading(true);
    api.get('/tanks/').then(r => setTanks(r.data)).catch(() => setError(t('common.error'))).finally(() => setLoading(false));
  };

  const openCreate = () => { setEditItem(null); setForm(emptyTankForm()); setFormError(''); setShowDialog(true); };
  const openEdit = (tk: Tank) => {
    setEditItem(tk);
    setForm({
      volume_l: tk.volume_l?.toString() || '', work_pressure_bar: tk.work_pressure_bar?.toString() || '',
      material: tk.material || '', serial_number: tk.serial_number || '', valve: tk.valve || '', note: tk.note || '',
    });
    setFormError(''); setShowDialog(true);
  };
  const closeDialog = () => { setShowDialog(false); setEditItem(null); };

  const buildPayload = () => ({
    volume_l: form.volume_l ? +form.volume_l : null,
    work_pressure_bar: form.work_pressure_bar ? +form.work_pressure_bar : null,
    material: form.material || null,
    serial_number: form.serial_number || null,
    valve: form.valve || null,
    note: form.note || null,
  });

  const handleSave = async () => {
    setSaving(true); setFormError('');
    try {
      if (editItem) {
        const r = await api.patch(`/tanks/${editItem.tank_id}`, buildPayload());
        setTanks(prev => prev.map(tk => tk.tank_id === editItem.tank_id ? r.data : tk));
      } else {
        const r = await api.post('/tanks/', buildPayload());
        setTanks(prev => [...prev, r.data]);
      }
      closeDialog();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setFormError(err.response?.data?.message || t('common.error'));
    } finally { setSaving(false); }
  };

  const handleDelete = async (id: number) => {
    try { await api.delete(`/tanks/${id}`); setTanks(prev => prev.filter(tk => tk.tank_id !== id)); }
    catch { setError(t('common.error')); }
    setDeleteId(null);
  };

  const upd = (k: string, v: string) => setForm(prev => ({ ...prev, [k]: v }));

  return (
    <>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{tanks.length}</p>
        <Button size="sm" onClick={openCreate}><Plus size={14} /> {t('gas.new_tank')}</Button>
      </div>

      {error && <p className="mb-4" style={{ color: 'var(--danger)' }}>{error}</p>}
      {loading ? <p style={{ color: 'var(--text-muted)' }}>{t('common.loading')}</p> : (
        <Card className="p-0 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('gas.col_size')}</TableHead>
                <TableHead>{t('gas.col_pressure')}</TableHead>
                <TableHead>{t('gas.col_material')}</TableHead>
                <TableHead>S/N</TableHead>
                <TableHead>{t('common.actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tanks.length === 0 ? (
                <EmptyTableRow colSpan={5} message={t('gas.no_tanks')} />
              ) : tanks.map(tk => (
                <TableRow key={tk.tank_id}>
                  <TableCell style={{ color: 'var(--text)' }}>{tk.volume_l != null ? `${tk.volume_l} l` : '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{tk.work_pressure_bar != null ? `${tk.work_pressure_bar} bar` : '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{tk.material || '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{tk.serial_number || '—'}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => openEdit(tk)}>{t('common.edit')}</Button>
                      <Button size="sm" variant="danger" onClick={() => setDeleteId(tk.tank_id)}>{t('common.delete')}</Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}

      <Dialog open={showDialog} onClose={closeDialog} size="md">
        <DialogHeader title={editItem ? t('gas.edit_tank') : t('gas.new_tank')} onClose={closeDialog} />
        <DialogContent>
          {formError && <p className="mb-4 text-sm" style={{ color: 'var(--danger)' }}>{formError}</p>}
          <div className="grid grid-cols-2 gap-4">
            <Input label={t('gas.field_volume')} type="number" value={form.volume_l} onChange={e => upd('volume_l', e.target.value)} min="0" step="0.5" />
            <Input label={t('gas.field_work_pressure')} type="number" value={form.work_pressure_bar} onChange={e => upd('work_pressure_bar', e.target.value)} min="0" step="10" />
            <Input label={t('gas.field_material')} value={form.material} onChange={e => upd('material', e.target.value)} placeholder="Steel, Alu..." />
            <Input label={t('gas.field_valve')} value={form.valve} onChange={e => upd('valve', e.target.value)} placeholder="DIN, INT..." />
            <Input label={t('gas.field_serial')} value={form.serial_number} onChange={e => upd('serial_number', e.target.value)} className="col-span-2" />
          </div>
          <div className="mt-4">
            <Textarea label={t('gas.field_note')} value={form.note} onChange={e => upd('note', e.target.value)} rows={2} />
          </div>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={closeDialog}>{t('common.cancel')}</Button>
          <Button loading={saving} onClick={handleSave}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      <Dialog open={deleteId !== null} onClose={() => setDeleteId(null)} size="sm">
        <DialogHeader title={t('common.delete')} onClose={() => setDeleteId(null)} />
        <DialogContent><p style={{ color: 'var(--text)' }}>{t('gas.delete_tank_confirm')}</p></DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setDeleteId(null)}>{t('common.cancel')}</Button>
          <Button variant="danger" onClick={() => handleDelete(deleteId!)}>{t('common.delete')}</Button>
        </DialogFooter>
      </Dialog>
    </>
  );
}

// MAIN GAS PAGE

export default function GasPage() {
  const { t } = useTranslation();
  const [tab, setTab] = useState('mixes');

  return (
    <PageContainer>
      <h1 className="text-3xl font-bold flex items-center gap-3 mb-8" style={{ color: 'var(--text)' }}>
        <Wind style={{ color: 'var(--accent)' }} size={28} />
        {t('gas.title')}
      </h1>

      <Tabs value={tab} onValueChange={setTab}>
        <TabsList>
          <TabsTrigger value="mixes">{t('gas.mixes_title')}</TabsTrigger>
          <TabsTrigger value="tanks">{t('gas.tanks_title')}</TabsTrigger>
        </TabsList>
        <TabsContent value="mixes" className="mt-6">
          <GasMixesTab />
        </TabsContent>
        <TabsContent value="tanks" className="mt-6">
          <TanksTab />
        </TabsContent>
      </Tabs>
    </PageContainer>
  );
}
