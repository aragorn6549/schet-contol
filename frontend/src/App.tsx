import { Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { authApi } from './services/api';
import { Profile, UserRole } from './types';

// Placeholder components - будут реализованы отдельно
const LoginPage = ({ onLogin }: { onLogin?: () => void }) => (
  <div className="p-8">
    <h1 className="text-2xl">Login Page</h1>
    <p className="mt-4 text-gray-600">Вход через Supabase Auth</p>
  </div>
);
const DashboardPage = ({ profile }: { profile: Profile }) => (
  <div className="p-8">
    <h1 className="text-2xl">Dashboard</h1>
    <p className="mt-4">Добро пожаловать, {profile.full_name}!</p>
    <p className="text-gray-600">Роль: {profile.role}</p>
  </div>
);
const RequestsPage = ({ profile }: { profile: Profile }) => (
  <div className="p-8">
    <h1 className="text-2xl">Заявки</h1>
    <p className="mt-4 text-gray-600">Управление заявками для роли: {profile.role}</p>
  </div>
);
const CounterpartiesPage = ({ profile }: { profile?: Profile }) => (
  <div className="p-8">
    <h1 className="text-2xl">Контрагенты</h1>
    <p className="mt-4 text-gray-600">Справочник контрагентов</p>
  </div>
);
const AdminPage = () => (
  <div className="p-8">
    <h1 className="text-2xl">Админ панель</h1>
    <p className="mt-4 text-gray-600">Управление пользователями</p>
  </div>
);
const JournalPage = () => (
  <div className="p-8">
    <h1 className="text-2xl">Журнал операций</h1>
    <p className="mt-4 text-gray-600">История всех действий</p>
  </div>
);

function App() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const userProfile = await authApi.getMe();
        setProfile(userProfile);
      } catch (error) {
        // Not authenticated
        console.log('Not authenticated');
      } finally {
        setLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center h-screen">Загрузка...</div>;
  }

  return (
    <Routes>
      <Route 
        path="/login" 
        element={!profile ? <LoginPage onLogin={() => {}} /> : <Navigate to="/" />} 
      />
      <Route 
        path="/" 
        element={profile ? <DashboardPage profile={profile} /> : <Navigate to="/login" />} 
      />
      <Route 
        path="/requests" 
        element={profile ? <RequestsPage profile={profile} /> : <Navigate to="/login" />} 
      />
      <Route 
        path="/counterparties" 
        element={profile ? <CounterpartiesPage profile={profile} /> : <Navigate to="/login" />} 
      />
      <Route 
        path="/admin" 
        element={profile?.role === UserRole.ADMIN ? <AdminPage /> : <Navigate to="/" />} 
      />
      <Route 
        path="/journal" 
        element={profile ? <JournalPage /> : <Navigate to="/login" />} 
      />
    </Routes>
  );
}

export default App;
