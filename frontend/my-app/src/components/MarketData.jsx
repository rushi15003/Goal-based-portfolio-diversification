import React, { useState, useEffect } from 'react';
import './MarketData.css';
import api from '../api/client';

export default function MarketData() {
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchMarketData = async () => {
    try {
      setError(null);
      const response = await api.get('/api/market/all');
      setMarketData(response.data);
      setLastUpdated(new Date().toLocaleTimeString('en-IN'));
      setLoading(false);
    } catch (err) {
      console.error('Error fetching market data:', err);
      setError('Unable to fetch market data');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMarketData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchMarketData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price);
  };

  const getChangeClass = (change) => {
    if (change > 0) return 'positive';
    if (change < 0) return 'negative';
    return 'neutral';
  };

  const getChangeIcon = (change) => {
    if (change > 0) return '▲';
    if (change < 0) return '▼';
    return '●';
  };

  if (loading) {
    return (
      <div className="market-data-container">
        <div className="market-header">
          <h2>📊 Live Market Data</h2>
        </div>
        <div className="market-loading">Loading market data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="market-data-container">
        <div className="market-header">
          <h2>📊 Live Market Data</h2>
        </div>
        <div className="market-error">{error}</div>
      </div>
    );
  }

  return (
    <div className="market-data-container">
      <div className="market-header">
        <div>
          <h2>📊 Live Market Data</h2>
          <p className="market-subtitle">NSE / BSE Real-time Prices</p>
        </div>
        <div className="market-refresh">
          <span className="last-updated">Updated: {lastUpdated}</span>
          <button onClick={fetchMarketData} className="refresh-btn" title="Refresh">
            🔄
          </button>
        </div>
      </div>

      {/* Indices Section */}
      <section className="market-section">
        <h3 className="section-title">Market Indices</h3>
        <div className="market-grid">
          {marketData?.indices?.map((index, i) => (
            <div key={i} className="market-card">
              <div className="market-card-header">
                <span className="market-name">{index.name}</span>
                <span className={`market-state ${index.marketState?.toLowerCase()}`}>
                  {index.marketState === 'REGULAR' ? '● OPEN' : '● CLOSED'}
                </span>
              </div>
              <div className="market-price">{formatPrice(index.price)}</div>
              <div className={`market-change ${getChangeClass(index.change)}`}>
                <span className="change-icon">{getChangeIcon(index.change)}</span>
                <span className="change-value">{formatPrice(Math.abs(index.change))}</span>
                <span className="change-percent">({index.changePercent > 0 ? '+' : ''}{index.changePercent}%)</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Stocks Section */}
      <section className="market-section">
        <h3 className="section-title">Popular Stocks</h3>
        <div className="stocks-table">
          <table>
            <thead>
              <tr>
                <th>Stock</th>
                <th>Price</th>
                <th>Change</th>
                <th>Change %</th>
                <th>Prev. Close</th>
              </tr>
            </thead>
            <tbody>
              {marketData?.stocks?.map((stock, i) => (
                <tr key={i}>
                  <td className="stock-name">
                    <strong>{stock.name}</strong>
                    <span className="stock-symbol">{stock.symbol}</span>
                  </td>
                  <td className="stock-price">{formatPrice(stock.price)}</td>
                  <td className={`stock-change ${getChangeClass(stock.change)}`}>
                    {getChangeIcon(stock.change)} {formatPrice(Math.abs(stock.change))}
                  </td>
                  <td className={`stock-change-percent ${getChangeClass(stock.changePercent)}`}>
                    {stock.changePercent > 0 ? '+' : ''}{stock.changePercent}%
                  </td>
                  <td className="stock-prev-close">{formatPrice(stock.previousClose)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <div className="market-footer">
        <p>Data sourced from Yahoo Finance • Auto-refreshes every 30 seconds</p>
        <p className="market-disclaimer">* Market data may be delayed. For informational purposes only.</p>
      </div>
    </div>
  );
}

