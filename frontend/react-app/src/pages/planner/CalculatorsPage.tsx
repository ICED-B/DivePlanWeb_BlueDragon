import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Gauge, Wind, Droplets, Activity, Timer, Layers, Waves } from 'lucide-react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input, Select } from '../../components/ui/input';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../../components/ui/table';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';

// GENERIC STATE HOOK

function useCalc(endpoint: string) {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

  const calc = async (payload: Record<string, unknown>) => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const r = await api.post(`/planner/calculators/${endpoint}`, payload);
      setResult(r.data);
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setError(err.response?.data?.message || t('calc.calc_error'));
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, result, calc };
}

// CARD WRAPPER

function CalcCard({
  title, desc, formula, icon, children, onCalc, loading, error, resultText, resultNode,
}: {
  title: string; desc: string; formula?: string; icon: React.ReactNode;
  children: React.ReactNode;
  onCalc: () => void; loading: boolean; error: string;
  resultText?: string | null; resultNode?: React.ReactNode;
}) {
  const { t } = useTranslation();
  return (
    <Card className="p-5 flex flex-col gap-3">
      <div className="flex items-start gap-3">
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: 'color-mix(in srgb, var(--accent) 15%, transparent)' }}
        >
          <span style={{ color: 'var(--accent)' }}>{icon}</span>
        </div>
        <div>
          <h3 className="font-semibold text-sm" style={{ color: 'var(--text)' }}>{title}</h3>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{desc}</p>
        </div>
      </div>
      {formula && (
        <div
          className="px-3 py-1.5 rounded text-xs font-mono"
          style={{
            backgroundColor: 'color-mix(in srgb, var(--accent) 8%, transparent)',
            color: 'var(--text-muted)',
            border: '1px solid color-mix(in srgb, var(--border) 60%, transparent)',
          }}
        >
          {formula}
        </div>
      )}
      <div className="flex flex-col gap-2">{children}</div>
      <Button size="sm" onClick={onCalc} loading={loading}>{t('calc.calculate')}</Button>
      {error && <p className="text-xs" style={{ color: 'var(--danger)' }}>{error}</p>}
      {resultText && (
        <div
          className="rounded-lg px-4 py-2 text-center font-bold text-lg"
          style={{ backgroundColor: 'color-mix(in srgb, var(--accent) 10%, transparent)', color: 'var(--accent)' }}
        >
          {resultText}
        </div>
      )}
      {resultNode}
    </Card>
  );
}

// INDIVIDUAL CALCULATORS

function PPO2Calc() {
  const { t } = useTranslation();
  const [fo2, setFo2] = useState('0.21');
  const [depth, setDepth] = useState('30');
  const { loading, error, result, calc } = useCalc('ppo2');
  return (
    <CalcCard title={t('calc.ppo2_title')} desc={t('calc.ppo2_desc')} formula={t('calc.formula_ppo2')}
      icon={<Gauge size={16} />}
      onCalc={() => calc({ f_o2: +fo2, depth: +depth })} loading={loading} error={error}
      resultText={result ? `${result.result} ${result.unit}` : null}>
      <Input label={t('calc.input_fo2')} type="number" value={fo2} onChange={e => setFo2(e.target.value)} min="0" max="1" step="0.01" />
      <Input label={t('calc.input_depth')} type="number" value={depth} onChange={e => setDepth(e.target.value)} min="0" step="1" />
    </CalcCard>
  );
}

function MODCalc() {
  const { t } = useTranslation();
  const [fo2, setFo2] = useState('0.32');
  const [maxPpo2, setMaxPpo2] = useState('1.4');
  const { loading, error, result, calc } = useCalc('mod');
  return (
    <CalcCard title={t('calc.mod_title')} desc={t('calc.mod_desc')} formula={t('calc.formula_mod')}
      icon={<Gauge size={16} />}
      onCalc={() => calc({ f_o2: +fo2, max_pp_o2: +maxPpo2 })} loading={loading} error={error}
      resultText={result ? `${result.result} ${result.unit}` : null}>
      <Input label={t('calc.input_fo2')} type="number" value={fo2} onChange={e => setFo2(e.target.value)} min="0" max="1" step="0.01" />
      <Input label={t('calc.input_max_ppo2')} type="number" value={maxPpo2} onChange={e => setMaxPpo2(e.target.value)} min="0.5" max="2" step="0.1" />
    </CalcCard>
  );
}

