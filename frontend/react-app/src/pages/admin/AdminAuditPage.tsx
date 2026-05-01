import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FileText } from 'lucide-react';
import { Card } from '../../components/ui/card';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, EmptyTableRow } from '../../components/ui/table';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';

interface AuditLog {
  audit_id: number;
  user_id: number | null;
  action: string;
  entity: string | null;
  entity_id: number | null;
  created_at: string;
}

export default function AdminAuditPage() {
  const { t } = useTranslation();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/audit-logs/')
      .then((r) => setLogs(r.data))
      .catch(() => setError(t('common.error')))
      .finally(() => setLoading(false));
  }, []);

  return (
    <PageContainer>
      <h1 className="text-3xl font-bold mb-8 flex items-center gap-3" style={{ color: 'var(--text)' }}>
        <FileText style={{ color: 'var(--accent)' }} size={28} />
        {t('admin.audit_title')}
      </h1>
      {error && <p style={{ color: 'var(--danger)' }}>{error}</p>}
      {loading ? (
        <p style={{ color: 'var(--text-muted)' }}>{t('common.loading')}</p>
      ) : (
        <Card className="p-0 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>User ID</TableHead>
                <TableHead>{t('admin.col_action')}</TableHead>
                <TableHead>{t('admin.col_entity')}</TableHead>
                <TableHead>{t('admin.col_time')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {logs.length === 0 ? (
                <EmptyTableRow colSpan={5} message={t('admin.no_logs')} />
              ) : (
                logs.map((l) => (
                  <TableRow key={l.audit_id}>
                    <TableCell style={{ color: 'var(--text-muted)' }}>{l.audit_id}</TableCell>
                    <TableCell>{l.user_id ?? '—'}</TableCell>
                    <TableCell className="font-medium">{l.action}</TableCell>
                    <TableCell style={{ color: 'var(--text-muted)' }}>{l.entity ?? '—'} {l.entity_id ? `#${l.entity_id}` : ''}</TableCell>
                    <TableCell style={{ color: 'var(--text-muted)' }}>{l.created_at}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </Card>
      )}
    </PageContainer>
  );
}
