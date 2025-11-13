import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import GoalForm from './GoalForm';
import MarketData from '../components/MarketData';
import FinancialTracker from '../components/FinancialTracker';
import './Dashboard.css';
import api from '../api/client';

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalGoals: 0,
    totalInvestment: 0,
    portfolioValue: 0
  });
  const [activeTab, setActiveTab] = useState('portfolio'); // 'portfolio' or 'market'

  function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  }

  function handleGoalCreated() {
    // Stats remain at 0
  }

  return (
    <div className="dashboard-layout">
      <Navbar />
      
      <div className="dashboard-container">
        <aside className="dashboard-sidebar">
          <div className="sidebar-section">
            <h3 className="sidebar-title">📈 Quick Stats</h3>
            <div className="stat-card">
              <div className="stat-label">Total Goals</div>
              <div className="stat-value">{stats.totalGoals}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Yearly Investment</div>
              <div className="stat-value">{formatCurrency(stats.totalInvestment)}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Target Corpus</div>
              <div className="stat-value">{formatCurrency(stats.portfolioValue)}</div>
            </div>
          </div>
        </aside>

        <main className="dashboard-main">
          <div className="dashboard-tabs">
            <button 
              className={`tab-btn ${activeTab === 'portfolio' ? 'active' : ''}`}
              onClick={() => setActiveTab('portfolio')}
            >
              📊 Portfolio Planning
            </button>
            <button 
              className={`tab-btn ${activeTab === 'market' ? 'active' : ''}`}
              onClick={() => setActiveTab('market')}
            >
              📈 Live Market Data
            </button>
            <button 
              className={`tab-btn ${activeTab === 'financial' ? 'active' : ''}`}
              onClick={() => setActiveTab('financial')}
            >
              💰 Financial Tracker
            </button>
          </div>

          {activeTab === 'portfolio' ? (
            <>
              <div className="dashboard-header">
                <h2 className="page-title">Goal-Based Portfolio Planning</h2>
                <p className="page-subtitle">
                  Create and manage your investment goals with personalized portfolio recommendations
                </p>
              </div>
              <GoalForm onGoalCreated={handleGoalCreated} />
            </>
          ) : activeTab === 'market' ? (
            <>
              <div className="dashboard-header">
                <h2 className="page-title">NSE/BSE Live Market Data</h2>
                <p className="page-subtitle">
                  Real-time stock prices and market indices
                </p>
              </div>
              <MarketData />
            </>
          ) : (
            <>
              <div className="dashboard-header">
                <h2 className="page-title">💰 Income & Savings Tracker</h2>
                <p className="page-subtitle">
                  Track your monthly income and expenses to monitor your financial health
                </p>
              </div>
              <FinancialTracker />
            </>
          )}
        </main>
      </div>
    </div>
  );
}