function BestMixCalc() {
  const { t } = useTranslation();
  const [depth, setDepth] = useState('30');
  const [targetPpo2, setTargetPpo2] = useState('1.4');
  const { loading, error, result, calc } = useCalc('best-mix');
  const r = result as { result?: number } | null;
  return (
    <CalcCard title={t('calc.best_mix_title')} desc={t('calc.best_mix_desc')} formula={t('calc.formula_best_mix')}
      icon={<Wind size={16} />}
      onCalc={() => calc({ depth: +depth, target_pp_o2: +targetPpo2 })} loading={loading} error={error}
      resultText={r ? `FO₂ = ${(r.result! * 100).toFixed(1)} %` : null}>
      <Input label={t('calc.input_depth')} type="number" value={depth} onChange={e => setDepth(e.target.value)} min="0" step="1" />
      <Input label={t('calc.input_target_ppo2')} type="number" value={targetPpo2} onChange={e => setTargetPpo2(e.target.value)} min="0.5" max="2" step="0.1" />
    </CalcCard>
  );
}

function EADCalc() {
  const { t } = useTranslation();
  const [depth, setDepth] = useState('30');
  const [fo2, setFo2] = useState('0.32');
  const { loading, error, result, calc } = useCalc('ead');
  return (
    <CalcCard title={t('calc.ead_title')} desc={t('calc.ead_desc')} formula={t('calc.formula_ead')}
      icon={<Waves size={16} />}
      onCalc={() => calc({ depth: +depth, f_o2: +fo2 })} loading={loading} error={error}
      resultText={result ? `${result.result} ${result.unit}` : null}>
      <Input label={t('calc.input_depth')} type="number" value={depth} onChange={e => setDepth(e.target.value)} min="0" step="1" />
      <Input label={t('calc.input_fo2')} type="number" value={fo2} onChange={e => setFo2(e.target.value)} min="0" max="1" step="0.01" />
    </CalcCard>
  );
}

function ENDCalc() {
  const { t } = useTranslation();
  const [depth, setDepth] = useState('40');
  const [fo2, setFo2] = useState('0.21');
  const [fhe, setFhe] = useState('0.35');
  const { loading, error, result, calc } = useCalc('end');
  return (
    <CalcCard title={t('calc.end_title')} desc={t('calc.end_desc')} formula={t('calc.formula_end')}
      icon={<Layers size={16} />}
      onCalc={() => calc({ depth: +depth, f_o2: +fo2, f_he: +fhe })} loading={loading} error={error}
      resultText={result ? `${result.result} ${result.unit}` : null}>
      <Input label={t('calc.input_depth')} type="number" value={depth} onChange={e => setDepth(e.target.value)} min="0" step="1" />
      <Input label={t('calc.input_fo2')} type="number" value={fo2} onChange={e => setFo2(e.target.value)} min="0" max="1" step="0.01" />
      <Input label={t('calc.input_fhe')} type="number" value={fhe} onChange={e => setFhe(e.target.value)} min="0" max="1" step="0.01" />
    </CalcCard>
  );
}

function TankGasCalc() {
  const { t } = useTranslation();
  const [size, setSize] = useState('12');
  const [pressure, setPressure] = useState('200');
  const { loading, error, result, calc } = useCalc('tank-gas-content');
  return (
    <CalcCard title={t('calc.tank_gas_title')} desc={t('calc.tank_gas_desc')} formula={t('calc.formula_tank_gas')}
      icon={<Droplets size={16} />}
      onCalc={() => calc({ tank_size: +size, pressure: +pressure })} loading={loading} error={error}
      resultText={result ? `${result.result} ${result.unit}` : null}>
      <Input label={t('calc.input_size')} type="number" value={size} onChange={e => setSize(e.target.value)} min="0" step="0.5" />
      <Input label={t('calc.input_pressure')} type="number" value={pressure} onChange={e => setPressure(e.target.value)} min="0" step="10" />
    </CalcCard>
  );
}

