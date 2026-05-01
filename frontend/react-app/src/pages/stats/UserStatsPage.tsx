import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { TrendingUp, Waves, Clock, ArrowDown, MapPin, Flame } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';
import { fmt, fmtDuration } from '../../lib/utils';

// TYPES

interface BasicStats {
  dives_count?: number;
  total_duration_min?: number;
  avg_duration_min?: number;
  max_depth_m?: number;
  avg_depth_m?: number;
  avg_temp_c?: number;
}
interface TopSite { site_name: string; dives: number; }
interface RecentDive { id: number; start_time?: string; duration_min?: number; max_depth_m?: number; site?: string; }
interface DeepDive { id: number; start_time?: string; max_depth_m?: number; duration_min?: number; site?: string; }
interface UserOverview { basic?: BasicStats; top_sites?: TopSite[]; recent_dives?: RecentDive[]; top_deep_dives?: DeepDive[]; }

interface GasMixStat { name?: string; gas_type: string; o2_percent?: number; he_percent?: number; uses: number; }
interface TankStat { volume_l?: number; work_pressure_bar?: number; material?: string; uses: number; }
interface TagStat { name: string; uses: number; }
interface EventStat { type: string; uses: number; }
interface CircuitStat { breathing_system: string; dives: number; }
interface LicenseStat { agency?: string; certification?: string; dives: number; }
interface CountryStat { country: string; dives: number; }
interface RegionStat { region: string; dives: number; }

// HELPERS

type TabId = 'overview' | 'gas' | 'tanks' | 'tags' | 'events' | 'circuits' | 'licenses' | 'countries' | 'regions';

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <Card className="flex flex-col gap-3 p-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: 'color-mix(in srgb, var(--accent2) 15%, transparent)' }}>
          <span style={{ color: 'var(--accent2)' }}>{icon}</span>
        </div>
        <span className="text-sm font-medium" style={{ color: 'var(--text-muted)' }}>{label}</span>
      </div>
      <p className="text-3xl font-bold" style={{ color: 'var(--text)' }}>{value}</p>
    </Card>
  );
}

function RankTable({ rows }: { rows: { label: string; value: string | number }[] }) {
  return (
    <div className="divide-y" style={{ borderColor: 'var(--border-muted)' }}>
      {rows.map((r, i) => (
        <div key={i} className="flex items-center justify-between py-2 text-sm">
          <span style={{ color: 'var(--text)' }}>{r.label}</span>
          <span className="font-semibold" style={{ color: 'var(--accent2)' }}>{r.value}</span>
        </div>
      ))}
    </div>
  );
}

// PAGE

