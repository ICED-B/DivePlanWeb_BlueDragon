import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { ProtectedRoute, AdminRoute } from './components/ProtectedRoute';

// Pages — public
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import NotFoundPage from './pages/NotFoundPage';
import TermsPage from './pages/legal/TermsPage';
import PrivacyPage from './pages/legal/PrivacyPage';

// Planner — public
import CalculatorsPage from './pages/planner/CalculatorsPage';
import BigPlannerPage from './pages/planner/BigPlannerPage';

// Stats — public (global) / private (user)
import GlobalStatsPage from './pages/stats/GlobalStatsPage';
import UserStatsPage from './pages/stats/UserStatsPage';

// Data — protected
import DivesPage from './pages/dives/DivesPage';
import DiveDetailPage from './pages/dives/DiveDetailPage';
import SitesPage from './pages/sites/SitesPage';
import TripsPage from './pages/trips/TripsPage';
import GasPage from './pages/gas/GasPage';
import EquipmentPage from './pages/equipment/EquipmentPage';
import EquipmentServicesPage from './pages/equipment/EquipmentServicesPage';
import BuddiesPage from './pages/buddies/BuddiesPage';
import TagsPage from './pages/tags/TagsPage';
import LicensesPage from './pages/licenses/LicensesPage';
import DevicesPage from './pages/devices/DevicesPage';

// Profile — protected
import ProfilePage from './pages/profile/ProfilePage';
import UnitPrefsPage from './pages/profile/UnitPrefsPage';
import ChangePasswordPage from './pages/profile/ChangePasswordPage';

// Admin — admin only
import AdminUsersPage from './pages/admin/AdminUsersPage';
import AdminAuditPage from './pages/admin/AdminAuditPage';
import AdminBlacklistPage from './pages/admin/AdminBlacklistPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>

          {/* Public routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />

          {/* Planner — public */}
          <Route path="/planner" element={<Navigate to="/planner/calculators" replace />} />
          <Route path="/planner/calculators" element={<CalculatorsPage />} />
          <Route path="/planner/plan" element={<BigPlannerPage />} />

          {/* Stats */}
          <Route path="/stats" element={<Navigate to="/stats/global" replace />} />
          <Route path="/stats/global" element={<GlobalStatsPage />} />
          <Route path="/stats/user" element={
            <ProtectedRoute><UserStatsPage /></ProtectedRoute>
          } />

          {/* My data — protected */}
          <Route path="/dives" element={<ProtectedRoute><DivesPage /></ProtectedRoute>} />
          <Route path="/dives/detail" element={<ProtectedRoute><DiveDetailPage /></ProtectedRoute>} />
          <Route path="/sites" element={<ProtectedRoute><SitesPage /></ProtectedRoute>} />
          <Route path="/trips" element={<ProtectedRoute><TripsPage /></ProtectedRoute>} />
          <Route path="/gas" element={<ProtectedRoute><GasPage /></ProtectedRoute>} />
          <Route path="/equipment" element={<ProtectedRoute><EquipmentPage /></ProtectedRoute>} />
          <Route path="/equipment-services" element={<ProtectedRoute><EquipmentServicesPage /></ProtectedRoute>} />
          <Route path="/buddies" element={<ProtectedRoute><BuddiesPage /></ProtectedRoute>} />
          <Route path="/tags" element={<ProtectedRoute><TagsPage /></ProtectedRoute>} />
          <Route path="/licenses" element={<ProtectedRoute><LicensesPage /></ProtectedRoute>} />
          <Route path="/devices" element={<ProtectedRoute><DevicesPage /></ProtectedRoute>} />

          {/* Profile — protected */}
          <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
          <Route path="/profile/units" element={<ProtectedRoute><UnitPrefsPage /></ProtectedRoute>} />
          <Route path="/profile/password" element={<ProtectedRoute><ChangePasswordPage /></ProtectedRoute>} />

          {/* Admin — admin only */}
          <Route path="/admin/users" element={<AdminRoute><AdminUsersPage /></AdminRoute>} />
          <Route path="/admin/audit" element={<AdminRoute><AdminAuditPage /></AdminRoute>} />
          <Route path="/admin/blacklist" element={<AdminRoute><AdminBlacklistPage /></AdminRoute>} />

          {/* 404 */}
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
