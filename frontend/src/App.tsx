import { Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { authApi } from './services/api';
import { Profile, UserRole } from './types';

// Placeholder components - будут реализованы отдельно
const LoginPage = () => <div className="p-8"><h1 className="text-2xl">Login Page</h1></div>;
const DashboardPage = () => <div className="p-8"><h1 className="text-2xl">Dashboard</h1></div>;
const RequestsPage = () => <div className="p-8"><h1 className="text-2xl">Requests</h1></div>;
const CounterpartiesPage = () => <div className="p-8"><h1 className="text-2xl">Counterparties</h1></div>;
const AdminPage = () => <div className="p-8"><h1 className="text-2xl">Admin Panel</h1></div>;
const JournalPage = () => <div className="p-8"><h1 className="text-2xl">Journal</h1></div>;

function App() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      authApi.getMe()
        .then(res => setProfile(res.data))
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center h-screen">Загрузка...</div>;
  }

  return (
    <Routes>
      <Route 
        path="/login" 
        element={!profile ? <LoginPage /> : <Navigate to="/" />} 
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
