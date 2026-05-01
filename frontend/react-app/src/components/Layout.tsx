import { Outlet, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Navbar } from './Navbar';

export function Layout() {
  const { t } = useTranslation();
  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: 'var(--bg)', color: 'var(--text)' }}>
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <footer
        className="border-t py-6 px-4"
        style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
      >
        <div className="max-w-[1400px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2" style={{ color: 'var(--text-muted)' }}>
            <img src="/blue_dragon_outline.svg" alt="" style={{ height: '18px', width: 'auto' }} />
            <span className="text-sm font-medium">DivePlanWeb</span>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/terms" className="text-xs hover:underline" style={{ color: 'var(--text-subtle)' }}>
              {t('common.terms_of_use')}
            </Link>
            <Link to="/privacy" className="text-xs hover:underline" style={{ color: 'var(--text-subtle)' }}>
              {t('common.privacy_policy')}
            </Link>
            <p className="text-xs" style={{ color: 'var(--text-subtle)' }}>
              © {new Date().getFullYear()} DivePlanWeb
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export function PageContainer({
  children,
  className = '',
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`max-w-[1400px] mx-auto px-4 py-8 ${className}`}>
      {children}
    </div>
  );
}
