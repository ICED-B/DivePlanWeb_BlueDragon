import { useEffect, useState, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { BookOpen, Plus, Trash2 } from 'lucide-react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input, Select, Textarea } from '../../components/ui/input';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, EmptyTableRow } from '../../components/ui/table';
import { Dialog, DialogHeader, DialogContent, DialogFooter } from '../../components/ui/dialog';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';

// TYPES

interface DiveListItem {
  dive_id: number;
  start_time: string;
  max_depth_m: number | null;
  duration_min: number | null;
}

interface DiveDetail {
  dive_id: number;
  start_time: string;
  duration_min: number | null;
  max_depth_m: number | null;
  avg_depth_m: number | null;
  breathing_system: string | null;
  water_temp_c: number | null;
  air_temp_c: number | null;
  surface_interval_min: number | null;
  ndl_min: number | null;
  cns_max_pct: number | null;
  otu: number | null;
  notes: string | null;
  algorithm: string | null;
  deco_model: string | null;
  gf_low: number | null;
  gf_high: number | null;
  site_id: number | null;
  trip_id: number | null;
  device_id: number | null;
  license_id: number | null;
  tanks: DiveTank[];
  segments: DiveSegment[];
  samples: Sample[];
  events: DiveEvent[];
}

interface DiveTank {
  dive_tank_id: number;
  tank_id: number | null;
  gas_mix_id: number | null;
  start_pressure_bar: number | null;
  end_pressure_bar: number | null;
  position: string | null;
}

interface DiveSegment {
  dive_segment_id: number;
  start_t_min: number | null;
  end_t_min: number | null;
  gas_mix_id: number | null;
  setpoint_ppO2: number | null;
  note: string | null;
}

interface Sample {
  t_min: number;
  depth_m: number;
  temp_c: number | null;
  ndl_min: number | null;
  ppO2: number | null;
}

interface DiveEvent {
  dive_event_id: number;
  t_min: number | null;
  type: string | null;
  depth_m: number | null;
}

interface DiveBuddy {
  dive_buddy_id: number;
  buddy_id: number;
  confirmed: boolean;
}

interface DiveTag {
  dive_tag_id: number;
  tag_id: number;
}

interface MediaItem {
  media_id: number;
  kind: string | null;
  uri: string | null;
  caption: string | null;
}

interface DiveEquip {
  dive_equipment_id: number;
  equipment_id: number;
}

interface BuddyRef  { buddy_id: number; name: string; }
interface TagRef    { tag_id: number;   name: string; }
interface TankRef   { tank_id: number; volume_l: number | null; work_pressure_bar: number | null; material: string | null; serial_number: string | null; }
interface GasMixRef { gas_mix_id: number; name: string | null; gas_type: string; o2_percent: number | null; }
interface EquipRef { equipment_id: number; category: string; brand: string | null; model: string | null; }
interface SiteRef    { site_id: number; name: string; country: string | null; region: string | null; body_of_water: string | null; type: string | null; latitude: number | null; longitude: number | null; altitude_m: number | null; description: string | null; }
interface TripRef    { trip_id: number; title: string | null; start_date: string | null; end_date: string | null; notes: string | null; }
interface DeviceRef  { device_id: number; brand: string | null; model: string | null; serial_number: string | null; firmware: string | null; battery_v: number | null; notes: string | null; bt_mac: string | null; hw_model_display: string | null; }
interface LicenseRef { license_id: number; agency: string | null; certification: string | null; level: string | null; number: string | null; issued_on: string | null; expires_on: string | null; note: string | null; }

// PROFILE CHARTS

function ProfileChart({ samples }: { samples: Sample[] }) {
  if (samples.length === 0) return null;
  const maxDepth = Math.max(...samples.map(s => s.depth_m), 1);
  const maxTime  = Math.max(...samples.map(s => s.t_min), 1);
  const W = 320, H = 140;
  const PL = 36, PR = 8, PT = 8, PB = 20;
  const cW = W - PL - PR, cH = H - PT - PB;
  const toX = (t: number) => PL + (t / maxTime) * cW;
  const toY = (d: number) => PT + (d / maxDepth) * cH;
  const pts = samples.map(s => `${toX(s.t_min).toFixed(1)},${toY(s.depth_m).toFixed(1)}`).join(' ');
  const area = `${toX(0).toFixed(1)},${PT} ${pts} ${toX(maxTime).toFixed(1)},${PT}`;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full max-w-xl" style={{ display: 'block' }}>
      {/* depth grid */}
      {[0.25, 0.5, 0.75, 1].map(f => {
        const y = toY(maxDepth * f);
        return (
          <g key={f}>
            <line x1={PL} y1={y} x2={W - PR} y2={y} stroke="var(--border)" strokeWidth={0.5} strokeDasharray="3,3" />
            <text x={PL - 2} y={y + 3} textAnchor="end" fontSize={7} fill="var(--text-muted)">{(maxDepth * f).toFixed(0)}</text>
          </g>
        );
      })}
      {/* time ticks */}
      {[0.25, 0.5, 0.75, 1].map(f => {
        const x = toX(maxTime * f);
        return (
          <text key={f} x={x} y={H - 4} textAnchor="middle" fontSize={7} fill="var(--text-muted)">{(maxTime * f).toFixed(0)}</text>
        );
      })}
      {/* area fill */}
      <polygon points={area} fill="var(--accent)" opacity={0.15} />
      {/* line */}
      <polyline points={pts} fill="none" stroke="var(--accent)" strokeWidth={1.5} strokeLinejoin="round" />
    </svg>
  );
}

// HELPERS

function InfoRow({ label, value }: { label: string; value: string | number | null | undefined }) {
  return (
    <div>
      <p className="text-xs mb-0.5" style={{ color: 'var(--text-subtle)' }}>{label}</p>
      <p className="text-sm font-medium" style={{ color: 'var(--text)' }}>{value ?? '—'}</p>
    </div>
  );
}

// PAGE

