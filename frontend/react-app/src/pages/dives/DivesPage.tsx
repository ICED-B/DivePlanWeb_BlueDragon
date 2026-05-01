import { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Waves, Plus, Download, BookOpen } from 'lucide-react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input, Select, Textarea } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, EmptyTableRow } from '../../components/ui/table';
import { Dialog, DialogHeader, DialogContent, DialogFooter } from '../../components/ui/dialog';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';

interface Dive {
  dive_id: number;
  user_id: number;
  start_time: string;
  duration_min: number | null;
  max_depth_m: number | null;
  avg_depth_m: number | null;
  breathing_system: string;
  water_temp_c: number | null;
  air_temp_c: number | null;
  surface_interval_min: number | null;
  ndl_min: number | null;
  cns_max_pct: number | null;
  otu: number | null;
  notes: string | null;
  site_id: number | null;
  trip_id: number | null;
  device_id: number | null;
  license_id: number | null;
}

interface SiteRef   { site_id: number;    name: string; }
interface TripRef   { trip_id: number;    title: string | null; }
interface DeviceRef { device_id: number;  brand: string | null; model: string | null; }
interface LicenseRef { license_id: number; agency: string | null; certification: string | null; }

const BREATHING_BADGE: Record<string, string> = {
  open_circuit: 'OC', closed_circuit: 'CCR', semi_closed: 'SCR', apnea: 'Apnoe',
};

const emptyForm = () => ({
  start_date: new Date().toISOString().slice(0, 10),
  start_time: new Date().toTimeString().slice(0, 5),
  duration_min: '',
  max_depth_m: '',
  avg_depth_m: '',
  breathing_system: 'open_circuit',
  water_temp_c: '',
  air_temp_c: '',
  surface_interval_min: '',
  ndl_min: '',
  cns_max_pct: '',
  otu: '',
  notes: '',
  site_id: '',
  trip_id: '',
  device_id: '',
  license_id: '',
});