function OTUCalc() {
  const { t } = useTranslation();
  const [ppo2, setPpo2] = useState('1.4');
  const [time, setTime] = useState('30');
  const { loading, error, result, calc } = useCalc('otu');
  return (
    <CalcCard title={t('calc.otu_title')} desc={t('calc.otu_desc')} formula={t('calc.formula_otu')}
      icon={<Activity size={16} />}
      onCalc={() => calc({ pp_o2_ata: +ppo2, time_min: +time })} loading={loading} error={error}
      resultText={result ? `${result.result} ${result.unit}` : null}>
      <Input label={t('calc.input_ppo2_ata')} type="number" value={ppo2} onChange={e => setPpo2(e.target.value)} min="0.5" max="2" step="0.05" />
      <Input label={t('calc.input_time')} type="number" value={time} onChange={e => setTime(e.target.value)} min="0" step="1" />
    </CalcCard>
  );
}

function CNSCalc() {
  const { t } = useTranslation();
  const [fo2, setFo2] = useState('0.32');
  const [depth, setDepth] = useState('30');
  const [time, setTime] = useState('30');
  const { loading, error, result, calc } = useCalc('cns');
  const r = result as { pp_o2_ata?: number; mbt_min?: number; cns_percent?: number; warning?: string } | null;
  return (
    <CalcCard title={t('calc.cns_title')} desc={t('calc.cns_desc')} formula={t('calc.formula_cns')}
      icon={<Activity size={16} />}
      onCalc={() => calc({ f_o2: +fo2, depth: +depth, time_min: +time })} loading={loading} error={error}
      resultNode={r ? (
        <div className="rounded-lg p-3 flex flex-col gap-1 text-sm" style={{ backgroundColor: 'color-mix(in srgb, var(--accent) 10%, transparent)' }}>
          <div style={{ color: 'var(--text)' }}>CNS: <b style={{ color: 'var(--accent)' }}>{r.cns_percent?.toFixed(1)} %</b></div>
          <div style={{ color: 'var(--text-muted)' }}>ppO₂: {r.pp_o2_ata?.toFixed(3)} ATA · MBT: {r.mbt_min} min</div>
          {r.warning && <div style={{ color: 'var(--warning)' }}>{r.warning}</div>}
        </div>
      ) : undefined}>
      <Input label={t('calc.input_fo2_air')} type="number" value={fo2} onChange={e => setFo2(e.target.value)} min="0" max="1" step="0.01" />
      <Input label={t('calc.input_depth')} type="number" value={depth} onChange={e => setDepth(e.target.value)} min="0" step="1" />
      <Input label={t('calc.input_time')} type="number" value={time} onChange={e => setTime(e.target.value)} min="0" step="1" />
    </CalcCard>
  );
}

function NDLCalc() {
  const { t } = useTranslation();
  const [depth, setDepth] = useState('30');
  const [fo2, setFo2] = useState('0.21');
  const { loading, error, result, calc } = useCalc('ndl');
  const r = result as { ndl_min?: number; f_o2?: number; depth?: number; depth_unit?: string } | null;
  return (
    <CalcCard title={t('calc.ndl_single_title')} desc={t('calc.ndl_single_desc')} formula={t('calc.formula_ndl')}
      icon={<Timer size={16} />}
      onCalc={() => calc({ depth: +depth, f_o2: +fo2 })} loading={loading} error={error}
      resultText={r ? (r.ndl_min != null ? `NDL: ${r.ndl_min} min` : t('calc.exceeded')) : null}>
      <Input label={t('calc.input_depth')} type="number" value={depth} onChange={e => setDepth(e.target.value)} min="0" step="1" />
      <Input label={t('calc.input_fo2_air')} type="number" value={fo2} onChange={e => setFo2(e.target.value)} min="0.18" max="1" step="0.01" />
    </CalcCard>
  );
}

