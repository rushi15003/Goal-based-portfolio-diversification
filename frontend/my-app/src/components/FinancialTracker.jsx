import { useState, useEffect } from 'react';
import api from '../api/client';
import './FinancialTracker.css';

export default function FinancialTracker() {
  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1;

  const [selectedYear, setSelectedYear] = useState(currentYear);
  const [selectedMonth, setSelectedMonth] = useState(currentMonth);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [yearlyComparison, setYearlyComparison] = useState(null);
  const [yearlySummary, setYearlySummary] = useState(null);
  const [editingRecord, setEditingRecord] = useState(null);

  const [formData, setFormData] = useState({
    // Income
    salary: 0,
    bonus: 0,
    other_income: 0,
    // Expenses
    rent: 0,
    groceries: 0,
    utilities: 0,
    transportation: 0,
    entertainment: 0,
    healthcare: 0,
    education: 0,
    other_expenses: 0
  });

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const years = Array.from({ length: 10 }, (_, i) => currentYear - i);

  useEffect(() => {
    fetchRecords();
  }, [selectedYear]);

  useEffect(() => {
    if (records.length > 0) {
      fetchYearlySummary();
      fetchYearlyComparison();
    }
  }, [records, selectedYear]);

  async function fetchRecords() {
    try {
      setLoading(true);
      const res = await api.get(`/api/financial?year=${selectedYear}`);
      setRecords(res.data);
    } catch (error) {
      console.error('Failed to fetch records:', error);
    } finally {
      setLoading(false);
    }
  }

  async function fetchYearlySummary() {
    try {
      const res = await api.get(`/api/financial/summary/${selectedYear}`);
      setYearlySummary(res.data);
    } catch (error) {
      console.error('Failed to fetch yearly summary:', error);
      setYearlySummary(null);
    }
  }

  async function fetchYearlyComparison() {
    try {
      const res = await api.get(`/api/financial/comparison/${selectedYear}`);
      setYearlyComparison(res.data);
    } catch (error) {
      console.error('Failed to fetch yearly comparison:', error);
      setYearlyComparison(null);
    }
  }

  function handleInputChange(e) {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: parseFloat(value) || 0
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    
    try {
      const payload = {
        ...formData,
        year: selectedYear,
        month: selectedMonth,
        user_id: "user@example.com" // This will be overridden by backend
      };

      if (editingRecord) {
        await api.put(`/api/financial/${editingRecord.id}`, payload);
        alert('Record updated successfully!');
        setEditingRecord(null);
      } else {
        await api.post('/api/financial', payload);
        alert('Record saved successfully!');
      }

      // Reset form
      setFormData({
        salary: 0,
        bonus: 0,
        other_income: 0,
        rent: 0,
        groceries: 0,
        utilities: 0,
        transportation: 0,
        entertainment: 0,
        healthcare: 0,
        education: 0,
        other_expenses: 0
      });

      fetchRecords();
    } catch (error) {
      console.error('Error saving record:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to save record';
      alert(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
    }
  }

  function handleEdit(record) {
    setEditingRecord(record);
    setSelectedMonth(record.month);
    setFormData({
      salary: record.salary,
      bonus: record.bonus,
      other_income: record.other_income,
      rent: record.rent,
      groceries: record.groceries,
      utilities: record.utilities,
      transportation: record.transportation,
      entertainment: record.entertainment,
      healthcare: record.healthcare,
      education: record.education,
      other_expenses: record.other_expenses
    });
  }

  async function handleDelete(recordId) {
    if (!confirm('Are you sure you want to delete this record?')) return;

    try {
      await api.delete(`/api/financial/${recordId}`);
      alert('Record deleted successfully!');
      fetchRecords();
    } catch (error) {
      console.error('Error deleting record:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to delete record';
      alert(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
    }
  }

  function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  }

  const totalIncome = formData.salary + formData.bonus + formData.other_income;
  const totalExpenses = formData.rent + formData.groceries + formData.utilities + 
    formData.transportation + formData.entertainment + formData.healthcare + 
    formData.education + formData.other_expenses;
  const monthlySavings = totalIncome - totalExpenses;

  return (
    <div className="financial-tracker">
      {/* Yearly Comparison Card */}
      {yearlyComparison && yearlyComparison.trend !== 'no_data' && (
        <div className={`comparison-card ${yearlyComparison.trend}`}>
          <div className="comparison-header">
            <h3>📊 Year-over-Year Comparison</h3>
            <span className="comparison-years">
              {yearlyComparison.previous_year} vs {yearlyComparison.current_year}
            </span>
          </div>
          <div className="comparison-stats">
            <div className="comparison-item">
              <span className="label">Previous Year Savings</span>
              <span className="value">{formatCurrency(yearlyComparison.previous_year_savings)}</span>
            </div>
            <div className="comparison-item">
              <span className="label">Current Year Savings</span>
              <span className="value">{formatCurrency(yearlyComparison.current_year_savings)}</span>
            </div>
            <div className="comparison-item highlight">
              <span className="label">Change</span>
              <span className={`value ${yearlyComparison.trend}`}>
                {yearlyComparison.change_amount >= 0 ? '↑' : '↓'} {formatCurrency(Math.abs(yearlyComparison.change_amount))}
                <span className="percentage">
                  ({yearlyComparison.change_percentage.toFixed(2)}%)
                </span>
              </span>
            </div>
          </div>
          <div className={`trend-badge ${yearlyComparison.trend}`}>
            {yearlyComparison.trend === 'increasing' ? '📈 Savings Increasing' : '📉 Savings Decreasing'}
          </div>
        </div>
      )}

      {/* Yearly Summary */}
      {yearlySummary && (
        <div className="summary-cards">
          <div className="summary-card">
            <div className="summary-icon">💵</div>
            <div className="summary-content">
              <span className="summary-label">Total Income</span>
              <span className="summary-value">{formatCurrency(yearlySummary.total_income)}</span>
            </div>
          </div>
          <div className="summary-card">
            <div className="summary-icon">💸</div>
            <div className="summary-content">
              <span className="summary-label">Total Expenses</span>
              <span className="summary-value">{formatCurrency(yearlySummary.total_expenses)}</span>
            </div>
          </div>
          <div className="summary-card highlight">
            <div className="summary-icon">💰</div>
            <div className="summary-content">
              <span className="summary-label">Total Savings</span>
              <span className="summary-value savings">{formatCurrency(yearlySummary.total_savings)}</span>
            </div>
          </div>
          <div className="summary-card">
            <div className="summary-icon">📅</div>
            <div className="summary-content">
              <span className="summary-label">Months Recorded</span>
              <span className="summary-value">{yearlySummary.months_recorded}/12</span>
            </div>
          </div>
        </div>
      )}

      {/* Input Form */}
      <div className="financial-form-section">
        <h3>{editingRecord ? '✏️ Edit Record' : '➕ Add New Record'}</h3>
        
        <form onSubmit={handleSubmit} className="financial-form">
          <div className="form-selectors">
            <div className="form-group">
              <label>Year</label>
              <select 
                value={selectedYear} 
                onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                disabled={editingRecord}
              >
                {years.map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Month</label>
              <select 
                value={selectedMonth} 
                onChange={(e) => setSelectedMonth(parseInt(e.target.value))}
                disabled={editingRecord}
              >
                {months.map((month, idx) => (
                  <option key={idx} value={idx + 1}>{month}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-sections">
            {/* Income Section */}
            <div className="form-section">
              <h4 className="section-title">💵 Income</h4>
              <div className="form-grid">
                <div className="form-group">
                  <label>Salary</label>
                  <input
                    type="number"
                    name="salary"
                    value={formData.salary}
                    onChange={handleInputChange}
                    min="0"
                    step="100"
                  />
                </div>
                <div className="form-group">
                  <label>Bonus</label>
                  <input
                    type="number"
                    name="bonus"
                    value={formData.bonus}
                    onChange={handleInputChange}
                    min="0"
                    step="100"
                  />
                </div>
                <div className="form-group">
                  <label>Other Income</label>
                  <input
                    type="number"
                    name="other_income"
                    value={formData.other_income}
                    onChange={handleInputChange}
                    min="0"
                    step="100"
                  />
                </div>
              </div>
              <div className="section-total">
                Total Income: <strong>{formatCurrency(totalIncome)}</strong>
              </div>
            </div>

            {/* Expenses Section */}
            <div className="form-section">
              <h4 className="section-title">💸 Expenses</h4>
              <div className="form-grid">
                <div className="form-group">
                  <label>Rent</label>
                  <input
                    type="number"
                    name="rent"
                    value={formData.rent}
                    onChange={handleInputChange}
                    min="0"
                    step="100"
                  />
                </div>
                <div className="form-group">
                  <label>Groceries</label>
                  <input
                    type="number"
                    name="groceries"
                    value={formData.groceries}
                    onChange={handleInputChange}
                    min="0"
                    step="100"
                  />
                </div>
                <div className="form-group">
                  <label>Utilities</label>
                  <input
                    type="number"
                    name="utilities"
                    value={formData.utilities}
                    onChange={handleInputChange}
                    min="0"
                    step="100"
                  />
                </div>
                <div className="form-group">
                  <label>Transportation</label>
                  <input
                    type="number"
                    name="transportation"
                    value={formData.transportation}
                    onChange={handleInputChange}
                    min="0"
                    step="100"
                  />
                </div>
                <div className="form-group">
                  <label>Entertainment</label>
                  <input
                    type="number"
                    name="entertainment"
                    value={formData.entertainment}
                    onChange={handleInputChange}
                    min="0"
                    step="100"
                  />
                </div>
                <div className="form-group">
                  <label>Healthcare</label>
                  <input
                    type="number"
                    name="healthcare"
                    value={formData.healthcare}
                    onChange={handleInputChange}
                    min="0"
                    step="100"
                  />
                </div>
                <div className="form-group">
                  <label>Education</label>
                  <input
                    type="number"
                    name="education"
                    value={formData.education}
                    onChange={handleInputChange}
                    min="0"
                    step="100"
                  />
                </div>
                <div className="form-group">
                  <label>Other Expenses</label>
                  <input
                    type="number"
                    name="other_expenses"
                    value={formData.other_expenses}
                    onChange={handleInputChange}
                    min="0"
                    step="100"
                  />
                </div>
              </div>
              <div className="section-total">
                Total Expenses: <strong>{formatCurrency(totalExpenses)}</strong>
              </div>
            </div>
          </div>

          {/* Savings Preview */}
          <div className={`savings-preview ${monthlySavings < 0 ? 'negative' : 'positive'}`}>
            <span className="savings-label">Monthly Savings:</span>
            <span className="savings-amount">{formatCurrency(monthlySavings)}</span>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary">
              {editingRecord ? 'Update Record' : 'Save Record'}
            </button>
            {editingRecord && (
              <button 
                type="button" 
                className="btn-secondary"
                onClick={() => {
                  setEditingRecord(null);
                  setFormData({
                    salary: 0, bonus: 0, other_income: 0,
                    rent: 0, groceries: 0, utilities: 0,
                    transportation: 0, entertainment: 0, healthcare: 0,
                    education: 0, other_expenses: 0
                  });
                }}
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      </div>

      {/* Records Table */}
      <div className="records-section">
        <h3>📋 Monthly Records for {selectedYear}</h3>
        
        {loading ? (
          <div className="loading-state">Loading records...</div>
        ) : records.length === 0 ? (
          <div className="empty-state">
            <p>No records found for {selectedYear}</p>
            <p className="empty-hint">Start by adding your first monthly record above</p>
          </div>
        ) : (
          <div className="records-table-container">
            <table className="records-table">
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Total Income</th>
                  <th>Total Expenses</th>
                  <th>Savings</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {records.map(record => (
                  <tr key={record.id}>
                    <td>{months[record.month - 1]}</td>
                    <td className="income">{formatCurrency(record.total_income)}</td>
                    <td className="expense">{formatCurrency(record.total_expenses)}</td>
                    <td className={`savings ${record.monthly_savings < 0 ? 'negative' : 'positive'}`}>
                      {formatCurrency(record.monthly_savings)}
                    </td>
                    <td className="actions">
                      <button 
                        className="btn-edit" 
                        onClick={() => handleEdit(record)}
                        title="Edit"
                      >
                        ✏️
                      </button>
                      <button 
                        className="btn-delete" 
                        onClick={() => handleDelete(record.id)}
                        title="Delete"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