export default function UserStatsPage() {
  const { t } = useTranslation();
  const [tab, setTab] = useState<TabId>('overview');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [overview, setOverview] = useState<UserOverview | null>(null);
  const [gas, setGas] = useState<GasMixStat[] | null>(null);
  const [tanks, setTanks] = useState<TankStat[] | null>(null);
  const [tags, setTags] = useState<TagStat[] | null>(null);
  const [events, setEvents] = useState<EventStat[] | null>(null);
  const [circuits, setCircuits] = useState<CircuitStat[] | null>(null);
  const [licenses, setLicenses] = useState<LicenseStat[] | null>(null);
  const [countries, setCountries] = useState<CountryStat[] | null>(null);
  const [regions, setRegions] = useState<RegionStat[] | null>(null);

  const TABS = useMemo(() => [
    { id: 'overview' as TabId,  label: t('stats.tab_overview') },
    { id: 'gas' as TabId,       label: t('stats.tab_gas') },
    { id: 'tanks' as TabId,     label: t('stats.tab_tanks') },
    { id: 'tags' as TabId,      label: t('stats.tab_tags') },
    { id: 'events' as TabId,    label: t('stats.tab_events') },
    { id: 'circuits' as TabId,  label: t('stats.tab_circuits') },
    { id: 'licenses' as TabId,  label: t('stats.tab_licenses') },
    { id: 'countries' as TabId, label: t('stats.tab_countries') },
    { id: 'regions' as TabId,   label: t('stats.tab_regions') },
  ], [t]);

  useEffect(() => {
    setLoading(true);
    setError('');

    const endpoints: Record<TabId, string> = {
      overview:  '/user-stats/',
      gas:       '/user-stats/gas-mix',
      tanks:     '/user-stats/tanks',
      tags:      '/user-stats/tags',
      events:    '/user-stats/events',
      circuits:  '/user-stats/circuits',
      licenses:  '/user-stats/licenses',
      countries: '/user-stats/countries',
      regions:   '/user-stats/regions',
    };

    api.get(endpoints[tab])
      .then((r) => {
        if (tab === 'overview')  setOverview(r.data);
        if (tab === 'gas')       setGas(r.data.items);
        if (tab === 'tanks')     setTanks(r.data.items);
        if (tab === 'tags')      setTags(r.data.items);
        if (tab === 'events')    setEvents(r.data.items);
        if (tab === 'circuits')  setCircuits(r.data.items);
        if (tab === 'licenses')  setLicenses(r.data.items);
        if (tab === 'countries') setCountries(r.data.items);
        if (tab === 'regions')   setRegions(r.data.items);
      })
      .catch(() => setError(t('stats.error')))
      .finally(() => setLoading(false));
  }, [tab, t]);

  const b = overview?.basic;

  const tabDataMap: Record<string, unknown[] | null> = { gas, tanks, tags, events, circuits, licenses, countries, regions };
  const currentTabEmpty = tab !== 'overview' && !loading && !error && Array.isArray(tabDataMap[tab]) && (tabDataMap[tab] as unknown[]).length === 0;

  return (
    <PageContainer>
      <div className="mb-6">
        <h1 className="text-3xl font-bold flex items-center gap-3" style={{ color: 'var(--text)' }}>
          <TrendingUp style={{ color: 'var(--accent2)' }} size={28} />
          {t('stats.user_title')}
        </h1>
        <p className="mt-1 text-sm" style={{ color: 'var(--text-muted)' }}>
          {t('stats.user_subtitle')}
        </p>
      </div>

      {/* Tab bar */}
      <div className="flex flex-wrap gap-1 mb-6 p-1 rounded-xl" style={{ backgroundColor: 'var(--bg-subtle)' }}>
        {TABS.map((tb) => (
          <button
            key={tb.id}
            onClick={() => setTab(tb.id)}
            className="px-3 py-1.5 rounded-lg text-sm font-medium transition-all"
            style={tab === tb.id ? {
              backgroundColor: 'var(--bg-card)',
              color: 'var(--accent2)',
              boxShadow: 'var(--shadow-sm)',
            } : { color: 'var(--text-muted)' }}
          >
            {tb.label}
          </button>
        ))}
      </div>

      {loading && <p style={{ color: 'var(--text-muted)' }}>{t('stats.loading')}</p>}
      {error && <p style={{ color: 'var(--danger)' }}>{error}</p>}

      {/* Overview tab */}
      {tab === 'overview' && b && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <StatCard icon={<Waves size={20} />}     label={t('stats.total_dives')}  value={String(b.dives_count ?? 0)} />
            <StatCard icon={<Clock size={20} />}     label={t('stats.total_time')}   value={fmtDuration(b.total_duration_min)} />
            <StatCard icon={<ArrowDown size={20} />} label={t('stats.max_depth')}    value={`${fmt(b.max_depth_m as number)} m`} />
            <StatCard icon={<ArrowDown size={20} />} label={t('stats.avg_depth')}    value={`${fmt(b.avg_depth_m as number)} m`} />
            <StatCard icon={<Clock size={20} />}     label={t('stats.avg_duration')} value={fmtDuration(b.avg_duration_min)} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {overview?.top_sites && overview.top_sites.length > 0 && (
              <Card>
                <CardHeader><CardTitle className="flex items-center gap-2"><MapPin size={16} /> {t('stats.top_sites')}</CardTitle></CardHeader>
                <CardContent>
                  <RankTable rows={overview.top_sites.map((s) => ({ label: s.site_name, value: `${s.dives} ${t('stats.dives_suffix')}` }))} />
                </CardContent>
              </Card>
            )}
            {overview?.top_deep_dives && overview.top_deep_dives.length > 0 && (
              <Card>
                <CardHeader><CardTitle className="flex items-center gap-2"><Flame size={16} /> {t('stats.top_deep')}</CardTitle></CardHeader>
                <CardContent>
                  <RankTable rows={overview.top_deep_dives.map((d) => ({
                    label: `#${d.id}${d.site ? ` — ${d.site}` : ''}`,
                    value: `${fmt(d.max_depth_m as number)} m`,
                  }))} />
                </CardContent>
              </Card>
            )}
            {overview?.recent_dives && overview.recent_dives.length > 0 && (
              <Card>
                <CardHeader><CardTitle>{t('stats.recent_dives')}</CardTitle></CardHeader>
                <CardContent>
                  <RankTable rows={overview.recent_dives.map((d) => ({
                    label: `#${d.id}${d.site ? ` — ${d.site}` : ''}`,
                    value: `${fmt(d.max_depth_m as number)} m / ${fmtDuration(d.duration_min)}`,
                  }))} />
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}

      {tab === 'gas' && gas && (
        <Card>
          <CardHeader><CardTitle>{t('stats.tab_gas')}</CardTitle></CardHeader>
          <CardContent>
            <RankTable rows={gas.map((g) => ({
              label: g.name || `${g.gas_type} O₂:${g.o2_percent ?? '?'}%`,
              value: `${g.uses}×`,
            }))} />
          </CardContent>
        </Card>
      )}

      {tab === 'tanks' && tanks && (
        <Card>
          <CardHeader><CardTitle>{t('stats.tab_tanks')}</CardTitle></CardHeader>
          <CardContent>
            <RankTable rows={tanks.map((tk) => ({
              label: `${tk.volume_l ?? '?'} l / ${tk.work_pressure_bar ?? '?'} bar${tk.material ? ` (${tk.material})` : ''}`,
              value: `${tk.uses}×`,
            }))} />
          </CardContent>
        </Card>
      )}

      {tab === 'tags' && tags && (
        <Card>
          <CardHeader><CardTitle>{t('stats.tab_tags')}</CardTitle></CardHeader>
          <CardContent>
            <RankTable rows={tags.map((tg) => ({ label: tg.name, value: `${tg.uses}×` }))} />
          </CardContent>
        </Card>
      )}

      {tab === 'events' && events && (
        <Card>
          <CardHeader><CardTitle>{t('stats.tab_events')}</CardTitle></CardHeader>
          <CardContent>
            <RankTable rows={events.map((ev) => ({ label: ev.type, value: `${ev.uses}×` }))} />
          </CardContent>
        </Card>
      )}

      {tab === 'circuits' && circuits && (
        <Card>
          <CardHeader><CardTitle>{t('stats.tab_circuits')}</CardTitle></CardHeader>
          <CardContent>
            <RankTable rows={circuits.map((c) => ({ label: c.breathing_system, value: `${c.dives} ${t('stats.dives_suffix')}` }))} />
          </CardContent>
        </Card>
      )}

      {tab === 'licenses' && licenses && (
        <Card>
          <CardHeader><CardTitle>{t('stats.tab_licenses')}</CardTitle></CardHeader>
          <CardContent>
            <RankTable rows={licenses.map((l) => ({
              label: [l.agency, l.certification].filter(Boolean).join(' — ') || t('stats.unknown'),
              value: `${l.dives} ${t('stats.dives_suffix')}`,
            }))} />
          </CardContent>
        </Card>
      )}

      {tab === 'countries' && countries && (
        <Card>
          <CardHeader><CardTitle>{t('stats.tab_countries')}</CardTitle></CardHeader>
          <CardContent>
            <RankTable rows={countries.map((c) => ({ label: c.country, value: `${c.dives} ${t('stats.dives_suffix')}` }))} />
          </CardContent>
        </Card>
      )}

      {tab === 'regions' && regions && (
        <Card>
          <CardHeader><CardTitle>{t('stats.tab_regions')}</CardTitle></CardHeader>
          <CardContent>
            <RankTable rows={regions.map((r) => ({ label: r.region, value: `${r.dives} ${t('stats.dives_suffix')}` }))} />
          </CardContent>
        </Card>
      )}

      {currentTabEmpty && (
        <p style={{ color: 'var(--text-muted)' }}>{t('stats.no_data')}</p>
      )}
    </PageContainer>
  );
}