export default function DiveDetailPage() {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();

  // dive selector
  const [dives, setDives] = useState<DiveListItem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<DiveDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [activeTab, setActiveTab] = useState('info');

  // sub-resource lists (separate endpoints)
  const [buddies, setBuddies] = useState<DiveBuddy[]>([]);
  const [tags, setTags] = useState<DiveTag[]>([]);
  const [media, setMedia] = useState<MediaItem[]>([]);
  const [equipment, setEquipment] = useState<DiveEquip[]>([]);

  // reference lists for selectors
  const [allBuddies, setAllBuddies] = useState<BuddyRef[]>([]);
  const [allTags, setAllTags] = useState<TagRef[]>([]);
  const [allEquip, setAllEquip] = useState<EquipRef[]>([]);
  const [allSites, setAllSites] = useState<SiteRef[]>([]);
  const [allTrips, setAllTrips] = useState<TripRef[]>([]);
  const [allDevices, setAllDevices] = useState<DeviceRef[]>([]);
  const [allLicenses, setAllLicenses] = useState<LicenseRef[]>([]);
  const [allTanks, setAllTanks] = useState<TankRef[]>([]);
  const [allGasMixes, setAllGasMixes] = useState<GasMixRef[]>([]);

  // top bar (TRIP / SITE / LICENSE / DEVICE)
  const [activeTopTab, setActiveTopTab] = useState<'trip' | 'site' | 'license' | 'device'>('trip');

  // dialog states per tab
  const [tankDlg, setTankDlg] = useState({ open: false, edit: null as DiveTank | null, saving: false, err: '',
    form: { tank_id: '', gas_mix_id: '', start_pressure_bar: '', end_pressure_bar: '', position: '' } });
  const [segDlg, setSegDlg] = useState({ open: false, edit: null as DiveSegment | null, saving: false, err: '',
    form: { start_t_min: '', end_t_min: '', gas_mix_id: '', setpoint_ppO2: '', note: '' } });
  const [eventDlg, setEventDlg] = useState({ open: false, edit: null as DiveEvent | null, saving: false, err: '',
    form: { t_min: '', type: '', depth_m: '' } });
  const [buddyDlg, setBuddyDlg] = useState({ open: false, edit: null as DiveBuddy | null, saving: false, err: '',
    form: { buddy_id: '', confirmed: 'false' } });
  const [tagDlg, setTagDlg] = useState({ open: false, saving: false, err: '',
    form: { tag_id: '' } });
  const [mediaDlg, setMediaDlg] = useState({ open: false, edit: null as MediaItem | null, saving: false, err: '',
    form: { kind: '', uri: '', caption: '' } });
  const [equipDlg, setEquipDlg] = useState({ open: false, saving: false, err: '',
    form: { equipment_id: '' } });
  const [deleteTarget, setDeleteTarget] = useState<{ endpoint: string; id: number; onDone: () => void } | null>(null);

  // load dives list + reference data on mount
  useEffect(() => {
    api.get('/dives/?page_size=500').then(r => setDives(r.data)).catch(() => {});
    api.get('/buddies/').then(r => setAllBuddies(r.data)).catch(() => {});
    api.get('/tags/').then(r => setAllTags(r.data)).catch(() => {});
    api.get('/equipment-items/').then(r => setAllEquip(r.data)).catch(() => {});
    api.get('/sites/').then(r => setAllSites(r.data)).catch(() => {});
    api.get('/trips/').then(r => setAllTrips(r.data)).catch(() => {});
    api.get('/devices/').then(r => setAllDevices(r.data)).catch(() => {});
    api.get('/licenses/').then(r => setAllLicenses(r.data)).catch(() => {});
    api.get('/tanks/').then(r => setAllTanks(r.data)).catch(() => {});
    api.get('/gases/').then(r => setAllGasMixes(r.data)).catch(() => {});
  }, []);

  // pre-select from URL param
  useEffect(() => {
    const id = searchParams.get('id');
    if (id) setSelectedId(+id);
  }, [searchParams]);

  // load detail when dive selected
  useEffect(() => {
    if (!selectedId) { setDetail(null); return; }
    setLoadingDetail(true);
    Promise.all([
      api.get(`/dives/${selectedId}/detail`),
      api.get(`/dive-buddies/?dive_id=${selectedId}`),
      api.get(`/dive-tags/?dive_id=${selectedId}`),
      api.get(`/media/?dive_id=${selectedId}`),
      api.get(`/dive-equipment/?dive_id=${selectedId}`),
    ]).then(([det, bud, tag, med, equip]) => {
      setDetail(det.data);
      setBuddies(bud.data);
      setTags(tag.data);
      setMedia(med.data);
      setEquipment(equip.data);
    }).catch(() => {}).finally(() => setLoadingDetail(false));
  }, [selectedId]);

  const diveOptions = useMemo(() => [
    { value: '', label: t('dive_detail.select_placeholder') },
    ...dives.map(d => ({
      value: d.dive_id.toString(),
      label: `${d.start_time}${d.max_depth_m != null ? ` — ${d.max_depth_m}m` : ''}${d.duration_min != null ? ` / ${d.duration_min}min` : ''}`,
    })),
  ], [dives, t]);

  const TOP_TABS = useMemo(() => [
    { id: 'trip'    as const, label: t('dive_detail.top_trip') },
    { id: 'site'    as const, label: t('dive_detail.top_site') },
    { id: 'license' as const, label: t('dive_detail.top_license') },
    { id: 'device'  as const, label: t('dive_detail.top_device') },
  ], [t]);

  const TABS = useMemo(() => [
    { id: 'info',      label: t('dive_detail.tab_info') },
    { id: 'tanks',     label: t('dive_detail.tab_tanks') },
    { id: 'segments',  label: t('dive_detail.tab_segments') },
    { id: 'profile',   label: t('dive_detail.tab_profile') },
    { id: 'events',    label: t('dive_detail.tab_events') },
    { id: 'buddies',   label: t('dive_detail.tab_buddies') },
    { id: 'tags',      label: t('dive_detail.tab_tags') },
    { id: 'media',     label: t('dive_detail.tab_media') },
    { id: 'equipment', label: t('dive_detail.tab_equipment') },
  ], [t]);

  // GENERIC DELETE
  const confirmDelete = (endpoint: string, id: number, onDone: () => void) =>
    setDeleteTarget({ endpoint, id, onDone });

  const execDelete = async () => {
    if (!deleteTarget) return;
    await api.delete(`${deleteTarget.endpoint}/${deleteTarget.id}`).catch(() => {});
    deleteTarget.onDone();
    setDeleteTarget(null);
  };

  // TANKS
  const openTankCreate = () => setTankDlg(d => ({ ...d, open: true, edit: null, err: '', form: { tank_id: '', gas_mix_id: '', start_pressure_bar: '', end_pressure_bar: '', position: '' } }));
  const openTankEdit = (t2: DiveTank) => setTankDlg(d => ({ ...d, open: true, edit: t2, err: '', form: { tank_id: t2.tank_id?.toString() || '', gas_mix_id: t2.gas_mix_id?.toString() || '', start_pressure_bar: t2.start_pressure_bar?.toString() || '', end_pressure_bar: t2.end_pressure_bar?.toString() || '', position: t2.position || '' } }));
  const saveTank = async () => {
    if (!selectedId) return;
    setTankDlg(d => ({ ...d, saving: true, err: '' }));
    const payload = {
      dive_id: selectedId,
      tank_id: tankDlg.form.tank_id ? +tankDlg.form.tank_id : null,
      gas_mix_id: tankDlg.form.gas_mix_id ? +tankDlg.form.gas_mix_id : null,
      start_pressure_bar: tankDlg.form.start_pressure_bar ? +tankDlg.form.start_pressure_bar : null,
      end_pressure_bar: tankDlg.form.end_pressure_bar ? +tankDlg.form.end_pressure_bar : null,
      position: tankDlg.form.position || null,
    };
    try {
      if (tankDlg.edit) {
        const r = await api.patch(`/dive-tanks/${tankDlg.edit.dive_tank_id}`, payload);
        setDetail(d => d ? { ...d, tanks: d.tanks.map(t2 => t2.dive_tank_id === tankDlg.edit!.dive_tank_id ? r.data : t2) } : d);
      } else {
        const r = await api.post('/dive-tanks/', payload);
        setDetail(d => d ? { ...d, tanks: [...d.tanks, r.data] } : d);
      }
      setTankDlg(d => ({ ...d, open: false }));
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setTankDlg(d => ({ ...d, err: err.response?.data?.message || t('common.error') }));
    } finally { setTankDlg(d => ({ ...d, saving: false })); }
  };

  // SEGMENTS
  const openSegCreate = () => setSegDlg(d => ({ ...d, open: true, edit: null, err: '', form: { start_t_min: '', end_t_min: '', gas_mix_id: '', setpoint_ppO2: '', note: '' } }));
  const openSegEdit = (s: DiveSegment) => setSegDlg(d => ({ ...d, open: true, edit: s, err: '', form: { start_t_min: s.start_t_min?.toString() || '', end_t_min: s.end_t_min?.toString() || '', gas_mix_id: s.gas_mix_id?.toString() || '', setpoint_ppO2: s.setpoint_ppO2?.toString() || '', note: s.note || '' } }));
  const saveSeg = async () => {
    if (!selectedId) return;
    setSegDlg(d => ({ ...d, saving: true, err: '' }));
    const payload = {
      dive_id: selectedId,
      start_t_min: segDlg.form.start_t_min ? +segDlg.form.start_t_min : null,
      end_t_min: segDlg.form.end_t_min ? +segDlg.form.end_t_min : null,
      gas_mix_id: segDlg.form.gas_mix_id ? +segDlg.form.gas_mix_id : null,
      setpoint_ppO2: segDlg.form.setpoint_ppO2 ? +segDlg.form.setpoint_ppO2 : null,
      note: segDlg.form.note || null,
    };
    try {
      if (segDlg.edit) {
        const r = await api.patch(`/dive-segments/${segDlg.edit.dive_segment_id}`, payload);
        setDetail(d => d ? { ...d, segments: d.segments.map(s => s.dive_segment_id === segDlg.edit!.dive_segment_id ? r.data : s) } : d);
      } else {
        const r = await api.post('/dive-segments/', payload);
        setDetail(d => d ? { ...d, segments: [...d.segments, r.data] } : d);
      }
      setSegDlg(d => ({ ...d, open: false }));
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setSegDlg(d => ({ ...d, err: err.response?.data?.message || t('common.error') }));
    } finally { setSegDlg(d => ({ ...d, saving: false })); }
  };

  // EVENTS
  const openEventCreate = () => setEventDlg(d => ({ ...d, open: true, edit: null, err: '', form: { t_min: '', type: '', depth_m: '' } }));
  const openEventEdit = (e2: DiveEvent) => setEventDlg(d => ({ ...d, open: true, edit: e2, err: '', form: { t_min: e2.t_min?.toString() || '', type: e2.type || '', depth_m: e2.depth_m?.toString() || '' } }));
  const saveEvent = async () => {
    if (!selectedId) return;
    setEventDlg(d => ({ ...d, saving: true, err: '' }));
    const payload = {
      dive_id: selectedId,
      t_min: eventDlg.form.t_min ? +eventDlg.form.t_min : null,
      type: eventDlg.form.type || null,
      depth_m: eventDlg.form.depth_m ? +eventDlg.form.depth_m : null,
    };
    try {
      if (eventDlg.edit) {
        const r = await api.patch(`/dive-events/${eventDlg.edit.dive_event_id}`, payload);
        setDetail(d => d ? { ...d, events: d.events.map(e2 => e2.dive_event_id === eventDlg.edit!.dive_event_id ? r.data : e2) } : d);
      } else {
        const r = await api.post('/dive-events/', payload);
        setDetail(d => d ? { ...d, events: [...d.events, r.data] } : d);
      }
      setEventDlg(d => ({ ...d, open: false }));
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setEventDlg(d => ({ ...d, err: err.response?.data?.message || t('common.error') }));
    } finally { setEventDlg(d => ({ ...d, saving: false })); }
  };

  // BUDDIES
  const openBuddyEdit = (b: DiveBuddy) => setBuddyDlg(d => ({ ...d, open: true, edit: b, err: '',
    form: { buddy_id: b.buddy_id.toString(), confirmed: b.confirmed.toString() } }));

  const saveBuddy = async () => {
    if (!selectedId) return;
    setBuddyDlg(d => ({ ...d, saving: true, err: '' }));
    try {
      if (buddyDlg.edit) {
        const r = await api.patch(`/dive-buddies/${selectedId}/${buddyDlg.edit.buddy_id}`, { confirmed: buddyDlg.form.confirmed === 'true' });
        setBuddies(prev => prev.map(b => b.dive_buddy_id === buddyDlg.edit!.dive_buddy_id ? r.data : b));
      } else {
        const r = await api.post('/dive-buddies/', { dive_id: selectedId, buddy_id: +buddyDlg.form.buddy_id, confirmed: buddyDlg.form.confirmed === 'true' });
        setBuddies(prev => [...prev, r.data]);
      }
      setBuddyDlg(d => ({ ...d, open: false }));
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setBuddyDlg(d => ({ ...d, err: err.response?.data?.message || t('common.error') }));
    } finally { setBuddyDlg(d => ({ ...d, saving: false })); }
  };

  // TAGS
  const saveTag = async () => {
    if (!selectedId) return;
    setTagDlg(d => ({ ...d, saving: true, err: '' }));
    try {
      const r = await api.post('/dive-tags/', { dive_id: selectedId, tag_id: +tagDlg.form.tag_id });
      setTags(prev => [...prev, r.data]);
      setTagDlg(d => ({ ...d, open: false }));
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setTagDlg(d => ({ ...d, err: err.response?.data?.message || t('common.error') }));
    } finally { setTagDlg(d => ({ ...d, saving: false })); }
  };

  // MEDIA
  const openMediaCreate = () => setMediaDlg(d => ({ ...d, open: true, edit: null, err: '', form: { kind: '', uri: '', caption: '' } }));
  const openMediaEdit = (m: MediaItem) => setMediaDlg(d => ({ ...d, open: true, edit: m, err: '', form: { kind: m.kind || '', uri: m.uri || '', caption: m.caption || '' } }));
  const saveMedia = async () => {
    if (!selectedId) return;
    setMediaDlg(d => ({ ...d, saving: true, err: '' }));
    const payload = { dive_id: selectedId, kind: mediaDlg.form.kind || null, uri: mediaDlg.form.uri || null, caption: mediaDlg.form.caption || null };
    try {
      if (mediaDlg.edit) {
        const r = await api.patch(`/media/${mediaDlg.edit.media_id}`, payload);
        setMedia(prev => prev.map(m => m.media_id === mediaDlg.edit!.media_id ? r.data : m));
      } else {
        const r = await api.post('/media/', payload);
        setMedia(prev => [...prev, r.data]);
      }
      setMediaDlg(d => ({ ...d, open: false }));
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setMediaDlg(d => ({ ...d, err: err.response?.data?.message || t('common.error') }));
    } finally { setMediaDlg(d => ({ ...d, saving: false })); }
  };

  // EQUIPMENT
  const saveEquip = async () => {
    if (!selectedId) return;
    setEquipDlg(d => ({ ...d, saving: true, err: '' }));
    try {
      const r = await api.post('/dive-equipment/', { dive_id: selectedId, equipment_id: +equipDlg.form.equipment_id });
      setEquipment(prev => [...prev, r.data]);
      setEquipDlg(d => ({ ...d, open: false }));
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setEquipDlg(d => ({ ...d, err: err.response?.data?.message || t('common.error') }));
    } finally { setEquipDlg(d => ({ ...d, saving: false })); }
  };

  // Tab content renderers

  const renderInfo = () => {
    if (!detail) return null;
    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 p-4">
        <InfoRow label={t('dive_detail.info_start')} value={detail.start_time} />
        <InfoRow label={t('dive_detail.info_duration')} value={detail.duration_min != null ? `${detail.duration_min} min` : null} />
        <InfoRow label={t('dive_detail.info_max_depth')} value={detail.max_depth_m != null ? `${detail.max_depth_m} m` : null} />
        <InfoRow label={t('dive_detail.info_avg_depth')} value={detail.avg_depth_m != null ? `${detail.avg_depth_m} m` : null} />
        <InfoRow label={t('dive_detail.info_breathing')} value={detail.breathing_system} />
        <InfoRow label={t('dive_detail.info_water_temp')} value={detail.water_temp_c != null ? `${detail.water_temp_c} °C` : null} />
        <InfoRow label={t('dive_detail.info_air_temp')} value={detail.air_temp_c != null ? `${detail.air_temp_c} °C` : null} />
        <InfoRow label={t('dive_detail.info_surface_interval')} value={detail.surface_interval_min != null ? `${detail.surface_interval_min} min` : null} />
        <InfoRow label={t('dive_detail.info_ndl')} value={detail.ndl_min != null ? `${detail.ndl_min} min` : null} />
        <InfoRow label={t('dive_detail.info_cns')} value={detail.cns_max_pct != null ? `${detail.cns_max_pct} %` : null} />
        <InfoRow label={t('dive_detail.info_otu')} value={detail.otu} />
        <InfoRow label={t('dive_detail.info_algorithm')} value={detail.algorithm} />
        <InfoRow label={t('dive_detail.info_deco_model')} value={detail.deco_model} />
        <InfoRow label={t('dive_detail.info_gf')} value={detail.gf_low != null && detail.gf_high != null ? `${detail.gf_low}/${detail.gf_high}` : null} />
        {detail.notes && (
          <div className="col-span-2 sm:col-span-3">
            <InfoRow label={t('dive_detail.info_notes')} value={detail.notes} />
          </div>
        )}
      </div>
    );
  };

  const renderTanks = () => (
    <>
      <div className="flex justify-end p-2">
        <Button size="sm" onClick={openTankCreate}><Plus size={14} /> {t('dive_detail.new_tank')}</Button>
      </div>
      <Table>
        <TableHeader><TableRow>
          <TableHead>{t('dive_detail.col_tank_id')}</TableHead>
          <TableHead>{t('dive_detail.col_gas_mix_id')}</TableHead>
          <TableHead>{t('dive_detail.col_start_p')}</TableHead>
          <TableHead>{t('dive_detail.col_end_p')}</TableHead>
          <TableHead>{t('dive_detail.col_position')}</TableHead>
          <TableHead>{t('common.actions')}</TableHead>
        </TableRow></TableHeader>
        <TableBody>
          {(detail?.tanks ?? []).length === 0 ? <EmptyTableRow colSpan={6} message={t('common.no_data')} /> :
            detail!.tanks.map(tk => (
              <TableRow key={tk.dive_tank_id}>
                <TableCell style={{ color: 'var(--text-muted)' }}>{tk.tank_id ?? '—'}</TableCell>
                <TableCell style={{ color: 'var(--text-muted)' }}>{tk.gas_mix_id ?? '—'}</TableCell>
                <TableCell style={{ color: 'var(--text)' }}>{tk.start_pressure_bar ?? '—'}</TableCell>
                <TableCell style={{ color: 'var(--text)' }}>{tk.end_pressure_bar ?? '—'}</TableCell>
                <TableCell style={{ color: 'var(--text-muted)' }}>{tk.position ?? '—'}</TableCell>
                <TableCell><div className="flex gap-2">
                  <Button size="sm" variant="outline" onClick={() => openTankEdit(tk)}>{t('common.edit')}</Button>
                  <Button size="sm" variant="danger" onClick={() => confirmDelete('/dive-tanks', tk.dive_tank_id, () => setDetail(d => d ? { ...d, tanks: d.tanks.filter(x => x.dive_tank_id !== tk.dive_tank_id) } : d))}><Trash2 size={12} /></Button>
                </div></TableCell>
              </TableRow>
            ))}
        </TableBody>
      </Table>
    </>
  );

  const renderSegments = () => (
    <>
      <div className="flex justify-end p-2">
        <Button size="sm" onClick={openSegCreate}><Plus size={14} /> {t('dive_detail.new_segment')}</Button>
      </div>
      <Table>
        <TableHeader><TableRow>
          <TableHead>{t('dive_detail.col_seg_start')}</TableHead>
          <TableHead>{t('dive_detail.col_seg_end')}</TableHead>
          <TableHead>{t('dive_detail.col_gas_mix_id')}</TableHead>
          <TableHead>{t('dive_detail.col_setpoint')}</TableHead>
          <TableHead>{t('dive_detail.col_note')}</TableHead>
          <TableHead>{t('common.actions')}</TableHead>
        </TableRow></TableHeader>
        <TableBody>
          {(detail?.segments ?? []).length === 0 ? <EmptyTableRow colSpan={6} message={t('common.no_data')} /> :
            detail!.segments.map(seg => (
              <TableRow key={seg.dive_segment_id}>
                <TableCell style={{ color: 'var(--text)' }}>{seg.start_t_min ?? '—'}</TableCell>
                <TableCell style={{ color: 'var(--text)' }}>{seg.end_t_min ?? '—'}</TableCell>
                <TableCell style={{ color: 'var(--text-muted)' }}>{seg.gas_mix_id ?? '—'}</TableCell>
                <TableCell style={{ color: 'var(--text-muted)' }}>{seg.setpoint_ppO2 ?? '—'}</TableCell>
                <TableCell style={{ color: 'var(--text-muted)' }}>{seg.note ?? '—'}</TableCell>
                <TableCell><div className="flex gap-2">
                  <Button size="sm" variant="outline" onClick={() => openSegEdit(seg)}>{t('common.edit')}</Button>
                  <Button size="sm" variant="danger" onClick={() => confirmDelete('/dive-segments', seg.dive_segment_id, () => setDetail(d => d ? { ...d, segments: d.segments.filter(x => x.dive_segment_id !== seg.dive_segment_id) } : d))}><Trash2 size={12} /></Button>
                </div></TableCell>
              </TableRow>
            ))}
        </TableBody>
      </Table>
    </>
  );

  const renderProfile = () => {
    const samples = detail?.samples ?? [];
    return (
      <div className="p-4">
        {samples.length === 0 ? (
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{t('dive_detail.no_samples')}</p>
        ) : (
          <>
            <div className="mb-4">
              <p className="text-sm font-medium mb-2" style={{ color: 'var(--text-subtle)' }}>{t('dive_detail.chart_title')}</p>
              <ProfileChart samples={samples} />
            </div>
            <div style={{ overflowX: 'auto' }}>
              <Table>
                <TableHeader><TableRow>
                  <TableHead>{t('dive_detail.col_t')}</TableHead>
                  <TableHead>{t('dive_detail.col_depth')}</TableHead>
                  <TableHead>{t('dive_detail.col_temp')}</TableHead>
                  <TableHead>{t('dive_detail.col_ndl')}</TableHead>
                  <TableHead>{t('dive_detail.col_ppo2')}</TableHead>
                </TableRow></TableHeader>
                <TableBody>
                  {samples.map((s, i) => (
                    <TableRow key={i}>
                      <TableCell style={{ color: 'var(--text-muted)' }}>{s.t_min}</TableCell>
                      <TableCell style={{ color: 'var(--text)' }}>{s.depth_m}</TableCell>
                      <TableCell style={{ color: 'var(--text-muted)' }}>{s.temp_c ?? '—'}</TableCell>
                      <TableCell style={{ color: 'var(--text-muted)' }}>{s.ndl_min ?? '—'}</TableCell>
                      <TableCell style={{ color: 'var(--text-muted)' }}>{s.ppO2 ?? '—'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </>
        )}
      </div>
    );
  };

  const renderEvents = () => (
    <>
      <div className="flex justify-end p-2">
        <Button size="sm" onClick={openEventCreate}><Plus size={14} /> {t('dive_detail.new_event')}</Button>
      </div>
      <Table>
        <TableHeader><TableRow>
          <TableHead>{t('dive_detail.col_event_t')}</TableHead>
          <TableHead>{t('dive_detail.col_event_type')}</TableHead>
          <TableHead>{t('dive_detail.col_event_depth')}</TableHead>
          <TableHead>{t('common.actions')}</TableHead>
        </TableRow></TableHeader>
        <TableBody>
          {(detail?.events ?? []).length === 0 ? <EmptyTableRow colSpan={4} message={t('common.no_data')} /> :
            detail!.events.map(ev => (
              <TableRow key={ev.dive_event_id}>
                <TableCell style={{ color: 'var(--text)' }}>{ev.t_min ?? '—'}</TableCell>
                <TableCell style={{ color: 'var(--text)' }}>{ev.type ?? '—'}</TableCell>
                <TableCell style={{ color: 'var(--text-muted)' }}>{ev.depth_m ?? '—'}</TableCell>
                <TableCell><div className="flex gap-2">
                  <Button size="sm" variant="outline" onClick={() => openEventEdit(ev)}>{t('common.edit')}</Button>
                  <Button size="sm" variant="danger" onClick={() => confirmDelete('/dive-events', ev.dive_event_id, () => setDetail(d => d ? { ...d, events: d.events.filter(x => x.dive_event_id !== ev.dive_event_id) } : d))}><Trash2 size={12} /></Button>
                </div></TableCell>
              </TableRow>
            ))}
        </TableBody>
      </Table>
    </>
  );

  const renderBuddies = () => (
    <>
      <div className="flex justify-end p-2">
        <Button size="sm" onClick={() => setBuddyDlg(d => ({ ...d, open: true, err: '', form: { buddy_id: '', confirmed: 'false' } }))}><Plus size={14} /> {t('dive_detail.new_buddy')}</Button>
      </div>
      <Table>
        <TableHeader><TableRow>
          <TableHead>{t('dive_detail.col_buddy')}</TableHead>
          <TableHead>{t('dive_detail.col_confirmed')}</TableHead>
          <TableHead>{t('common.actions')}</TableHead>
        </TableRow></TableHeader>
        <TableBody>
          {buddies.length === 0 ? <EmptyTableRow colSpan={3} message={t('common.no_data')} /> :
            buddies.map(b => (
              <TableRow key={b.dive_buddy_id}>
                <TableCell style={{ color: 'var(--text)' }}>{allBuddies.find(ab => ab.buddy_id === b.buddy_id)?.name ?? b.buddy_id}</TableCell>
                <TableCell style={{ color: 'var(--text-muted)' }}>{b.confirmed ? '✓' : '—'}</TableCell>
                <TableCell><div className="flex gap-2">
                  <Button size="sm" variant="outline" onClick={() => openBuddyEdit(b)}>{t('common.edit')}</Button>
                  <Button size="sm" variant="danger" onClick={() => confirmDelete('/dive-buddies', b.dive_buddy_id, () => setBuddies(prev => prev.filter(x => x.dive_buddy_id !== b.dive_buddy_id)))}><Trash2 size={12} /></Button>
                </div></TableCell>
              </TableRow>
            ))}
        </TableBody>
      </Table>
    </>
  );

  const renderTags = () => (
    <>
      <div className="flex justify-end p-2">
        <Button size="sm" onClick={() => setTagDlg(d => ({ ...d, open: true, err: '', form: { tag_id: '' } }))}><Plus size={14} /> {t('dive_detail.new_tag')}</Button>
      </div>
      <Table>
        <TableHeader><TableRow>
          <TableHead>{t('dive_detail.col_tag')}</TableHead>
          <TableHead>{t('common.actions')}</TableHead>
        </TableRow></TableHeader>
        <TableBody>
          {tags.length === 0 ? <EmptyTableRow colSpan={2} message={t('common.no_data')} /> :
            tags.map(tg => (
              <TableRow key={tg.dive_tag_id}>
                <TableCell style={{ color: 'var(--text)' }}>{allTags.find(at => at.tag_id === tg.tag_id)?.name ?? tg.tag_id}</TableCell>
                <TableCell>
                  <Button size="sm" variant="danger" onClick={() => confirmDelete('/dive-tags', tg.dive_tag_id, () => setTags(prev => prev.filter(x => x.dive_tag_id !== tg.dive_tag_id)))}><Trash2 size={12} /></Button>
                </TableCell>
              </TableRow>
            ))}
        </TableBody>
      </Table>
    </>
  );

  const renderMedia = () => (
    <>
      <div className="flex justify-end p-2">
        <Button size="sm" onClick={openMediaCreate}><Plus size={14} /> {t('dive_detail.new_media')}</Button>
      </div>
      <Table>
        <TableHeader><TableRow>
          <TableHead>{t('dive_detail.col_kind')}</TableHead>
          <TableHead>{t('dive_detail.col_uri')}</TableHead>
          <TableHead>{t('dive_detail.col_caption')}</TableHead>
          <TableHead>{t('common.actions')}</TableHead>
        </TableRow></TableHeader>
        <TableBody>
          {media.length === 0 ? <EmptyTableRow colSpan={4} message={t('common.no_data')} /> :
            media.map(m => (
              <TableRow key={m.media_id}>
                <TableCell style={{ color: 'var(--text-muted)' }}>{m.kind ?? '—'}</TableCell>
                <TableCell style={{ color: 'var(--text)', maxWidth: 160, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{m.uri ?? '—'}</TableCell>
                <TableCell style={{ color: 'var(--text-muted)' }}>{m.caption ?? '—'}</TableCell>
                <TableCell><div className="flex gap-2">
                  <Button size="sm" variant="outline" onClick={() => openMediaEdit(m)}>{t('common.edit')}</Button>
                  <Button size="sm" variant="danger" onClick={() => confirmDelete('/media', m.media_id, () => setMedia(prev => prev.filter(x => x.media_id !== m.media_id)))}><Trash2 size={12} /></Button>
                </div></TableCell>
              </TableRow>
            ))}
        </TableBody>
      </Table>
    </>
  );

  const renderEquipment = () => (
    <>
      <div className="flex justify-end p-2">
        <Button size="sm" onClick={() => setEquipDlg(d => ({ ...d, open: true, err: '', form: { equipment_id: '' } }))}><Plus size={14} /> {t('dive_detail.new_equipment')}</Button>
      </div>
      <Table>
        <TableHeader><TableRow>
          <TableHead>{t('dive_detail.col_equipment')}</TableHead>
          <TableHead>{t('common.actions')}</TableHead>
        </TableRow></TableHeader>
        <TableBody>
          {equipment.length === 0 ? <EmptyTableRow colSpan={2} message={t('common.no_data')} /> :
            equipment.map(eq => (
              <TableRow key={eq.dive_equipment_id}>
                <TableCell style={{ color: 'var(--text)' }}>{(() => { const r = allEquip.find(ae => ae.equipment_id === eq.equipment_id); return r ? [r.category, r.brand, r.model].filter(Boolean).join(' ') : eq.equipment_id; })()}</TableCell>
                <TableCell>
                  <Button size="sm" variant="danger" onClick={() => confirmDelete('/dive-equipment', eq.dive_equipment_id, () => setEquipment(prev => prev.filter(x => x.dive_equipment_id !== eq.dive_equipment_id)))}><Trash2 size={12} /></Button>
                </TableCell>
              </TableRow>
            ))}
        </TableBody>
      </Table>
    </>
  );

  const renderTopTab = () => {
    if (!detail) return null;
    const none = <p className="text-sm p-4" style={{ color: 'var(--text-muted)' }}>{t(`dive_detail.no_${activeTopTab}`)}</p>;
    if (activeTopTab === 'trip') {
      const trip = allTrips.find(tr => tr.trip_id === detail.trip_id);
      if (!trip) return none;
      return (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 p-4">
          <InfoRow label={t('trips.field_name')} value={trip.title} />
          <InfoRow label={t('trips.field_start_date')} value={trip.start_date} />
          <InfoRow label={t('trips.field_end_date')} value={trip.end_date} />
          {trip.notes && <div className="col-span-2 sm:col-span-3"><InfoRow label={t('trips.field_notes')} value={trip.notes} /></div>}
        </div>
      );
    }
    if (activeTopTab === 'site') {
      const site = allSites.find(s => s.site_id === detail.site_id);
      if (!site) return none;
      return (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 p-4">
          <InfoRow label={t('sites.field_name')} value={site.name} />
          <InfoRow label={t('sites.field_country')} value={site.country} />
          <InfoRow label={t('sites.field_region')} value={site.region} />
          <InfoRow label={t('sites.field_body_of_water')} value={site.body_of_water} />
          <InfoRow label={t('sites.field_type')} value={site.type} />
          <InfoRow label={t('sites.field_altitude')} value={site.altitude_m != null ? `${site.altitude_m} m` : null} />
          {(site.latitude != null || site.longitude != null) && (
            <InfoRow label={t('sites.col_gps')} value={site.latitude != null && site.longitude != null ? `${site.latitude}, ${site.longitude}` : null} />
          )}
          {site.description && <div className="col-span-2 sm:col-span-3"><InfoRow label={t('sites.field_notes')} value={site.description} /></div>}
        </div>
      );
    }
    if (activeTopTab === 'license') {
      const lic = allLicenses.find(l => l.license_id === detail.license_id);
      if (!lic) return none;
      return (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 p-4">
          <InfoRow label={t('licenses.field_agency')} value={lic.agency} />
          <InfoRow label={t('licenses.field_cert')} value={lic.certification} />
          <InfoRow label={t('licenses.field_level')} value={lic.level} />
          <InfoRow label={t('licenses.field_number')} value={lic.number} />
          <InfoRow label={t('licenses.field_issued')} value={lic.issued_on} />
          <InfoRow label={t('licenses.field_expires')} value={lic.expires_on} />
          {lic.note && <div className="col-span-2 sm:col-span-3"><InfoRow label={t('licenses.field_note')} value={lic.note} /></div>}
        </div>
      );
    }
    if (activeTopTab === 'device') {
      const dev = allDevices.find(d => d.device_id === detail.device_id);
      if (!dev) return none;
      return (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 p-4">
          <InfoRow label={t('devices.field_brand')} value={dev.brand} />
          <InfoRow label={t('devices.field_model')} value={dev.model} />
          <InfoRow label={t('devices.field_sn')} value={dev.serial_number} />
          <InfoRow label={t('devices.field_firmware')} value={dev.firmware} />
          <InfoRow label={t('devices.field_battery')} value={dev.battery_v != null ? `${dev.battery_v} V` : null} />
          <InfoRow label={t('devices.field_hw_model')} value={dev.hw_model_display} />
          <InfoRow label={t('devices.field_bt_mac')} value={dev.bt_mac} />
          {dev.notes && <div className="col-span-2 sm:col-span-3"><InfoRow label={t('devices.field_notes')} value={dev.notes} /></div>}
        </div>
      );
    }
    return null;
  };

  const tabContent: Record<string, () => React.ReactNode> = {
    info:      renderInfo,
    tanks:     renderTanks,
    segments:  renderSegments,
    profile:   renderProfile,
    events:    renderEvents,
    buddies:   renderBuddies,
    tags:      renderTags,
    media:     renderMedia,
    equipment: renderEquipment,
  };

  return (
    <PageContainer>
      <div className="mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3 mb-4" style={{ color: 'var(--text)' }}>
          <BookOpen style={{ color: 'var(--accent)' }} size={28} />
          {t('dive_detail.title')}
        </h1>
        <div className="max-w-lg">
          <Select
            label={t('dive_detail.select_label')}
            value={selectedId?.toString() || ''}
            onChange={e => setSelectedId(e.target.value ? +e.target.value : null)}
            options={diveOptions}
          />
        </div>
      </div>

      {!selectedId && (
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{t('dive_detail.no_dive_selected')}</p>
      )}

      {selectedId && loadingDetail && (
        <p style={{ color: 'var(--text-muted)' }}>{t('dive_detail.loading')}</p>
      )}

      {selectedId && !loadingDetail && detail && (
        <>
          {/* Top bar: Trip / Site / License / Device */}
          <Card className="p-0 overflow-hidden mb-4">
            <div className="flex overflow-x-auto border-b" style={{ borderColor: 'var(--border)' }}>
              {TOP_TABS.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTopTab(tab.id)}
                  className="px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors flex-shrink-0"
                  style={{
                    color: activeTopTab === tab.id ? 'var(--accent)' : 'var(--text-muted)',
                    borderBottom: activeTopTab === tab.id ? '2px solid var(--accent)' : '2px solid transparent',
                    background: 'transparent',
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>
            <div>{renderTopTab()}</div>
          </Card>

          {/* Main 9-tab card */}
          <Card className="p-0 overflow-hidden">
            {/* Tab bar */}
            <div className="flex overflow-x-auto border-b" style={{ borderColor: 'var(--border)' }}>
              {TABS.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className="px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors flex-shrink-0"
                  style={{
                    color: activeTab === tab.id ? 'var(--accent)' : 'var(--text-muted)',
                    borderBottom: activeTab === tab.id ? '2px solid var(--accent)' : '2px solid transparent',
                    background: 'transparent',
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>
            <div>{tabContent[activeTab]?.()}</div>
          </Card>
        </>
      )}

      {/* ── Tank Dialog ── */}
      <Dialog open={tankDlg.open} onClose={() => setTankDlg(d => ({ ...d, open: false }))} size="md">
        <DialogHeader title={tankDlg.edit ? t('common.edit') : t('dive_detail.new_tank')} onClose={() => setTankDlg(d => ({ ...d, open: false }))} />
        <DialogContent>
          {tankDlg.err && <p className="mb-3 text-sm" style={{ color: 'var(--danger)' }}>{tankDlg.err}</p>}
          <div className="grid grid-cols-2 gap-3">
            <Select label={t('dive_detail.field_tank_id')} value={tankDlg.form.tank_id} onChange={e => setTankDlg(d => ({ ...d, form: { ...d.form, tank_id: e.target.value } }))}
              options={[{ value: '', label: '—' }, ...allTanks.map(tk => ({ value: tk.tank_id.toString(), label: [tk.volume_l != null ? `${tk.volume_l} l` : null, tk.material, tk.serial_number ? `SN: ${tk.serial_number}` : null].filter(Boolean).join(' / ') || `#${tk.tank_id}` }))]} />
            <Select label={t('dive_detail.field_gas_mix_id')} value={tankDlg.form.gas_mix_id} onChange={e => setTankDlg(d => ({ ...d, form: { ...d.form, gas_mix_id: e.target.value } }))}
              options={[{ value: '', label: '—' }, ...allGasMixes.map(gm => ({ value: gm.gas_mix_id.toString(), label: gm.name || `${gm.gas_type}${gm.o2_percent != null ? ` ${gm.o2_percent}%` : ''}` }))]} />
            <Input label={t('dive_detail.field_start_p')} type="number" value={tankDlg.form.start_pressure_bar} onChange={e => setTankDlg(d => ({ ...d, form: { ...d.form, start_pressure_bar: e.target.value } }))} />
            <Input label={t('dive_detail.field_end_p')} type="number" value={tankDlg.form.end_pressure_bar} onChange={e => setTankDlg(d => ({ ...d, form: { ...d.form, end_pressure_bar: e.target.value } }))} />
            <Input label={t('dive_detail.field_position')} value={tankDlg.form.position} onChange={e => setTankDlg(d => ({ ...d, form: { ...d.form, position: e.target.value } }))} className="col-span-2" />
          </div>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setTankDlg(d => ({ ...d, open: false }))}>{t('common.cancel')}</Button>
          <Button loading={tankDlg.saving} onClick={saveTank}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      {/* ── Segment Dialog ── */}
      <Dialog open={segDlg.open} onClose={() => setSegDlg(d => ({ ...d, open: false }))} size="md">
        <DialogHeader title={segDlg.edit ? t('common.edit') : t('dive_detail.new_segment')} onClose={() => setSegDlg(d => ({ ...d, open: false }))} />
        <DialogContent>
          {segDlg.err && <p className="mb-3 text-sm" style={{ color: 'var(--danger)' }}>{segDlg.err}</p>}
          <div className="grid grid-cols-2 gap-3">
            <Input label={t('dive_detail.field_seg_start')} type="number" value={segDlg.form.start_t_min} onChange={e => setSegDlg(d => ({ ...d, form: { ...d.form, start_t_min: e.target.value } }))} />
            <Input label={t('dive_detail.field_seg_end')} type="number" value={segDlg.form.end_t_min} onChange={e => setSegDlg(d => ({ ...d, form: { ...d.form, end_t_min: e.target.value } }))} />
            <Select label={t('dive_detail.field_gas_mix_id')} value={segDlg.form.gas_mix_id} onChange={e => setSegDlg(d => ({ ...d, form: { ...d.form, gas_mix_id: e.target.value } }))}
              options={[{ value: '', label: '—' }, ...allGasMixes.map(gm => ({ value: gm.gas_mix_id.toString(), label: gm.name || `${gm.gas_type}${gm.o2_percent != null ? ` ${gm.o2_percent}%` : ''}` }))]} />
            <Input label={t('dive_detail.field_seg_setpoint')} type="number" value={segDlg.form.setpoint_ppO2} onChange={e => setSegDlg(d => ({ ...d, form: { ...d.form, setpoint_ppO2: e.target.value } }))} step="0.01" />
          </div>
          <div className="mt-3">
            <Textarea label={t('dive_detail.field_seg_note')} value={segDlg.form.note} onChange={e => setSegDlg(d => ({ ...d, form: { ...d.form, note: e.target.value } }))} rows={2} />
          </div>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setSegDlg(d => ({ ...d, open: false }))}>{t('common.cancel')}</Button>
          <Button loading={segDlg.saving} onClick={saveSeg}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      {/* ── Event Dialog ── */}
      <Dialog open={eventDlg.open} onClose={() => setEventDlg(d => ({ ...d, open: false }))} size="sm">
        <DialogHeader title={eventDlg.edit ? t('common.edit') : t('dive_detail.new_event')} onClose={() => setEventDlg(d => ({ ...d, open: false }))} />
        <DialogContent>
          {eventDlg.err && <p className="mb-3 text-sm" style={{ color: 'var(--danger)' }}>{eventDlg.err}</p>}
          <div className="flex flex-col gap-3">
            <Input label={t('dive_detail.field_event_t')} type="number" value={eventDlg.form.t_min} onChange={e => setEventDlg(d => ({ ...d, form: { ...d.form, t_min: e.target.value } }))} />
            <Input label={t('dive_detail.field_event_type')} value={eventDlg.form.type} onChange={e => setEventDlg(d => ({ ...d, form: { ...d.form, type: e.target.value } }))} />
            <Input label={t('dive_detail.field_event_depth')} type="number" value={eventDlg.form.depth_m} onChange={e => setEventDlg(d => ({ ...d, form: { ...d.form, depth_m: e.target.value } }))} step="0.5" />
          </div>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setEventDlg(d => ({ ...d, open: false }))}>{t('common.cancel')}</Button>
          <Button loading={eventDlg.saving} onClick={saveEvent}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      {/* ── Buddy Dialog ── */}
      <Dialog open={buddyDlg.open} onClose={() => setBuddyDlg(d => ({ ...d, open: false }))} size="sm">
        <DialogHeader title={buddyDlg.edit ? t('common.edit') : t('dive_detail.new_buddy')} onClose={() => setBuddyDlg(d => ({ ...d, open: false }))} />
        <DialogContent>
          {buddyDlg.err && <p className="mb-3 text-sm" style={{ color: 'var(--danger)' }}>{buddyDlg.err}</p>}
          <div className="flex flex-col gap-3">
            {buddyDlg.edit ? (
              <div>
                <p className="text-xs mb-0.5" style={{ color: 'var(--text-subtle)' }}>{t('dive_detail.field_buddy')}</p>
                <p className="text-sm font-medium" style={{ color: 'var(--text)' }}>
                  {allBuddies.find(ab => ab.buddy_id === buddyDlg.edit!.buddy_id)?.name ?? `#${buddyDlg.edit.buddy_id}`}
                </p>
              </div>
            ) : (
              <Select
                label={t('dive_detail.field_buddy')}
                value={buddyDlg.form.buddy_id}
                onChange={e => setBuddyDlg(d => ({ ...d, form: { ...d.form, buddy_id: e.target.value } }))}
                options={[{ value: '', label: '—' }, ...allBuddies.map(b => ({ value: b.buddy_id.toString(), label: b.name }))]}
              />
            )}
            <Select
              label={t('dive_detail.field_confirmed')}
              value={buddyDlg.form.confirmed}
              onChange={e => setBuddyDlg(d => ({ ...d, form: { ...d.form, confirmed: e.target.value } }))}
              options={[{ value: 'false', label: t('common.no') }, { value: 'true', label: t('common.yes') }]}
            />
          </div>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setBuddyDlg(d => ({ ...d, open: false }))}>{t('common.cancel')}</Button>
          <Button loading={buddyDlg.saving} onClick={saveBuddy} disabled={!buddyDlg.edit && !buddyDlg.form.buddy_id}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      {/* ── Tag Dialog ── */}
      <Dialog open={tagDlg.open} onClose={() => setTagDlg(d => ({ ...d, open: false }))} size="sm">
        <DialogHeader title={t('dive_detail.new_tag')} onClose={() => setTagDlg(d => ({ ...d, open: false }))} />
        <DialogContent>
          {tagDlg.err && <p className="mb-3 text-sm" style={{ color: 'var(--danger)' }}>{tagDlg.err}</p>}
          <Select
            label={t('dive_detail.field_tag')}
            value={tagDlg.form.tag_id}
            onChange={e => setTagDlg(d => ({ ...d, form: { tag_id: e.target.value } }))}
            options={[{ value: '', label: '—' }, ...allTags.map(tg => ({ value: tg.tag_id.toString(), label: tg.name }))]}
          />
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setTagDlg(d => ({ ...d, open: false }))}>{t('common.cancel')}</Button>
          <Button loading={tagDlg.saving} onClick={saveTag} disabled={!tagDlg.form.tag_id}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      {/* ── Media Dialog ── */}
      <Dialog open={mediaDlg.open} onClose={() => setMediaDlg(d => ({ ...d, open: false }))} size="md">
        <DialogHeader title={mediaDlg.edit ? t('common.edit') : t('dive_detail.new_media')} onClose={() => setMediaDlg(d => ({ ...d, open: false }))} />
        <DialogContent>
          {mediaDlg.err && <p className="mb-3 text-sm" style={{ color: 'var(--danger)' }}>{mediaDlg.err}</p>}
          <div className="flex flex-col gap-3">
            <Input label={t('dive_detail.field_kind')} value={mediaDlg.form.kind} onChange={e => setMediaDlg(d => ({ ...d, form: { ...d.form, kind: e.target.value } }))} />
            <Input label={t('dive_detail.field_uri')} value={mediaDlg.form.uri} onChange={e => setMediaDlg(d => ({ ...d, form: { ...d.form, uri: e.target.value } }))} />
            <Input label={t('dive_detail.field_caption')} value={mediaDlg.form.caption} onChange={e => setMediaDlg(d => ({ ...d, form: { ...d.form, caption: e.target.value } }))} />
          </div>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setMediaDlg(d => ({ ...d, open: false }))}>{t('common.cancel')}</Button>
          <Button loading={mediaDlg.saving} onClick={saveMedia}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      {/* ── Equipment Dialog ── */}
      <Dialog open={equipDlg.open} onClose={() => setEquipDlg(d => ({ ...d, open: false }))} size="sm">
        <DialogHeader title={t('dive_detail.new_equipment')} onClose={() => setEquipDlg(d => ({ ...d, open: false }))} />
        <DialogContent>
          {equipDlg.err && <p className="mb-3 text-sm" style={{ color: 'var(--danger)' }}>{equipDlg.err}</p>}
          <Select
            label={t('dive_detail.field_equipment')}
            value={equipDlg.form.equipment_id}
            onChange={e => setEquipDlg(d => ({ ...d, form: { equipment_id: e.target.value } }))}
            options={[{ value: '', label: '—' }, ...allEquip.map(eq => ({ value: eq.equipment_id.toString(), label: [eq.category, eq.brand, eq.model].filter(Boolean).join(' ') }))]}
          />
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setEquipDlg(d => ({ ...d, open: false }))}>{t('common.cancel')}</Button>
          <Button loading={equipDlg.saving} onClick={saveEquip} disabled={!equipDlg.form.equipment_id}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      {/* ── Generic Delete Confirm ── */}
      <Dialog open={deleteTarget !== null} onClose={() => setDeleteTarget(null)} size="sm">
        <DialogHeader title={t('common.delete')} onClose={() => setDeleteTarget(null)} />
        <DialogContent><p style={{ color: 'var(--text)' }}>{t('dive_detail.delete_confirm')}</p></DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setDeleteTarget(null)}>{t('common.cancel')}</Button>
          <Button variant="danger" onClick={execDelete}>{t('common.delete')}</Button>
        </DialogFooter>
      </Dialog>
    </PageContainer>
  );
}
