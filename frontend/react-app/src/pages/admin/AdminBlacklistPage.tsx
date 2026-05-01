import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Ban } from 'lucide-react';
import { Card } from '../../components/ui/card';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, EmptyTableRow } from '../../components/ui/table';
import { PageContainer } from '../../components/Layout';
import api from '../../lib/api';

interface BlacklistToken {
  id: number;
  jti: string;
  created_at: string;
}

export default function AdminBlacklistPage() {
  const { t } = useTranslation();
  const [tokens, setTokens] = useState<BlacklistToken[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/token-blacklist/')
      .then((r) => setTokens(r.data))
      .catch(() => setError(t('common.error')))
      .finally(() => setLoading(false));
  }, []);

  return (
    <PageContainer>
      <h1 className="text-3xl font-bold mb-8 flex items-center gap-3" style={{ color: 'var(--text)' }}>
        <Ban style={{ color: 'var(--danger)' }} size={28} />
        {t('admin.blacklist_title')}
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
                <TableHead>{t('admin.col_jti')}</TableHead>
                <TableHead>{t('admin.col_created')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tokens.length === 0 ? (
                <EmptyTableRow colSpan={3} message={t('admin.no_tokens')} />
              ) : (
                tokens.map((tk) => (
                  <TableRow key={tk.id}>
                    <TableCell>{tk.id}</TableCell>
                    <TableCell className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>{tk.jti}</TableCell>
                    <TableCell style={{ color: 'var(--text-muted)' }}>{tk.created_at}</TableCell>
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
