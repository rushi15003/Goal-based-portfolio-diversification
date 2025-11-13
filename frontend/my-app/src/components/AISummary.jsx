import './AISummary.css';

export default function AISummary({ summary }) {
  if (!summary) return null;

  // Parse markdown-style formatting
  const renderSummary = () => {
    const lines = summary.split('\n');
    return lines.map((line, index) => {
      // Headers (###)
      if (line.startsWith('### ')) {
        return <h3 key={index} className="ai-summary-header">{line.replace('### ', '')}</h3>;
      }
      // Bold (**text:**)
      if (line.startsWith('**') && line.includes(':**')) {
        const text = line.replace(/\*\*/g, '');
        const [label, ...rest] = text.split(':');
        return (
          <div key={index} className="ai-summary-section">
            <strong className="ai-summary-label">{label}:</strong>
            <span>{rest.join(':')}</span>
          </div>
        );
      }
      // Bullet points
      if (line.startsWith('• ')) {
        return <li key={index} className="ai-summary-bullet">{line.replace('• ', '')}</li>;
      }
      // Empty lines
      if (line.trim() === '') {
        return <div key={index} className="ai-summary-spacer"></div>;
      }
      // Regular text
      return <p key={index} className="ai-summary-text">{line}</p>;
    });
  };

  return (
    <div className="ai-summary-container">
      <div className="ai-summary-header-bar">
        <span className="ai-icon">🤖</span>
        <h2>AI Portfolio Insights</h2>
        <span className="ai-badge">Powered by AI</span>
      </div>
      <div className="ai-summary-content">
        {renderSummary()}
      </div>
    </div>
  );
}



