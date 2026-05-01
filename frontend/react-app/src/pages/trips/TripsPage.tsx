import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Compass, Plus } from 'lucide-react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input, Textarea } from '../../components/ui/input';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, EmptyTableRow } from '../../components/ui/table';
import { Dialog, DialogHeader, DialogContent, DialogFooter } from '../../components/ui/dialog';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';

interface Trip {
  trip_id: number;
  title: string | null;
  start_date: string | null;
  end_date: string | null;
  notes: string | null;
}

const emptyForm = () => ({ title: '', start_date: '', end_date: '', notes: '' });

export default function TripsPage() {
  const { t } = useTranslation();
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [editItem, setEditItem] = useState<Trip | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyForm());
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');

  useEffect(() => { load(); }, []);

  const load = () => {
    setLoading(true);
    api.get('/trips/').then(r => setTrips(r.data)).catch(() => setError(t('common.error'))).finally(() => setLoading(false));
  };

  const openCreate = () => { setEditItem(null); setForm(emptyForm()); setFormError(''); setShowDialog(true); };
  const openEdit = (trip: Trip) => {
    setEditItem(trip);
    setForm({ title: trip.title || '', start_date: trip.start_date || '', end_date: trip.end_date || '', notes: trip.notes || '' });
    setFormError(''); setShowDialog(true);
  };
  const closeDialog = () => { setShowDialog(false); setEditItem(null); };

  const buildPayload = () => ({
    title: form.title || null,
    start_date: form.start_date || null,
    end_date: form.end_date || null,
    notes: form.notes || null,
  });

  const handleSave = async () => {
    setSaving(true); setFormError('');
    try {
      if (editItem) {
        const r = await api.patch(`/trips/${editItem.trip_id}`, buildPayload());
        setTrips(prev => prev.map(trip => trip.trip_id === editItem.trip_id ? r.data : trip));
      } else {
        const r = await api.post('/trips/', buildPayload());
        setTrips(prev => [...prev, r.data]);
      }
      closeDialog();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      setFormError(err.response?.data?.message || t('common.error'));
    } finally { setSaving(false); }
  };

  const handleDelete = async (id: number) => {
    try { await api.delete(`/trips/${id}`); setTrips(prev => prev.filter(trip => trip.trip_id !== id)); }
    catch { setError(t('common.error')); }
    setDeleteId(null);
  };

  const upd = (k: string, v: string) => setForm(prev => ({ ...prev, [k]: v }));

  return (
    <PageContainer>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3" style={{ color: 'var(--text)' }}>
          <Compass style={{ color: 'var(--accent)' }} size={28} />
          {t('trips.title')}
        </h1>
        <Button onClick={openCreate}><Plus size={16} /> {t('trips.new')}</Button>
      </div>

      {error && <p className="mb-4" style={{ color: 'var(--danger)' }}>{error}</p>}
      {loading ? <p style={{ color: 'var(--text-muted)' }}>{t('common.loading')}</p> : (
        <Card className="p-0 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('trips.col_name')}</TableHead>
                <TableHead>{t('trips.col_start')}</TableHead>
                <TableHead>{t('trips.col_end')}</TableHead>
                <TableHead>{t('common.actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {trips.length === 0 ? (
                <EmptyTableRow colSpan={4} message={t('trips.no_trips')} />
              ) : trips.map(trip => (
                <TableRow key={trip.trip_id}>
                  <TableCell className="font-medium" style={{ color: 'var(--text)' }}>{trip.title || '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{trip.start_date || '—'}</TableCell>
                  <TableCell style={{ color: 'var(--text-muted)' }}>{trip.end_date || '—'}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => openEdit(trip)}>{t('common.edit')}</Button>
                      <Button size="sm" variant="danger" onClick={() => setDeleteId(trip.trip_id)}>{t('common.delete')}</Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}

      <Dialog open={showDialog} onClose={closeDialog} size="md">
        <DialogHeader title={editItem ? t('trips.edit') : t('trips.new')} onClose={closeDialog} />
        <DialogContent>
          {formError && <p className="mb-4 text-sm" style={{ color: 'var(--danger)' }}>{formError}</p>}
          <div className="flex flex-col gap-4">
            <Input label={t('trips.field_name')} value={form.title} onChange={e => upd('title', e.target.value)} />
            <div className="grid grid-cols-2 gap-4">
              <Input label={t('trips.field_start_date')} type="date" value={form.start_date} onChange={e => upd('start_date', e.target.value)} />
              <Input label={t('trips.field_end_date')} type="date" value={form.end_date} onChange={e => upd('end_date', e.target.value)} />
            </div>
            <Textarea label={t('trips.field_notes')} value={form.notes} onChange={e => upd('notes', e.target.value)} rows={3} />
          </div>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={closeDialog}>{t('common.cancel')}</Button>
          <Button loading={saving} onClick={handleSave}>{t('common.save')}</Button>
        </DialogFooter>
      </Dialog>

      <Dialog open={deleteId !== null} onClose={() => setDeleteId(null)} size="sm">
        <DialogHeader title={t('common.delete')} onClose={() => setDeleteId(null)} />
        <DialogContent><p style={{ color: 'var(--text)' }}>{t('trips.delete_confirm')}</p></DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setDeleteId(null)}>{t('common.cancel')}</Button>
          <Button variant="danger" onClick={() => handleDelete(deleteId!)}>{t('common.delete')}</Button>
        </DialogFooter>
      </Dialog>
    </PageContainer>
  );
}
