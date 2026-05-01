import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  BookOpen, Calculator, BarChart2, Wrench, Waves,
  ArrowRight, CheckCircle, Wind, Activity, Package
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { useAuth } from '../contexts/AuthContext';

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  desc: string;
  accent?: string;
}

function FeatureCard({ icon, title, desc, accent = 'var(--accent)' }: FeatureCardProps) {
  return (
    <Card hover className="flex flex-col gap-4 p-6">
      <div
        className="w-12 h-12 rounded-xl flex items-center justify-center"
        style={{ backgroundColor: `color-mix(in srgb, ${accent} 15%, transparent)` }}
      >
        <span style={{ color: accent }}>{icon}</span>
      </div>
      <div>
        <h3 className="font-semibold text-base mb-1" style={{ color: 'var(--text)' }}>{title}</h3>
        <p className="text-sm leading-relaxed" style={{ color: 'var(--text-muted)' }}>{desc}</p>
      </div>
    </Card>
  );
}

function StatBubble({ value, label }: { value: string; label: string }) {
  return (
    <div className="text-center">
      <p className="text-3xl font-bold" style={{ color: 'var(--accent)' }}>{value}</p>
      <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>{label}</p>
    </div>
  );
}

export default function HomePage() {
  const { t } = useTranslation();
  const { user } = useAuth();

  const features = [
    { icon: <Calculator size={22} />, title: t('home.feat_planner_title'), desc: t('home.feat_planner_desc'), accent: 'var(--accent)' },
    { icon: <Activity size={22} />, title: t('home.feat_calc_title'), desc: t('home.feat_calc_desc'), accent: 'var(--accent2)' },
    { icon: <BookOpen size={22} />, title: t('home.feat_dives_title'), desc: t('home.feat_dives_desc'), accent: 'var(--accent)' },
    { icon: <Wind size={22} />, title: t('home.feat_gas_title'), desc: t('home.feat_gas_desc'), accent: 'var(--accent2)' },
    { icon: <Wrench size={22} />, title: t('home.feat_equipment_title'), desc: t('home.feat_equipment_desc'), accent: 'var(--accent)' },
    { icon: <BarChart2 size={22} />, title: t('home.feat_stats_title'), desc: t('home.feat_stats_desc'), accent: 'var(--accent2)' },
  ];

  const perks = [
    t('home.perk_free'),
    t('home.perk_browser'),
    t('home.perk_planner_free'),
    t('home.perk_multilevel'),
    t('home.perk_units'),
    t('home.perk_languages'),
  ];

  return (
    <div style={{ backgroundColor: 'var(--bg)' }}>

      {/* HERO */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none" style={{
          background: 'radial-gradient(ellipse 80% 60% at 50% -10%, color-mix(in srgb, var(--accent) 18%, transparent), transparent)',
        }} />
        <div className="absolute top-20 right-10 w-64 h-64 rounded-full pointer-events-none" style={{
          background: 'radial-gradient(circle, color-mix(in srgb, var(--accent2) 12%, transparent), transparent)',
          filter: 'blur(40px)',
        }} />

        <div className="max-w-[1200px] mx-auto px-4 py-20 sm:py-32 relative">
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium mb-8" style={{
              backgroundColor: 'color-mix(in srgb, var(--accent) 15%, transparent)',
              color: 'var(--accent)',
              border: '1px solid color-mix(in srgb, var(--accent) 30%, transparent)',
            }}>
              <img src="/blue_dragon_outline.svg" alt="" style={{ height: '16px', width: 'auto' }} />
              {t('home.badge_text')}
            </div>

            <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight mb-6">
              <span style={{ color: 'var(--text)' }}>Dive</span>
              <span style={{ color: 'var(--accent)' }}>Plan</span>
              <span style={{ color: 'var(--accent2)' }}>Web</span>
            </h1>

            <p className="text-lg sm:text-xl mb-4 font-medium" style={{ color: 'var(--text)' }}>
              {t('home.hero_subtitle')}
            </p>
            <p className="text-base sm:text-lg mb-10 leading-relaxed" style={{ color: 'var(--text-muted)' }}>
              {t('home.hero_desc')}
            </p>

            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link to="/planner/plan">
                <Button size="lg" className="gap-2 shadow-lg">
                  <Waves size={18} />
                  {t('home.hero_cta_plan')}
                  <ArrowRight size={16} />
                </Button>
              </Link>
              {user ? (
                <Link to="/dives">
                  <Button size="lg" variant="outline" className="gap-2">
                    <BookOpen size={18} />
                    {t('nav.dives')}
                  </Button>
                </Link>
              ) : (
                <Link to="/register">
                  <Button size="lg" variant="outline" className="gap-2">
                    {t('home.hero_cta_register')}
                  </Button>
                </Link>
              )}
            </div>
          </div>

          {/* Stats bar */}
          <div className="mt-20 p-6 rounded-2xl grid grid-cols-2 sm:grid-cols-4 gap-8 max-w-2xl mx-auto" style={{
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border)',
            boxShadow: 'var(--shadow)',
          }}>
            <StatBubble value="∞" label={t('home.stat_dives')} />
            <StatBubble value="NDL+" label={t('home.stat_ndl')} />
            <StatBubble value="2" label={t('home.stat_languages')} />
            <StatBubble value="3" label={t('home.stat_themes')} />
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="py-20 px-4" style={{ backgroundColor: 'var(--bg-muted)' }}>
        <div className="max-w-[1200px] mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4" style={{ color: 'var(--text)' }}>
              {t('home.features_title')}
            </h2>
            <p className="text-lg max-w-xl mx-auto" style={{ color: 'var(--text-muted)' }}>
              {t('home.features_desc')}
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f, i) => <FeatureCard key={i} {...f} />)}
          </div>
        </div>
      </section>

      {/* WHY section */}
      <section className="py-20 px-4">
        <div className="max-w-[1200px] mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-4" style={{ color: 'var(--text)' }}>
                {t('home.why_title')}
              </h2>
              <p className="text-lg mb-8" style={{ color: 'var(--text-muted)' }}>
                {t('home.why_desc')}
              </p>
              <ul className="space-y-4">
                {perks.map((perk, i) => (
                  <li key={i} className="flex items-center gap-3">
                    <CheckCircle size={20} style={{ color: 'var(--success)', flexShrink: 0 }} />
                    <span className="text-sm" style={{ color: 'var(--text)' }}>{perk}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Dive profile diagram */}
            <div className="card p-6 rounded-2xl" style={{ boxShadow: 'var(--shadow)' }}>
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-semibold" style={{ color: 'var(--text-muted)' }}>
                  {t('nav.planner_plan')}
                </span>
                <span className="badge text-xs" style={{
                  backgroundColor: 'color-mix(in srgb, var(--success) 20%, transparent)',
                  color: 'var(--success)',
                }}>NDL</span>
              </div>
              <svg viewBox="0 0 300 160" className="w-full">
                {[40, 80, 120].map(y => (
                  <line key={y} x1="30" y1={y} x2="290" y2={y} stroke="var(--border)" strokeWidth="1" strokeDasharray="4,4" />
                ))}
                <text x="5" y="44" fill="var(--text-subtle)" fontSize="9">10m</text>
                <text x="5" y="84" fill="var(--text-subtle)" fontSize="9">20m</text>
                <text x="5" y="124" fill="var(--text-subtle)" fontSize="9">30m</text>
                <polygon
                  points="30,10 80,120 180,120 220,60 250,60 280,10 280,155 30,155"
                  fill="color-mix(in srgb, var(--accent) 10%, transparent)"
                />
                <polyline
                  points="30,10 80,120 180,120 220,60 250,60 280,10"
                  fill="none" stroke="var(--accent)" strokeWidth="2.5" strokeLinejoin="round"
                />
                {[[30,10],[80,120],[180,120],[220,60],[250,60],[280,10]].map(([x,y], i) => (
                  <circle key={i} cx={x} cy={y} r="4" fill="var(--accent)" />
                ))}
              </svg>
              <div className="grid grid-cols-3 gap-4 mt-4 pt-4" style={{ borderTop: '1px solid var(--border)' }}>
                {[{ label: t('home.chart_label_max'), value: '30 m' }, { label: t('home.chart_label_time'), value: '47 min' }, { label: t('home.chart_label_ndl'), value: '12 min' }].map((s) => (
                  <div key={s.label} className="text-center">
                    <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{s.label}</p>
                    <p className="text-base font-bold" style={{ color: 'var(--accent)' }}>{s.value}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      {!user && (
        <section className="py-20 px-4" style={{ backgroundColor: 'var(--bg-muted)' }}>
          <div className="max-w-2xl mx-auto text-center">
            <Package size={40} className="mx-auto mb-6" style={{ color: 'var(--accent)' }} />
            <h2 className="text-3xl sm:text-4xl font-bold mb-4" style={{ color: 'var(--text)' }}>
              {t('home.cta_title')}
            </h2>
            <p className="text-lg mb-8" style={{ color: 'var(--text-muted)' }}>
              {t('home.cta_desc')}
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link to="/register">
                <Button size="lg" className="gap-2">
                  {t('home.cta_button')}
                  <ArrowRight size={16} />
                </Button>
              </Link>
              <Link to="/login">
                <Button size="lg" variant="ghost">{t('nav.login')}</Button>
              </Link>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