function DecoStopsCalc() {
  const { t } = useTranslation();
  const [depth, setDepth] = useState('40');
  const [bottomTime, setBottomTime] = useState('25');
  const [fo2, setFo2] = useState('0.21');
  const { loading, error, result, calc } = useCalc('deco-stops');
  const r = result as { is_deco?: boolean; stops?: { stop_depth: number; minutes: number; depth_unit: string }[]; source?: string } | null;
  return (
    <CalcCard title={t('calc.deco_stops_title')} desc={t('calc.deco_stops_desc')} formula={t('calc.formula_deco')}
      icon={<Layers size={16} />}
      onCalc={() => calc({ depth: +depth, bottom_time: +bottomTime, f_o2: +fo2 })} loading={loading} error={error}
      resultNode={r ? (
        <div className="flex flex-col gap-2">
          <div className="text-sm font-medium" style={{ color: r.is_deco ? 'var(--warning)' : 'var(--success)' }}>
            {r.is_deco ? t('calc.is_deco_label') : t('calc.no_deco_label')}
          </div>
          {r.stops && r.stops.length > 0 && (
            <div className="flex flex-col gap-1 text-sm">
              {r.stops.map((s, i) => (
                <div key={i} style={{ color: 'var(--text)' }}>{s.stop_depth} {s.depth_unit}: {s.minutes} min</div>
              ))}
            </div>
          )}
          {r.source && <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{t('calc.source_label')}: {r.source}</div>}
        </div>
      ) : undefined}>
      <Input label={t('calc.input_depth')} type="number" value={depth} onChange={e => setDepth(e.target.value)} min="0" step="1" />
      <Input label={t('calc.input_bottom_time')} type="number" value={bottomTime} onChange={e => setBottomTime(e.target.value)} min="0" step="1" />
      <Input label={t('calc.input_fo2_air')} type="number" value={fo2} onChange={e => setFo2(e.target.value)} min="0.18" max="1" step="0.01" />
    </CalcCard>
  );
}

function RMVCalc() {
  const { t } = useTranslation();
  const [depth, setDepth] = useState('30');
  const [size, setSize] = useState('12');
  const [time, setTime] = useState('30');
  const [consumed, setConsumed] = useState('100');
  const { loading, error, result, calc } = useCalc('rmv');
  return (
    <CalcCard title={t('calc.rmv_title')} desc={t('calc.rmv_desc')} formula={t('calc.formula_rmv')}
      icon={<Wind size={16} />}
      onCalc={() => calc({ depth: +depth, tank_size: +size, dive_time: +time, gas_consumed: +consumed })} loading={loading} error={error}
      resultText={result ? `${result.result} ${result.unit}` : null}>
      <Input label={t('calc.input_depth')} type="number" value={depth} onChange={e => setDepth(e.target.value)} min="0" step="1" />
      <Input label={t('calc.input_size')} type="number" value={size} onChange={e => setSize(e.target.value)} min="0" step="0.5" />
      <Input label={t('calc.input_dive_time')} type="number" value={time} onChange={e => setTime(e.target.value)} min="0" step="1" />
      <Input label={t('calc.input_pressure_drop')} type="number" value={consumed} onChange={e => setConsumed(e.target.value)} min="0" step="10" />
    </CalcCard>
  );
}

function SACCalc() {
  const { t } = useTranslation();
  const [depth, setDepth] = useState('30');
  const [time, setTime] = useState('30');
  const [consumed, setConsumed] = useState('100');
  const { loading, error, result, calc } = useCalc('sac');
  return (
    <CalcCard title={t('calc.sac_calc_title')} desc={t('calc.sac_calc_desc')} formula={t('calc.formula_sac')}
      icon={<Wind size={16} />}
      onCalc={() => calc({ depth: +depth, dive_time: +time, gas_consumed: +consumed })} loading={loading} error={error}
      resultText={result ? `${result.result} ${result.unit}` : null}>
      <Input label={t('calc.input_depth')} type="number" value={depth} onChange={e => setDepth(e.target.value)} min="0" step="1" />
      <Input label={t('calc.input_dive_time')} type="number" value={time} onChange={e => setTime(e.target.value)} min="0" step="1" />
      <Input label={t('calc.input_pressure_drop')} type="number" value={consumed} onChange={e => setConsumed(e.target.value)} min="0" step="10" />
    </CalcCard>
  );
}

