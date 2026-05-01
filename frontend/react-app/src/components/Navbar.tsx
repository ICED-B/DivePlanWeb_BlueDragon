import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { useTheme, Theme } from '../contexts/ThemeContext';
import { NavDropdown, DropdownItem, DropdownSeparator } from './ui/dropdown';
import {
  Calculator, Map, BookOpen, BarChart2, User, Shield,
  Sun, Moon, LogOut, Lock, Sliders,
  Waves, Package, Wrench, Cpu, Users, FileText,
  Ban, Globe, TrendingUp, Dices, FolderOpen, Tag, Award
} from 'lucide-react';

const THEMES: { value: Theme; labelKey: string; icon: React.ReactNode }[] = [
  { value: 'ocean', labelKey: 'theme.ocean', icon: <Waves size={14} /> },
  { value: 'light', labelKey: 'theme.light', icon: <Sun size={14} /> },
  { value: 'gray',  labelKey: 'theme.gray',  icon: <Moon size={14} /> },
];

const LANGS = [
  { code: 'cs', label: '🇨🇿 Čeština' },
  { code: 'en', label: '🇬🇧 English' },
];

export function Navbar() {
  const { t, i18n } = useTranslation();
  const { user, isAdmin, logout } = useAuth();
  const { theme, setTheme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      const token = sessionStorage.getItem('access_token');
      if (token) {
        await fetch('/api/v1/auth/logout', {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        });
      }
    } catch { /* ignore */ }
    logout();
    navigate('/login');
  };

  const currentThemeIcon = theme === 'light' ? <Sun size={16} /> : theme === 'gray' ? <Moon size={16} /> : <Waves size={16} />;

  return (
    <header
      className="sticky top-0 z-40 border-b"
      style={{
        backgroundColor: 'var(--bg-card)',
        borderColor: 'var(--border)',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      <div className="max-w-[1400px] mx-auto px-4 h-14 flex items-center gap-2">

        {/* Logo */}
        <Link
          to="/"
          className="flex items-center gap-2 mr-4 font-bold text-lg flex-shrink-0"
          style={{ color: 'var(--accent)' }}
        >
          <img src="/blue_dragon_outline.svg" alt="logo" className="flex-shrink-0" style={{ height: '32px', width: 'auto' }} />
          <span className="hidden sm:block">DivePlanWeb</span>
        </Link>

        {/* Main nav */}
        <nav className="flex items-center gap-1 flex-1 overflow-x-auto">

          {/* Planner — public */}
          <NavDropdown label={t('nav.planner')} icon={<Calculator size={15} />}>
            <DropdownItem icon={<Dices size={14} />} onClick={() => navigate('/planner/calculators')}>
              {t('nav.planner_calculators')}
            </DropdownItem>
            <DropdownItem icon={<BookOpen size={14} />} onClick={() => navigate('/planner/plan')}>
              {t('nav.planner_plan')}
            </DropdownItem>
          </NavDropdown>

          {/* Stats — public */}
          <NavDropdown label={t('nav.stats')} icon={<BarChart2 size={15} />}>
            <DropdownItem icon={<TrendingUp size={14} />} onClick={() => navigate('/stats/global')}>
              {t('nav.stats_global')}
            </DropdownItem>
            {user && (
              <DropdownItem icon={<BarChart2 size={14} />} onClick={() => navigate('/stats/user')}>
                {t('nav.stats_user')}
              </DropdownItem>
            )}
          </NavDropdown>

          {/* Records — only logged in */}
          {user && (
            <NavDropdown label={t('nav.records')} icon={<FolderOpen size={15} />}>
              <DropdownItem icon={<Map size={14} />} onClick={() => navigate('/sites')}>
                {t('nav.sites')}
              </DropdownItem>
              <DropdownItem icon={<Map size={14} />} onClick={() => navigate('/trips')}>
                {t('nav.trips')}
              </DropdownItem>
              <DropdownSeparator />
              <DropdownItem icon={<Package size={14} />} onClick={() => navigate('/gas')}>
                {t('nav.gas_mixes')} &amp; {t('nav.tanks')}
              </DropdownItem>
              <DropdownItem icon={<Wrench size={14} />} onClick={() => navigate('/equipment')}>
                {t('nav.equipment')}
              </DropdownItem>
              <DropdownItem icon={<Cpu size={14} />} onClick={() => navigate('/devices')}>
                {t('nav.devices')}
              </DropdownItem>
              <DropdownItem icon={<Wrench size={14} />} onClick={() => navigate('/equipment-services')}>
                {t('nav.equipment_services')}
              </DropdownItem>
              <DropdownSeparator />
              <DropdownItem icon={<Users size={14} />} onClick={() => navigate('/buddies')}>
                {t('nav.buddies')}
              </DropdownItem>
              <DropdownItem icon={<Tag size={14} />} onClick={() => navigate('/tags')}>
                {t('nav.tags')}
              </DropdownItem>
              <DropdownItem icon={<Award size={14} />} onClick={() => navigate('/licenses')}>
                {t('nav.licenses')}
              </DropdownItem>
            </NavDropdown>
          )}

          {/* Logbook — only logged in */}
          {user && (
            <NavDropdown label={t('nav.logbook')} icon={<BookOpen size={15} />}>
              <DropdownItem icon={<Waves size={14} />} onClick={() => navigate('/dives')}>
                {t('nav.dives')}
              </DropdownItem>
              <DropdownItem icon={<BookOpen size={14} />} onClick={() => navigate('/dives/detail')}>
                {t('nav.dive_detail')}
              </DropdownItem>
            </NavDropdown>
          )}

          {/* Admin — only admin */}
          {isAdmin && (
            <NavDropdown label={t('nav.admin')} icon={<Shield size={15} />}>
              <DropdownItem icon={<Users size={14} />} onClick={() => navigate('/admin/users')}>
                {t('nav.admin_users')}
              </DropdownItem>
              <DropdownItem icon={<FileText size={14} />} onClick={() => navigate('/admin/audit')}>
                {t('nav.admin_audit')}
              </DropdownItem>
              <DropdownItem icon={<Ban size={14} />} onClick={() => navigate('/admin/blacklist')}>
                {t('nav.admin_blacklist')}
              </DropdownItem>
            </NavDropdown>
          )}
        </nav>

        {/* Right side — theme, lang, user */}
        <div className="flex items-center gap-1 flex-shrink-0 ml-2">

          {/* Theme switcher */}
          <NavDropdown label="" icon={currentThemeIcon}>
            <div className="px-2 py-1 text-xs font-semibold" style={{ color: 'var(--text-subtle)' }}>
              {t('theme.label')}
            </div>
            {THEMES.map((th) => (
              <DropdownItem
                key={th.value}
                icon={th.icon}
                onClick={() => setTheme(th.value)}
                style={theme === th.value ? { color: 'var(--accent)' } : {}}
              >
                {t(th.labelKey)}
                {theme === th.value && <span className="ml-auto text-xs" style={{ color: 'var(--accent)' }}>✓</span>}
              </DropdownItem>
            ))}
          </NavDropdown>

          {/* Language switcher */}
          <NavDropdown label={i18n.language === 'cs' ? 'CS' : 'EN'} icon={<Globe size={14} />}>
            {LANGS.map((lang) => (
              <DropdownItem
                key={lang.code}
                onClick={() => i18n.changeLanguage(lang.code)}
                style={i18n.language === lang.code ? { color: 'var(--accent)' } : {}}
              >
                {lang.label}
                {i18n.language === lang.code && <span className="ml-auto text-xs" style={{ color: 'var(--accent)' }}>✓</span>}
              </DropdownItem>
            ))}
          </NavDropdown>

          {/* User menu / Login */}
          {user ? (
            <NavDropdown label={user.login} icon={<User size={15} />}>
              <div className="px-3 py-2 mb-1" style={{ borderBottom: '1px solid var(--border)' }}>
                <p className="text-sm font-medium" style={{ color: 'var(--text)' }}>{user.login}</p>
                {user.email && (
                  <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{user.email}</p>
                )}
                {isAdmin && (
                  <span className="inline-flex items-center mt-1 text-xs font-medium px-2 py-0.5 rounded-full"
                    style={{ backgroundColor: 'color-mix(in srgb, var(--accent) 15%, transparent)', color: 'var(--accent)' }}>
                    Admin
                  </span>
                )}
              </div>
              <DropdownItem icon={<User size={14} />} onClick={() => navigate('/profile')}>
                {t('nav.profile')}
              </DropdownItem>
              <DropdownItem icon={<Award size={14} />} onClick={() => navigate('/licenses')}>
                {t('nav.licenses')}
              </DropdownItem>
              <DropdownItem icon={<Sliders size={14} />} onClick={() => navigate('/profile/units')}>
                {t('nav.unit_prefs')}
              </DropdownItem>
              <DropdownItem icon={<Lock size={14} />} onClick={() => navigate('/profile/password')}>
                {t('nav.change_password')}
              </DropdownItem>
              <DropdownSeparator />
              <DropdownItem icon={<LogOut size={14} />} danger onClick={handleLogout}>
                {t('nav.logout')}
              </DropdownItem>
            </NavDropdown>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                className="px-3 py-1.5 text-sm font-medium rounded-lg transition-all"
                style={{ color: 'var(--text-muted)' }}
              >
                {t('nav.login')}
              </Link>
              <Link
                to="/register"
                className="btn-primary px-4 py-1.5 text-sm rounded-lg"
              >
                {t('nav.register')}
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
