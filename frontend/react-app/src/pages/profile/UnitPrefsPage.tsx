import { useState, useEffect, FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Sliders } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Select } from '../../components/ui/input';
import { Button } from '../../components/ui/button';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';

interface Prefs {
  depth: string;
  pressure: string;
  temperature: string;
  volume: string;
}

export default function UnitPrefsPage() {
  const { t } = useTranslation();
  const [prefs, setPrefs] = useState<Prefs>({ depth: 'm', pressure: 'bar', temperature: '°C', volume: 'l' });
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/unit-prefs/me').then((r) => {
      const d = r.data;
      setPrefs({
        depth: d.depth ?? 'm',
        pressure: d.pressure ?? 'bar',
        temperature: d.temperature ?? '°C',
        volume: d.volume ?? 'l',
      });
    }).catch(() => {});
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await api.patch('/unit-prefs/me', {
        depth: prefs.depth,
        pressure: prefs.pressure,
        temperature: prefs.temperature,
        volume: prefs.volume,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch {
      setError(t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const set = (field: keyof Prefs) => (e: React.ChangeEvent<HTMLSelectElement>) =>
    setPrefs((p) => ({ ...p, [field]: e.target.value }));

  return (
    <PageContainer>
      <h1 className="text-3xl font-bold mb-8 flex items-center gap-3" style={{ color: 'var(--text)' }}>
        <Sliders style={{ color: 'var(--accent)' }} size={28} />
        {t('unit_prefs.title')}
      </h1>
      <Card className="max-w-md">
        <CardHeader><CardTitle>{t('unit_prefs.title')}</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Select
              label={t('unit_prefs.depth')}
              value={prefs.depth}
              onChange={set('depth')}
              options={[{ value: 'm', label: 'Metry (m)' }, { value: 'ft', label: 'Stopy (ft)' }]}
            />
            <Select
              label={t('unit_prefs.pressure')}
              value={prefs.pressure}
              onChange={set('pressure')}
              options={[{ value: 'bar', label: 'Bar' }, { value: 'psi', label: 'PSI' }]}
            />
            <Select
              label={t('unit_prefs.temperature')}
              value={prefs.temperature}
              onChange={set('temperature')}
              options={[{ value: '°C', label: 'Celsius (°C)' }, { value: '°F', label: 'Fahrenheit (°F)' }]}
            />
            <Select
              label={t('unit_prefs.volume')}
              value={prefs.volume}
              onChange={set('volume')}
              options={[{ value: 'l', label: 'Litry (l)' }, { value: 'cuft', label: 'Cubic feet (cuft)' }]}
            />
            {error && <p className="text-sm" style={{ color: 'var(--danger)' }}>{error}</p>}
            {saved && <p className="text-sm" style={{ color: 'var(--success)' }}>{t('unit_prefs.saved')}</p>}
            <Button type="submit" loading={loading}>{t('unit_prefs.save')}</Button>
          </form>
        </CardContent>
      </Card>
    </PageContainer>
  );
}