function ConsumedGasCalc() {
  const { t } = useTranslation();
  const [depth, setDepth] = useState('30');
  const [size, setSize] = useState('12');
  const [time, setTime] = useState('30');
  const [rmv, setRmv] = useState('25');
  const { loading, error, result, calc } = useCalc('consumed-gas');
  const r = result as { consumed_volume?: number; consumed_pressure?: number; unit_volume?: string; unit_pressure?: string } | null;
  return (
    <CalcCard title={t('calc.consumed_title')} desc={t('calc.consumed_desc')} formula={t('calc.formula_consumed')}
      icon={<Droplets size={16} />}
      onCalc={() => calc({ depth: +depth, tank_size: +size, dive_time: +time, rmv: +rmv })} loading={loading} error={error}
      resultNode={r ? (
        <div className="rounded-lg p-3 text-sm" style={{ backgroundColor: 'color-mix(in srgb, var(--accent) 10%, transparent)' }}>
          <div style={{ color: 'var(--text)' }}>{t('calc.result_volume')}: <b style={{ color: 'var(--accent)' }}>{r.consumed_volume} {r.unit_volume}</b></div>
          <div style={{ color: 'var(--text)' }}>{t('calc.result_pressure_label')}: <b style={{ color: 'var(--accent)' }}>{r.consumed_pressure} {r.unit_pressure}</b></div>
        </div>
      ) : undefined}>
      <Input label={t('calc.input_depth')} type="number" value={depth} onChange={e => setDepth(e.target.value)} min="0" step="1" />
      <Input label={t('calc.input_size')} type="number" value={size} onChange={e => setSize(e.target.value)} min="0" step="0.5" />
      <Input label={t('calc.input_dive_time')} type="number" value={time} onChange={e => setTime(e.target.value)} min="0" step="1" />
      <Input label={t('calc.input_rmv')} type="number" value={rmv} onChange={e => setRmv(e.target.value)} min="0" step="1" />
    </CalcCard>
  );
}

function RequiredGasCalc() {
  const { t } = useTranslation();
  const [depth, setDepth] = useState('30');
  const [time, setTime] = useState('30');
  const [rmv, setRmv] = useState('25');
  const { loading, error, result, calc } = useCalc('required-gas');
  return (
    <CalcCard title={t('calc.required_title')} desc={t('calc.required_desc')} formula={t('calc.formula_required')}
      icon={<Droplets size={16} />}
      onCalc={() => calc({ depth: +depth, dive_time: +time, rmv: +rmv })} loading={loading} error={error}
      resultText={result ? `${result.result} ${result.unit}` : null}>
      <Input label={t('calc.input_depth')} type="number" value={depth} onChange={e => setDepth(e.target.value)} min="0" step="1" />
      <Input label={t('calc.input_dive_time')} type="number" value={time} onChange={e => setTime(e.target.value)} min="0" step="1" />
      <Input label={t('calc.input_rmv')} type="number" value={rmv} onChange={e => setRmv(e.target.value)} min="0" step="1" />
    </CalcCard>
  );
}

function DiveTimeCalc() {
  const { t } = useTranslation();
  const [depth, setDepth] = useState('30');
  const [size, setSize] = useState('12');
  const [pressure, setPressure] = useState('150');
  const [rmv, setRmv] = useState('25');
  const { loading, error, result, calc } = useCalc('dive-time');
  return (
    <CalcCard title={t('calc.dive_time_title')} desc={t('calc.dive_time_desc')} formula={t('calc.formula_dive_time')}
      icon={<Timer size={16} />}
      onCalc={() => calc({ depth: +depth, tank_size: +size, gas_consumed: +pressure, rmv: +rmv })} loading={loading} error={error}
      resultText={result ? `${result.result} ${result.unit}` : null}>
      <Input label={t('calc.input_depth')} type="number" value={depth} onChange={e => setDepth(e.target.value)} min="0" step="1" />
      <Input label={t('calc.input_size')} type="number" value={size} onChange={e => setSize(e.target.value)} min="0" step="0.5" />
      <Input label={t('calc.input_available_pressure')} type="number" value={pressure} onChange={e => setPressure(e.target.value)} min="0" step="10" />
      <Input label={t('calc.input_rmv')} type="number" value={rmv} onChange={e => setRmv(e.target.value)} min="0" step="1" />
    </CalcCard>
  );
}

