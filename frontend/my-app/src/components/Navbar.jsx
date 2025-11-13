import { useAuth } from '../context/AuthContext';
import './Navbar.css';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <div className="brand-icon">📊</div>
          <h1 className="brand-title">Portfolio Manager</h1>
        </div>

        <div className="navbar-user">
          <div className="user-info">
            <div className="user-avatar">
              {user?.full_name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="user-details">
              <div className="user-name">{user?.full_name}</div>
              <div className="user-email">{user?.email}</div>
            </div>
          </div>
          <button onClick={logout} className="logout-btn">
            <span>🚪</span> Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
