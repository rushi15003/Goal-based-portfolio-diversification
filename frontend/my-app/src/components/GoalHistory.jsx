import { useState, useEffect } from 'react';
import api from '../api/client';
import './GoalHistory.css';

export default function GoalHistory({ onGoalSelect }) {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGoals();
  }, []);

  async function fetchGoals() {
    try {
      setLoading(true);
      const res = await api.get('/inputs');
      setGoals(res.data.slice(0, 5)); // Show last 5 goals
    } catch (error) {
      console.error('Failed to fetch goals:', error);
    } finally {
      setLoading(false);
    }
  }

  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  }

  if (loading) {
    return (
      <div className="goal-history-loading">
        <div className="spinner"></div>
        <p>Loading goals...</p>
      </div>
    );
  }

  if (goals.length === 0) {
    return (
      <div className="goal-history-empty">
        <span className="empty-icon">📝</span>
        <p>No goals yet</p>
        <small>Create your first goal to get started</small>
      </div>
    );
  }

  return (
    <div className="goal-history">
      {goals.map((goal) => (
        <div 
          key={goal.id} 
          className="goal-history-item"
          onClick={() => onGoalSelect && onGoalSelect(goal)}
        >
          <div className="goal-history-header">
            <span className="goal-amount">{formatCurrency(goal.target_corpus)}</span>
            <span className={`goal-risk goal-risk-${goal.risk_profile.toLowerCase()}`}>
              {goal.risk_profile}
            </span>
          </div>
          <div className="goal-history-details">
            <span className="goal-horizon">{goal.horizon} years</span>
            <span className="goal-date">{formatDate(goal.timestamp || goal.created_at)}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

