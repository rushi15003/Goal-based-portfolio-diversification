import { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import "./App.css";

function AppContent() {
  const { user, login, loading } = useAuth();
  const [showSignup, setShowSignup] = useState(false);

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        fontSize: '18px',
        color: '#667eea'
      }}>
        Loading...
      </div>
    );
  }

  if (!user) {
    return showSignup ? (
      <Signup
        onSwitchToLogin={() => setShowSignup(false)}
        onSignupSuccess={login}
      />
    ) : (
      <Login
        onSwitchToSignup={() => setShowSignup(true)}
        onLoginSuccess={login}
      />
    );
  }

  return <Dashboard />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}