// NDL Table — full-width component with mix selector
function NDLTableCalc() {
  const { t } = useTranslation();
  const [mix, setMix] = useState('air');
  const { loading, error, result, calc } = useCalc('ndl/table');

  const mixOptions = [
    { value: 'air', label: 'AIR (21%)' },
    { value: 'ean32', label: 'EAN32 (32%)' },
    { value: 'ean34', label: 'EAN34 (34%)' },
    { value: 'ean36', label: 'EAN36 (36%)' },
    { value: 'ean38', label: 'EAN38 (38%)' },
    { value: 'ean40', label: 'EAN40 (40%)' },
  ];

  type NDLRow = { depth: number; ndl_min: number | null; depth_unit: string };
  const rows = result as NDLRow[] | null;

  return (
    <Card className="p-5 flex flex-col gap-4">
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: 'color-mix(in srgb, var(--accent) 15%, transparent)' }}>
          <Timer size={16} style={{ color: 'var(--accent)' }} />
        </div>
        <div>
          <h3 className="font-semibold text-sm" style={{ color: 'var(--text)' }}>{t('calc.ndl_full_table_title')}</h3>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{t('calc.ndl_full_table_desc')}</p>
        </div>
      </div>
      <div
        className="px-3 py-1.5 rounded text-xs font-mono"
        style={{
          backgroundColor: 'color-mix(in srgb, var(--accent) 8%, transparent)',
          color: 'var(--text-muted)',
          border: '1px solid color-mix(in srgb, var(--border) 60%, transparent)',
        }}
      >
        {t('calc.formula_ndl_table')}
      </div>
      <Select
        label={t('calc.ndl_full_table_mix')}
        value={mix}
        onChange={e => setMix(e.target.value)}
        options={mixOptions}
      />
      <Button size="sm" onClick={() => calc({ mix })} loading={loading}>{t('calc.ndl_full_table_btn')}</Button>
      {error && <p className="text-xs" style={{ color: 'var(--danger)' }}>{error}</p>}
      {rows && rows.length > 0 && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t('calc.ndl_col_depth')}</TableHead>
              <TableHead>{t('calc.ndl_col_ndl')}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row, i) => (
              <TableRow key={i}>
                <TableCell style={{ color: 'var(--text)' }}>{row.depth} {row.depth_unit}</TableCell>
                <TableCell>
                  {row.ndl_min != null
                    ? <span style={{ color: 'var(--accent)', fontWeight: 600 }}>{row.ndl_min} min</span>
                    : <span style={{ color: 'var(--danger)' }}>{t('calc.exceeded')}</span>
                  }
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </Card>
  );
}

// MAIN PAGE

export default function CalculatorsPage() {
  const { t } = useTranslation();

  return (
    <PageContainer>
      <div className="mb-8">
        <h1 className="text-3xl font-bold" style={{ color: 'var(--text)' }}>{t('planner.calc_title')}</h1>
        <p className="mt-1 text-sm" style={{ color: 'var(--text-muted)' }}>{t('planner.calc_subtitle')}</p>
      </div>

      {/* Nitrox / Gas Mix */}
      <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-muted)' }}>{t('calc.section_nitrox')}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <PPO2Calc />
        <MODCalc />
        <BestMixCalc />
        <EADCalc />
        <ENDCalc />
        <TankGasCalc />
      </div>

      {/* Gas Supply */}
      <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-muted)' }}>{t('calc.section_gas')}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <RMVCalc />
        <SACCalc />
        <ConsumedGasCalc />
        <RequiredGasCalc />
        <DiveTimeCalc />
      </div>

      {/* Physiology */}
      <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-muted)' }}>{t('calc.section_physiology')}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <OTUCalc />
        <CNSCalc />
      </div>

      {/* NDL / Deco */}
      <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-muted)' }}>{t('calc.section_ndl_deco')}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <NDLCalc />
        <DecoStopsCalc />
      </div>

      {/* NDL Table — full width */}
      <NDLTableCalc />
    </PageContainer>
  );
}