export default function DivesPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const BREATHING_OPTIONS = useMemo(() => [
    { value: 'open_circuit', label: t('dives.breathing_open') },
    { value: 'closed_circuit', label: t('dives.breathing_closed') },
    { value: 'semi_closed', label: t('dives.breathing_semi') },
    { value: 'apnea', label: t('dives.breathing_apnea') },
  ], [t]);

  const [allSites, setAllSites] = useState<SiteRef[]>([]);
  const [allTrips, setAllTrips] = useState<TripRef[]>([]);
  const [allDevices, setAllDevices] = useState<DeviceRef[]>([]);
  const [allLicenses, setAllLicenses] = useState<LicenseRef[]>([]);

  const [dives, setDives] = useState<Dive[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [editItem, setEditItem] = useState<Dive | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyForm());
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const PAGE_SIZE = 20;

  useEffect(() => {
    api.get('/sites/').then(r => setAllSites(r.data)).catch(() => {});
    api.get('/trips/').then(r => setAllTrips(r.data)).catch(() => {});
    api.get('/devices/').then(r => setAllDevices(r.data)).catch(() => {});
    api.get('/licenses/').then(r => setAllLicenses(r.data)).catch(() => {});
  }, []);

  useEffect(() => { load(page); }, [page]);

  const load = (p = 1) => {
    setLoading(true);
    api.get(`/dives/?page=${p}&page_size=${PAGE_SIZE}`)
      .then(r => {
        setDives(r.data);
        const total = parseInt(r.headers['x-total-count'] || '0', 10);
        setTotalCount(total);
      })
      .catch(() => setError(t('dives.error')))
      .finally(() => setLoading(false));
  };

  const openCreate = () => {
    setEditItem(null); setForm(emptyForm()); setFormError(''); setShowDialog(true);
  };

  const openEdit = (dive: Dive) => {
    setEditItem(dive);
    setForm({
      start_date: dive.start_time ? dive.start_time.slice(0, 10) : new Date().toISOString().slice(0, 10),
      start_time: dive.start_time ? dive.start_time.slice(11, 16) : new Date().toTimeString().slice(0, 5),
      duration_min: dive.duration_min?.toString() || '',
      max_depth_m: dive.max_depth_m?.toString() || '',
      avg_depth_m: dive.avg_depth_m?.toString() || '',
      breathing_system: dive.breathing_system,
      water_temp_c: dive.water_temp_c?.toString() || '',
      air_temp_c: dive.air_temp_c?.toString() || '',
      surface_interval_min: dive.surface_interval_min?.toString() || '',
      ndl_min: dive.ndl_min?.toString() || '',
      cns_max_pct: dive.cns_max_pct?.toString() || '',
      otu: dive.otu?.toString() || '',
      notes: dive.notes || '',
      site_id: dive.site_id?.toString() || '',
      trip_id: dive.trip_id?.toString() || '',
      device_id: dive.device_id?.toString() || '',
      license_id: dive.license_id?.toString() || '',
    });
    setFormError(''); setShowDialog(true);
  };

  const closeDialog = () => { setShowDialog(false); setEditItem(null); };

  const buildPayload = () => ({
    start_time: `${form.start_date}T${form.start_time}:00`,
    breathing_system: form.breathing_system,
    duration_min: form.duration_min ? +form.duration_min : null,
    max_depth_m: form.max_depth_m ? +form.max_depth_m : null,
    avg_depth_m: form.avg_depth_m ? +form.avg_depth_m : null,
    water_temp_c: form.water_temp_c ? +form.water_temp_c : null,
    air_temp_c: form.air_temp_c ? +form.air_temp_c : null,
    surface_interval_min: form.surface_interval_min ? +form.surface_interval_min : null,
    ndl_min: form.ndl_min ? +form.ndl_min : null,
    cns_max_pct: form.cns_max_pct ? +form.cns_max_pct : null,
    otu: form.otu ? +form.otu : null,
    notes: form.notes || null,
    site_id: form.site_id ? +form.site_id : null,
    trip_id: form.trip_id ? +form.trip_id : null,
    device_id: form.device_id ? +form.device_id : null,
    license_id: form.license_id ? +form.license_id : null,
  });

  const handleSave = async () => {
    setSaving(true); setFormError('');
    try {
      if (editItem) {
        const r = await api.patch(`/dives/${editItem.dive_id}`, buildPayload());
        setDives(prev => prev.map(d => d.dive_id === editItem.dive_id ? r.data : d));
      } else {
        const r = await api.post('/dives/', buildPayload());
        setDives(prev => [r.data, ...prev]);
        setTotalCount(c => c + 1);
      }
      closeDialog();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setFormError(err.response?.data?.message || t('common.error'));
    } finally { setSaving(false); }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/dives/${id}`);
      setDives(prev => prev.filter(d => d.dive_id !== id));
      setTotalCount(c => c - 1);
    } catch { setError(t('common.error')); }
    setDeleteId(null);
  };

  const handleExportUDDF = async (id: number) => {
    try {
      const r = await api.get(`/dives/${id}/export/uddf`, { responseType: 'blob' });
      const url = URL.createObjectURL(new Blob([r.data]));
      const a = document.createElement('a');
      a.href = url; a.download = `dive_${id}.uddf.xml`; a.click();
      URL.revokeObjectURL(url);
    } catch { setError(t('dives.export_error')); }
  };

  const upd = (k: string, v: string) => setForm(prev => ({ ...prev, [k]: v }));

  const NONE_OPT = useMemo(() => [{ value: '', label: t('dives.none_selected') }], [t]);
  const siteOptions = useMemo(() => [
    ...NONE_OPT,
    ...allSites.map(s => ({ value: s.site_id.toString(), label: s.name })),
  ], [NONE_OPT, allSites]);
  const tripOptions = useMemo(() => [
    ...NONE_OPT,
    ...allTrips.map(tr => ({ value: tr.trip_id.toString(), label: tr.title || `#${tr.trip_id}` })),
  ], [NONE_OPT, allTrips]);
  const deviceOptions = useMemo(() => [
    ...NONE_OPT,
    ...allDevices.map(d => ({ value: d.device_id.toString(), label: [d.brand, d.model].filter(Boolean).join(' ') || `#${d.device_id}` })),
  ], [NONE_OPT, allDevices]);
  const licenseOptions = useMemo(() => [
    ...NONE_OPT,
    ...allLicenses.map(l => ({ value: l.license_id.toString(), label: [l.agency, l.certification].filter(Boolean).join(' — ') || `#${l.license_id}` })),
  ], [NONE_OPT, allLicenses]);

  const totalPages = Math.ceil(totalCount / PAGE_SIZE);

  return (
    <PageContainer>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3" style={{ color: 'var(--text)' }}>
            <Waves style={{ color: 'var(--accent)' }} size={28} />
            {t('dives.title')}
          </h1>
          {!loading && <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>{t('dives.total_count', { count: totalCount })}</p>}
        </div>
        <Button onClick={openCreate}><Plus size={16} /> {t('dives.new')}</Button>
      </div>

      {error && <p className="mb-4" style={{ color: 'var(--danger)' }}>{error}</p>}
      {loading ? <p style={{ color: 'var(--text-muted)' }}>{t('dives.loading')}</p> : (
        <>
          <Card className="p-0 overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>#</TableHead>
                  <TableHead>{t('dives.col_date')}</TableHead>
                  <TableHead>{t('dives.col_depth')}</TableHead>
                  <TableHead>{t('dives.col_duration')}</TableHead>
                  <TableHead>{t('dives.col_breathing')}</TableHead>
                  <TableHead>{t('dives.col_temp')}</TableHead>
                  <TableHead>{t('common.actions')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {dives.length === 0 ? (
                  <EmptyTableRow colSpan={7} message={t('dives.no_dives')} />
                ) : dives.map(dive => (
                  <TableRow key={dive.dive_id}>
                    <TableCell style={{ color: 'var(--text-muted)' }}>{dive.dive_id}</TableCell>
                    <TableCell style={{ color: 'var(--text)' }}>{dive.start_time ? new Date(dive.start_time).toLocaleString('cs-CZ', { dateStyle: 'short', timeStyle: 'short' }) : '—'}</TableCell>
                    <TableCell style={{ color: 'var(--text)' }}>
                      {dive.max_depth_m != null ? `${dive.max_depth_m} m` : '—'}
                    </TableCell>
                    <TableCell style={{ color: 'var(--text-muted)' }}>
                      {dive.duration_min != null ? `${dive.duration_min} min` : '—'}
                    </TableCell>
                    <TableCell>
                      <Badge variant="muted">{BREATHING_BADGE[dive.breathing_system] || dive.breathing_system}</Badge>
                    </TableCell>
                    <TableCell style={{ color: 'var(--text-muted)' }}>
                      {dive.water_temp_c != null ? `${dive.water_temp_c} °C` : '—'}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2 flex-wrap">
                        <Button size="sm" variant="outline" onClick={() => openEdit(dive)}>{t('common.edit')}</Button>
                        <Button size="sm" variant="ghost" title={t('dive_detail.title')} onClick={() => navigate(`/dives/detail?id=${dive.dive_id}`)}>
                          <BookOpen size={14} />
                        </Button>
                        <Button size="sm" variant="ghost" onClick={() => handleExportUDDF(dive.dive_id)}>
                          <Download size={14} />
                        </Button>
                        <Button size="sm" variant="danger" onClick={() => setDeleteId(dive.dive_id)}>{t('common.delete')}</Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4">
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                {t('dives.page_of', { page, total: totalPages })}
              </p>
              <div className="flex gap-2">
                <Button size="sm" variant="outline" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>{t('dives.prev')}</Button>
                <Button size="sm" variant="outline" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>{t('dives.next')}</Button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Create / Edit Dialog */}
      <Dialog open={showDialog} onClose={closeDialog} size="lg">
        <DialogHeader title={editItem ? t('dives.edit') : t('dives.new')} onClose={closeDialog} />
        <DialogContent>
          {formError && <p className="mb-4 text-sm" style={{ color: 'var(--danger)' }}>{formError}</p>}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label={`${t('dives.field_start_date')} *`}
              type="date"
              value={form.start_date}
              onChange={e => upd('start_date', e.target.value)}
              required
            />
            <Input
              label={`${t('dives.field_start_time')} *`}
              type="time"
              value={form.start_time}
              onChange={e => upd('start_time', e.target.value)}
              required
            />
            <Select
              label={`${t('dives.field_breathing')} *`}
              value={form.breathing_system}
              onChange={e => upd('breathing_system', e.target.value)}
              options={BREATHING_OPTIONS}
            />
            <Input label={t('dives.field_duration')} type="number" value={form.duration_min} onChange={e => upd('duration_min', e.target.value)} min="0" step="1" />
            <Input label={t('dives.field_max_depth')} type="number" value={form.max_depth_m} onChange={e => upd('max_depth_m', e.target.value)} min="0" step="0.5" />
            <Input label={t('dives.field_avg_depth')} type="number" value={form.avg_depth_m} onChange={e => upd('avg_depth_m', e.target.value)} min="0" step="0.5" />
            <Input label={t('dives.field_surface_interval')} type="number" value={form.surface_interval_min} onChange={e => upd('surface_interval_min', e.target.value)} min="0" step="1" />
            <Input label={t('dives.field_water_temp')} type="number" value={form.water_temp_c} onChange={e => upd('water_temp_c', e.target.value)} step="0.5" />
            <Input label={t('dives.field_surface_temp')} type="number" value={form.air_temp_c} onChange={e => upd('air_temp_c', e.target.value)} step="0.5" />
            <Input label={t('dives.field_ndl')} type="number" value={form.ndl_min} onChange={e => upd('ndl_min', e.target.value)} min="0" step="1" />
            <Input label={t('dives.field_cns')} type="number" value={form.cns_max_pct} onChange={e => upd('cns_max_pct', e.target.value)} min="0" max="100" step="0.1" />
            <Input label={t('dives.field_otu')} type="number" value={form.otu} onChange={e => upd('otu', e.target.value)} min="0" step="1" />
          </div>
          <div className="mt-4">
            <Textarea label={t('dives.field_notes')} value={form.notes} onChange={e => upd('notes', e.target.value)} rows={3} />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
            <Select label={t('dives.field_site')} value={form.site_id} onChange={e => upd('site_id', e.target.value)} options={siteOptions} />
            <Select label={t('dives.field_trip')} value={form.trip_id} onChange={e => upd('trip_id', e.target.value)} options={tripOptions} />
            <Select label={t('dives.field_device')} value={form.device_id} onChange={e => upd('device_id', e.target.value)} options={deviceOptions} />
            <Select label={t('dives.field_license')} value={form.license_id} onChange={e => upd('license_id', e.target.value)} options={licenseOptions} />
          </div>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={closeDialog}>{t('common.cancel')}</Button>
          <Button loading={saving} onClick={handleSave}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      {/* Delete confirmation */}
      <Dialog open={deleteId !== null} onClose={() => setDeleteId(null)} size="sm">
        <DialogHeader title={t('dives.delete')} onClose={() => setDeleteId(null)} />
        <DialogContent><p style={{ color: 'var(--text)' }}>{t('dives.delete_confirm')}</p></DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setDeleteId(null)}>{t('common.cancel')}</Button>
          <Button variant="danger" onClick={() => handleDelete(deleteId!)}>{t('common.delete')}</Button>
        </DialogFooter>
      </Dialog>
    </PageContainer>
  );
}
