import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { MapPin, Plus } from 'lucide-react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input, Textarea } from '../../components/ui/input';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, EmptyTableRow } from '../../components/ui/table';
import { Dialog, DialogHeader, DialogContent, DialogFooter } from '../../components/ui/dialog';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';

interface Site {
  site_id: number;
  name: string;
  country: string | null;
  region: string | null;
  body_of_water: string | null;
  type: string | null;
  latitude: number | null;
  longitude: number | null;
  altitude_m: number | null;
  description: string | null;
}

const emptyForm = () => ({
  name: '', country: '', region: '', body_of_water: '', type: '',
  latitude: '' as string | number, longitude: '' as string | number, altitude_m: '' as string | number,
  description: '',
});

export default function SitesPage() {
  const { t } = useTranslation();
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [editItem, setEditItem] = useState<Site | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyForm());
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');

  useEffect(() => { load(); }, []);

  const load = () => {
    setLoading(true);
    api.get('/sites/').then(r => setSites(r.data)).catch(() => setError(t('common.error'))).finally(() => setLoading(false));
  };

  const openCreate = () => { setEditItem(null); setForm(emptyForm()); setFormError(''); setShowDialog(true); };
  const openEdit = (s: Site) => {
    setEditItem(s);
    setForm({
      name: s.name, country: s.country || '', region: s.region || '',
      body_of_water: s.body_of_water || '', type: s.type || '',
      latitude: s.latitude ?? '', longitude: s.longitude ?? '', altitude_m: s.altitude_m ?? '',
      description: s.description || '',
    });
    setFormError(''); setShowDialog(true);
  };
  const closeDialog = () => { setShowDialog(false); setEditItem(null); };

  const buildPayload = () => ({
    name: form.name, country: form.country || null, region: form.region || null,
    body_of_water: form.body_of_water || null, type: form.type || null,
    latitude: form.latitude !== '' ? +form.latitude : null,
    longitude: form.longitude !== '' ? +form.longitude : null,
    altitude_m: form.altitude_m !== '' ? +form.altitude_m : null,
    description: form.description || null,
  });

  const handleSave = async () => {
    setSaving(true); setFormError('');
    try {
      if (editItem) {
        const r = await api.patch(`/sites/${editItem.site_id}`, buildPayload());
        setSites(prev => prev.map(s => s.site_id === editItem.site_id ? r.data : s));
      } else {
        const r = await api.post('/sites/', buildPayload());
        setSites(prev => [...prev, r.data]);
      }
      closeDialog();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setFormError(err.response?.data?.message || t('common.error'));
    } finally { setSaving(false); }
  };

  const handleDelete = async (id: number) => {
    try { await api.delete(`/sites/${id}`); setSites(prev => prev.filter(s => s.site_id !== id)); }
    catch { setError(t('common.error')); }
    setDeleteId(null);
  };

  const upd = (k: string, v: string | number) => setForm(prev => ({ ...prev, [k]: v }));

  return (
    <PageContainer>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3" style={{ color: 'var(--text)' }}>
          <MapPin style={{ color: 'var(--accent)' }} size={28} />
          {t('sites.title')}
        </h1>
        <Button onClick={openCreate}><Plus size={16} /> {t('sites.new')}</Button>
      </div>

      {error && <p className="mb-4" style={{ color: 'var(--danger)' }}>{error}</p>}
      {loading ? <p style={{ color: 'var(--text-muted)' }}>{t('common.loading')}</p> : (
        <Card className="p-0 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('sites.col_name')}</TableHead>
                <TableHead>{t('sites.col_country')}</TableHead>
                <TableHead>{t('sites.col_type')}</TableHead>
                <TableHead>GPS</TableHead>
                <TableHead>{t('common.actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sites.length === 0 ? (
                <EmptyTableRow colSpan={5} message={t('sites.no_sites')} />
              ) : sites.map(s => (
                <TableRow key={s.site_id}>
                  <TableCell className="font-medium" style={{ color: 'var(--text)' }}>{s.name}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{s.country || '—'}{s.region ? `, ${s.region}` : ''}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{s.type || '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>
                    {s.latitude != null && s.longitude != null ? `${s.latitude.toFixed(4)}, ${s.longitude.toFixed(4)}` : '—'}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => openEdit(s)}>{t('common.edit')}</Button>
                      <Button size="sm" variant="danger" onClick={() => setDeleteId(s.site_id)}>{t('common.delete')}</Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}

      <Dialog open={showDialog} onClose={closeDialog} size="lg">
        <DialogHeader title={editItem ? t('sites.edit') : t('sites.new')} onClose={closeDialog} />
        <DialogContent>
          {formError && <p className="mb-4 text-sm" style={{ color: 'var(--danger)' }}>{formError}</p>}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label={t('sites.field_name')} value={form.name} onChange={e => upd('name', e.target.value)} required />
            <Input label={t('sites.field_country')} value={form.country} onChange={e => upd('country', e.target.value)} />
            <Input label={t('sites.field_region')} value={form.region} onChange={e => upd('region', e.target.value)} />
            <Input label={t('sites.field_body_of_water')} value={form.body_of_water} onChange={e => upd('body_of_water', e.target.value)} />
            <Input label={t('sites.field_type')} value={form.type} onChange={e => upd('type', e.target.value)} />
            <Input label={t('sites.field_altitude')} type="number" value={form.altitude_m} onChange={e => upd('altitude_m', e.target.value)} />
            <Input label={t('sites.field_lat')} type="number" value={form.latitude} onChange={e => upd('latitude', e.target.value)} step="0.0001" min="-90" max="90" />
            <Input label={t('sites.field_lng')} type="number" value={form.longitude} onChange={e => upd('longitude', e.target.value)} step="0.0001" min="-180" max="180" />
          </div>
          <div className="mt-4">
            <Textarea label={t('sites.field_notes')} value={form.description} onChange={e => upd('description', e.target.value)} rows={3} />
          </div>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={closeDialog}>{t('common.cancel')}</Button>
          <Button loading={saving} onClick={handleSave}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      <Dialog open={deleteId !== null} onClose={() => setDeleteId(null)} size="sm">
        <DialogHeader title={t('common.delete')} onClose={() => setDeleteId(null)} />
        <DialogContent><p style={{ color: 'var(--text)' }}>{t('sites.delete_confirm')}</p></DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setDeleteId(null)}>{t('common.cancel')}</Button>
          <Button variant="danger" onClick={() => handleDelete(deleteId!)}>{t('common.delete')}</Button>
        </DialogFooter>
      </Dialog>
    </PageContainer>
  );
}
