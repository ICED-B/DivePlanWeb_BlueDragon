import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Map, Plus, Trash2, AlertTriangle } from 'lucide-react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, EmptyTableRow } from '../../components/ui/table';
import { Badge } from '../../components/ui/badge';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';

interface Tank {
  tank_name: string;
  size_l: number;
  pressure_bar: number;
  backup_pressure_bar: number;
  f_o2: number;
  f_he: number;
}

interface Waypoint {
  seq_num: number;
  depth: number;
  time_min: number;
  tank_name: string;
}

interface ProfileRow {
  segment_id: number;
  seg_type: string;
  from_depth: number;
  to_depth: number;
  duration_min: number;
  tank_name: string;
  mix: string;
}

interface DecoStop {
  stop_depth_m: number;
  duration_min: number;
  tank_name: string;
  mix: string;
}

interface TankGas {
  tank_name: string;
  mix: string;
  gas_sum_l: number;
  usable_l: number;
  backup_l: number;
  consumed_l: number;
  remaining_l: number;
}

interface PlanSummary {
  total_time_min: number;
  avg_depth_m: number;
  max_depth_m: number;
  ndl_min: number | null;
  is_deco: boolean;
  gas_sum_l: number;
  consumed_gas_l: number;
  remaining_gas_l: number;
  tanks_gas: TankGas[];
  cns_total_pct: number;
  otu_total: number;
  mods: Record<string, number>;
  deco_source: string;
  warnings: string[];
}

interface PlanResult {
  profile: ProfileRow[];
  deco_stops: DecoStop[];
  summary: PlanSummary;
  depth_unit: string;
}

// Dive Profile SVG Chart

function DiveProfileChart({ profile, maxDepth, totalTime, du }: {
  profile: ProfileRow[];
  maxDepth: number;
  totalTime: number;
  du: string;
}) {
  if (profile.length === 0 || maxDepth <= 0 || totalTime <= 0) return null;

  const W = 300, H = 150;
  const PAD_L = 32, PAD_R = 8, PAD_T = 8, PAD_B = 18;
  const chartW = W - PAD_L - PAD_R;
  const chartH = H - PAD_T - PAD_B;

  // Build (time, depth) point sequence
  const pts: [number, number][] = [[0, profile[0].from_depth]];
  let elapsed = 0;
  for (const row of profile) {
    elapsed += row.duration_min;
    pts.push([elapsed, row.to_depth]);
  }

  const toX = (time: number) => PAD_L + (time / totalTime) * chartW;
  const toY = (depth: number) => PAD_T + (depth / maxDepth) * chartH;

  const ptStr = pts.map(([ti, d]) => `${toX(ti).toFixed(1)},${toY(d).toFixed(1)}`).join(' ');
  const areaStr = `${toX(0).toFixed(1)},${PAD_T} ${ptStr} ${toX(totalTime).toFixed(1)},${PAD_T}`;

  // Depth grid lines
  const depthStep = maxDepth > 30 ? 10 : maxDepth > 15 ? 5 : 3;
  const gridDepths: number[] = [];
  for (let d = depthStep; d <= maxDepth; d += depthStep) gridDepths.push(d);

  // Time tick labels
  const timeStep = totalTime > 60 ? 20 : totalTime > 30 ? 10 : 5;
  const timeTicks: number[] = [];
  for (let tt = timeStep; tt < totalTime; tt += timeStep) timeTicks.push(tt);
  timeTicks.push(totalTime);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full">
      {gridDepths.map(d => (
        <line key={d} x1={PAD_L} y1={toY(d)} x2={W - PAD_R} y2={toY(d)}
          stroke="var(--border)" strokeWidth="1" strokeDasharray="3,3" />
      ))}
      {gridDepths.map(d => (
        <text key={d} x={PAD_L - 3} y={toY(d) + 4} fill="var(--text-muted)"
          fontSize="8" textAnchor="end">{d}{du}</text>
      ))}
      {timeTicks.map(tt => (
        <text key={tt} x={toX(tt)} y={H - 2} fill="var(--text-muted)"
          fontSize="8" textAnchor="middle">{tt}</text>
      ))}
      <polygon points={areaStr}
        fill="color-mix(in srgb, var(--accent) 10%, transparent)" />
      <polyline points={ptStr}
        fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinejoin="round" />
      {pts.map(([ti, d], i) => (
        <circle key={i} cx={toX(ti)} cy={toY(d)} r="3" fill="var(--accent)" />
      ))}
    </svg>
  );
}

// DEFAULTS

const defaultTank = (): Tank => ({
  tank_name: 'AIR_1',
  size_l: 12,
  pressure_bar: 200,
  backup_pressure_bar: 30,
  f_o2: 0.21,
  f_he: 0,
});

const defaultWaypoint = (tankName: string, seq: number): Waypoint => ({
  seq_num: seq,
  depth: 20,
  time_min: 20,
  tank_name: tankName,
});

// PAGE

export default function BigPlannerPage() {
  const { t } = useTranslation();

  const SEG_TYPE_LABELS: Record<string, string> = {
    descent:   t('planner.seg_type_descent'),
    bottom:    t('planner.seg_type_bottom'),
    ascent:    t('planner.seg_type_ascent'),
    deco_stop: t('planner.seg_type_deco_stop'),
  };

  // Form state
  const [sacLMin, setSacLMin] = useState('20');
  const [allowDeco, setAllowDeco] = useState(true);
  const [ppo2Limit, setPpo2Limit] = useState('1.6');
  const [descentRate, setDescentRate] = useState('10');
  const [ascentRate, setAscentRate] = useState('10');
  const [tanks, setTanks] = useState<Tank[]>([defaultTank()]);
  const [waypoints, setWaypoints] = useState<Waypoint[]>([defaultWaypoint('AIR_1', 1)]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Result state
  const [result, setResult] = useState<PlanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Tank management
  const addTank = () => {
    const n = tanks.length + 1;
    setTanks(prev => [...prev, { ...defaultTank(), tank_name: `TANK_${n}` }]);
  };

  const removeTank = (idx: number) => {
    setTanks(prev => prev.filter((_, i) => i !== idx));
  };

  const updateTank = (idx: number, key: keyof Tank, value: string | number) => {
    setTanks(prev => prev.map((tk, i) => i === idx ? { ...tk, [key]: value } : tk));
  };

  // Waypoint management
  const addWaypoint = () => {
    const firstTank = tanks[0]?.tank_name || 'AIR_1';
    const seq = waypoints.length > 0 ? Math.max(...waypoints.map(w => w.seq_num)) + 1 : 1;
    setWaypoints(prev => [...prev, defaultWaypoint(firstTank, seq)]);
  };

  const removeWaypoint = (idx: number) => {
    setWaypoints(prev => prev.filter((_, i) => i !== idx));
  };

  const updateWaypoint = (idx: number, key: keyof Waypoint, value: string | number) => {
    setWaypoints(prev => prev.map((w, i) => i === idx ? { ...w, [key]: value } : w));
  };

  // Submit
  const handlePlan = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const r = await api.post('/planner/plan', {
        sac_l_min: +sacLMin,
        allow_deco: allowDeco,
        ppo2_limit: +ppo2Limit,
        descent_rate_m_min: +descentRate,
        ascent_rate_m_min: +ascentRate,
        tanks,
        waypoints,
      });
      setResult(r.data);
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setError(err.response?.data?.message || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const du = result?.depth_unit || 'm';

  return (
    <PageContainer>
      <div className="mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3" style={{ color: 'var(--text)' }}>
          <Map style={{ color: 'var(--accent)' }} size={28} />
          {t('planner.title')}
        </h1>
        <p className="mt-1 text-sm" style={{ color: 'var(--text-muted)' }}>{t('planner.subtitle')}</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* ── Left: Form ── */}
        <div className="flex flex-col gap-6">

          {/* Basic settings */}
          <Card className="p-5 flex flex-col gap-4">
            <h2 className="font-semibold" style={{ color: 'var(--text)' }}>{t('planner.basic_settings')}</h2>
            <div className="grid grid-cols-2 gap-3">
              <Input
                label={t('planner.sac')}
                type="number" value={sacLMin} onChange={e => setSacLMin(e.target.value)}
                min="5" max="100" step="1"
              />
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium" style={{ color: 'var(--text-muted)' }}>{t('planner.deco_mode')}</label>
                <label className="flex items-center gap-2 cursor-pointer" style={{ color: 'var(--text)' }}>
                  <input type="checkbox" checked={allowDeco} onChange={e => setAllowDeco(e.target.checked)} className="w-4 h-4" />
                  <span className="text-sm">{t('planner.allow_deco')}</span>
                </label>
              </div>
            </div>
            <button
              className="text-sm text-left"
              style={{ color: 'var(--accent)', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
              onClick={() => setShowAdvanced(!showAdvanced)}
            >
              {showAdvanced ? t('planner.hide_advanced') : t('planner.show_advanced')}
            </button>
            {showAdvanced && (
              <div className="grid grid-cols-3 gap-3">
                <Input label={t('planner.ppo2_limit')} type="number" value={ppo2Limit} onChange={e => setPpo2Limit(e.target.value)} min="1" max="2" step="0.05" />
                <Input label={t('planner.descent_rate')} type="number" value={descentRate} onChange={e => setDescentRate(e.target.value)} min="1" step="1" />
                <Input label={t('planner.ascent_rate')} type="number" value={ascentRate} onChange={e => setAscentRate(e.target.value)} min="1" step="1" />
              </div>
            )}
          </Card>

          {/* Tanks */}
          <Card className="p-5 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold" style={{ color: 'var(--text)' }}>{t('planner.tanks_section')}</h2>
              <Button size="sm" variant="outline" onClick={addTank}>
                <Plus size={14} /> {t('planner.add_tank')}
              </Button>
            </div>
            {tanks.map((tank, i) => (
              <div key={i} className="rounded-lg p-3 flex flex-col gap-2" style={{ backgroundColor: 'var(--surface)', border: '1px solid var(--border)' }}>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium" style={{ color: 'var(--text)' }}>{t('planner.col_tank')} {i + 1}</span>
                  {tanks.length > 1 && (
                    <button onClick={() => removeTank(i)} style={{ color: 'var(--danger)', background: 'none', border: 'none', cursor: 'pointer' }}>
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <Input label={t('planner.tank_name')} value={tank.tank_name} onChange={e => updateTank(i, 'tank_name', e.target.value)} />
                  <Input label={t('planner.tank_size')} type="number" value={tank.size_l} onChange={e => updateTank(i, 'size_l', +e.target.value)} min="1" step="0.5" />
                  <Input label={t('planner.tank_pressure')} type="number" value={tank.pressure_bar} onChange={e => updateTank(i, 'pressure_bar', +e.target.value)} min="1" step="10" />
                  <Input label={t('planner.tank_backup')} type="number" value={tank.backup_pressure_bar} onChange={e => updateTank(i, 'backup_pressure_bar', +e.target.value)} min="0" step="10" />
                  <Input label={t('planner.fo2')} type="number" value={tank.f_o2} onChange={e => updateTank(i, 'f_o2', +e.target.value)} min="0.18" max="100" step="0.01" />
                  <Input label={t('planner.fhe')} type="number" value={tank.f_he} onChange={e => updateTank(i, 'f_he', +e.target.value)} min="0" max="100" step="0.01" />
                </div>
              </div>
            ))}
          </Card>

          {/* Waypoints */}
          <Card className="p-5 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold" style={{ color: 'var(--text)' }}>{t('planner.waypoints')}</h2>
              <Button size="sm" variant="outline" onClick={addWaypoint}>
                <Plus size={14} /> {t('planner.add_waypoint')}
              </Button>
            </div>
            {waypoints.map((wp, i) => (
              <div key={i} className="rounded-lg p-3 flex flex-col gap-2" style={{ backgroundColor: 'var(--surface)', border: '1px solid var(--border)' }}>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium" style={{ color: 'var(--text)' }}>{t('planner.waypoint')} #{wp.seq_num}</span>
                  {waypoints.length > 1 && (
                    <button onClick={() => removeWaypoint(i)} style={{ color: 'var(--danger)', background: 'none', border: 'none', cursor: 'pointer' }}>
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <Input label={t('planner.depth')} type="number" value={wp.depth} onChange={e => updateWaypoint(i, 'depth', +e.target.value)} min="0" step="1" />
                  <Input label={t('planner.time')} type="number" value={wp.time_min} onChange={e => updateWaypoint(i, 'time_min', +e.target.value)} min="0" step="1" />
                  <div className="flex flex-col gap-1">
                    <label className="text-sm font-medium" style={{ color: 'var(--text-muted)' }}>{t('planner.col_tank')}</label>
                    <select
                      className="input-base w-full px-3 py-2 text-sm cursor-pointer"
                      value={wp.tank_name}
                      onChange={e => updateWaypoint(i, 'tank_name', e.target.value)}
                    >
                      {tanks.map(tk => (
                        <option key={tk.tank_name} value={tk.tank_name}>{tk.tank_name}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            ))}
          </Card>

          {error && <p style={{ color: 'var(--danger)' }}>{error}</p>}
          <Button size="lg" onClick={handlePlan} loading={loading}>
            {t('planner.calculate')}
          </Button>
        </div>

        {/* ── Right: Results ── */}
        <div className="flex flex-col gap-6">
          {!result && !loading && (
            <div className="flex flex-col items-center justify-center py-24 text-center" style={{ color: 'var(--text-muted)' }}>
              <Map size={48} className="mb-4 opacity-30" />
              <p>{t('planner.form_hint')}</p>
            </div>
          )}

          {result && (
            <>
              {/* Summary */}
              <Card className="p-5">
                <h2 className="font-semibold mb-4" style={{ color: 'var(--text)' }}>{t('planner.result_summary')}</h2>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  {[
                    { label: t('planner.summary_total_time'), value: `${result.summary.total_time_min} min` },
                    { label: t('planner.summary_max_depth'),  value: `${result.summary.max_depth_m} ${du}` },
                    { label: t('planner.summary_avg_depth'),  value: `${result.summary.avg_depth_m} ${du}` },
                    { label: t('planner.summary_ndl'),        value: result.summary.ndl_min != null ? `${result.summary.ndl_min} min` : '—' },
                    { label: t('planner.summary_cns'),        value: `${result.summary.cns_total_pct?.toFixed(1)} %` },
                    { label: t('planner.summary_otu'),        value: result.summary.otu_total?.toFixed(1) },
                  ].map(({ label, value }) => (
                    <div key={label} className="rounded-lg p-3" style={{ backgroundColor: 'var(--surface)', border: '1px solid var(--border)' }}>
                      <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{label}</p>
                      <p className="font-semibold mt-0.5" style={{ color: 'var(--text)' }}>{value}</p>
                    </div>
                  ))}
                </div>
                <div className="flex items-center gap-2 mt-3">
                  {result.summary.is_deco
                    ? <Badge variant="warning">{t('planner.deco_badge')}</Badge>
                    : <Badge variant="success">{t('planner.ndl_badge')}</Badge>
                  }
                  <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                    {t('planner.table_source')} {result.summary.deco_source}
                  </span>
                </div>
                {result.summary.warnings.length > 0 && (
                  <div className="mt-3 rounded-lg p-3" style={{ backgroundColor: 'color-mix(in srgb, var(--warning) 10%, transparent)', border: '1px solid var(--warning)' }}>
                    <div className="flex items-center gap-2 mb-2">
                      <AlertTriangle size={14} style={{ color: 'var(--warning)' }} />
                      <span className="text-sm font-medium" style={{ color: 'var(--warning)' }}>{t('planner.warnings_title')}</span>
                    </div>
                    {result.summary.warnings.map((w, i) => (
                      <p key={i} className="text-xs" style={{ color: 'var(--text)' }}>{w}</p>
                    ))}
                  </div>
                )}
              </Card>

              {/* Dive Profile Chart */}
              <Card className="p-5">
                <h2 className="font-semibold mb-3" style={{ color: 'var(--text)' }}>{t('planner.profile_chart')}</h2>
                <DiveProfileChart
                  profile={result.profile}
                  maxDepth={result.summary.max_depth_m}
                  totalTime={result.summary.total_time_min}
                  du={du}
                />
              </Card>

              {/* Gas per tank */}
              {result.summary.tanks_gas.length > 0 && (
                <Card className="p-5">
                  <h2 className="font-semibold mb-4" style={{ color: 'var(--text)' }}>{t('planner.gas_section')}</h2>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>{t('planner.col_tank')}</TableHead>
                        <TableHead>{t('planner.col_total_l')}</TableHead>
                        <TableHead>{t('planner.col_consumed_l')}</TableHead>
                        <TableHead>{t('planner.col_remaining_l')}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {result.summary.tanks_gas.map((tg, i) => (
                        <TableRow key={i}>
                          <TableCell style={{ color: 'var(--text)' }}>
                            <div>{tg.tank_name}</div>
                            <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{tg.mix}</div>
                          </TableCell>
                          <TableCell style={{ color: 'var(--text-muted)' }}>{tg.gas_sum_l.toFixed(0)}</TableCell>
                          <TableCell style={{ color: 'var(--danger)' }}>{tg.consumed_l.toFixed(0)}</TableCell>
                          <TableCell style={{ color: 'var(--success)' }}>{tg.remaining_l.toFixed(0)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </Card>
              )}

              {/* Deco Stops */}
              {result.deco_stops.length > 0 && (
                <Card className="p-5">
                  <h2 className="font-semibold mb-4" style={{ color: 'var(--text)' }}>{t('planner.result_deco')}</h2>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>{t('planner.col_depth')}</TableHead>
                        <TableHead>{t('planner.col_duration')}</TableHead>
                        <TableHead>{t('planner.col_tank')}</TableHead>
                        <TableHead>{t('planner.col_mix')}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {result.deco_stops.map((s, i) => (
                        <TableRow key={i}>
                          <TableCell style={{ color: 'var(--text)' }}>{s.stop_depth_m} {du}</TableCell>
                          <TableCell style={{ color: 'var(--warning)', fontWeight: 600 }}>{s.duration_min} min</TableCell>
                          <TableCell style={{ color: 'var(--text-muted)' }}>{s.tank_name}</TableCell>
                          <TableCell style={{ color: 'var(--text-muted)' }}>{s.mix}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </Card>
              )}

              {/* Profile table */}
              <Card className="p-5">
                <h2 className="font-semibold mb-4" style={{ color: 'var(--text)' }}>{t('planner.result_profile')}</h2>
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>{t('planner.col_num')}</TableHead>
                        <TableHead>{t('planner.col_type')}</TableHead>
                        <TableHead>{t('planner.col_from')} ({du})</TableHead>
                        <TableHead>{t('planner.col_to')} ({du})</TableHead>
                        <TableHead>{t('planner.col_duration')}</TableHead>
                        <TableHead>{t('planner.col_tank')}</TableHead>
                        <TableHead>{t('planner.col_mix')}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {result.profile.length === 0 ? (
                        <EmptyTableRow colSpan={7} message={t('planner.no_segments')} />
                      ) : result.profile.map((row) => (
                        <TableRow key={row.segment_id}>
                          <TableCell style={{ color: 'var(--text-muted)' }}>{row.segment_id}</TableCell>
                          <TableCell>
                            <Badge variant={
                              row.seg_type === 'deco_stop' ? 'warning' :
                              row.seg_type === 'bottom' ? 'accent' : 'muted'
                            }>
                              {SEG_TYPE_LABELS[row.seg_type] || row.seg_type}
                            </Badge>
                          </TableCell>
                          <TableCell style={{ color: 'var(--text-muted)' }}>{row.from_depth}</TableCell>
                          <TableCell style={{ color: 'var(--text)' }}>{row.to_depth}</TableCell>
                          <TableCell style={{ color: 'var(--text)' }}>{row.duration_min}</TableCell>
                          <TableCell style={{ color: 'var(--text-muted)' }}>{row.tank_name}</TableCell>
                          <TableCell style={{ color: 'var(--text-muted)' }}>{row.mix}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </Card>
            </>
          )}
        </div>
      </div>
    </PageContainer>
  );
}
