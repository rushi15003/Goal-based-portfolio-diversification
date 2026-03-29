import { useState, useEffect, useRef } from "react";
import api from "../api/client";
import Toast from "../components/Toast";
import AISummary from "../components/AISummary";

export default function GoalForm({ onGoalCreated }) {
  const [form, setForm] = useState({
    target_corpus: 2500000,
    horizon: 10,
    risk_profile: "Aggressive",
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [toast, setToast] = useState(null);
  const [qaQuestion, setQaQuestion] = useState("");
  const [chatMessages, setChatMessages] = useState([]);
  const [qaLoading, setQaLoading] = useState(false);
  const [qaError, setQaError] = useState("");
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  function showToast(message, type = "info") {
    setToast({ message, type });
  }

  function formatMessage(text) {
    if (!text) return "";
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} style={{ color: "#f8fafc" }}>{part.slice(2, -2)}</strong>;
      }
      return <span key={i}>{part}</span>;
    });
  }

  function handleChange(e) {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
    setError("");
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (!form.target_corpus || !form.horizon) throw new Error("All fields required");
      const payload = { 
        target_corpus: +form.target_corpus, 
        horizon: +form.horizon, 
        risk_profile: form.risk_profile 
      };
      const res = await api.post("/inputs", payload);
      setResult(res.data);
      showToast("Goal created successfully!", "success");
      if (onGoalCreated) onGoalCreated();
    } catch (err) {
      setResult(null);
      setError(err.response?.data?.detail || err.message || "Something went wrong!");
      showToast(err.response?.data?.detail || "Failed to create goal", "error");
    }
    setLoading(false);
  }

  function handleReset() {
    setForm({
      target_corpus: 2500000,
      horizon: 10,
      risk_profile: "Aggressive",
    });
    setResult(null);
    setError("");
    showToast("Form reset", "info");
    setQaQuestion("");
    setChatMessages([]);
    setQaError("");
  }

  function handleExportPDF() {
    if (!result) return;
    showToast("Export feature coming soon!", "info");
  }

  function handleExportCSV() {
    if (!result || !result.portfolio_table) return;
    
    const headers = ["Asset Class", "Sub Category", "Allocation (%)", "Monthly SIP (₹)"];
    const rows = result.portfolio_table.map(row => [
      row.asset_class,
      row.sub_category,
      row.allocation.toFixed(2),
      Math.round(row.monthly_sip)
    ]);
    
    const csvContent = [
      headers.join(","),
      ...rows.map(row => row.join(","))
    ].join("\n");
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `portfolio_${Date.now()}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    showToast("Portfolio exported to CSV", "success");
  }

  async function handleAskQuestion(e) {
    if (e) e.preventDefault();
    if (!result || !result.user_input?.id || !qaQuestion.trim()) {
      return;
    }
    setQaLoading(true);
    setQaError("");
    
    const userMessage = { role: "user", parts: qaQuestion.trim() };
    const currentHistory = [...chatMessages];
    setChatMessages([...currentHistory, userMessage]);
    setQaQuestion("");

    try {
      const res = await api.post("/inputs/chat", {
        question: userMessage.parts,
        goal_id: result.user_input.id,
        history: currentHistory.length > 0 ? currentHistory : undefined
      });
      const aiMessage = { role: "model", parts: res.data.answer || "" };
      setChatMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      console.error("Chat error:", err);
      // Remove the optimistic user message or show error
      setChatMessages(currentHistory);
      setQaError(
        err.response?.data?.detail ||
          "Unable to get an AI answer right now. Please try again."
      );
    } finally {
      setQaLoading(false);
    }
  }

  return (
    <main className="gbp-root">
      {toast && (
        <Toast 
          message={toast.message} 
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
      
      <form className="gbp-card gbp-form" onSubmit={handleSubmit}>
        <div className="form-header">
          <h1>Goal-Based Portfolio Planner</h1>
          {result && (
            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={handleReset}>
                New Goal
              </button>
              <button type="button" className="btn-secondary" onClick={handleExportCSV}>
                📥 Export CSV
              </button>
            </div>
          )}
        </div>
        
        <div className="gbp-fields">
          <label>Target Corpus (₹)
            <input name="target_corpus" type="number" min={1} step={1} value={form.target_corpus} onChange={handleChange} required />
          </label>
          <label>Horizon (years)
            <input name="horizon" type="number" min={1} max={30} value={form.horizon} onChange={handleChange} required />
          </label>
          <label>Risk Profile
            <select name="risk_profile" value={form.risk_profile} onChange={handleChange} required>
              <option>Conservative</option>
              <option>Moderate</option>
              <option>Aggressive</option>
            </select>
          </label>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? "Calculating..." : result ? "Recalculate" : "Calculate Portfolio"}
        </button>
        {error && <div className="gbp-err">{error}</div>}
      </form>

      {result && (
        <div className="gbp-results">
          <PortfolioSummaryCard result={result} />
          <PortfolioTable data={result.portfolio_table} />
          {result.notes?.ai_summary && (
            <AISummary summary={result.notes.ai_summary} />
          )}
          
          {/* Portfolio-aware chatbot */}
          <section className="gbp-card" style={{ marginTop: "1.5rem" }}>
            <h3 style={{ marginTop: 0 }}>Ask a question about this portfolio</h3>
            {chatMessages.length === 0 && (
              <p style={{ fontSize: 13, color: "#9ca3af", marginBottom: "0.5rem" }}>
                Example: “Is this allocation too aggressive for a {result.user_input.horizon}-year goal?” or
                “How should I adjust if I can increase my SIP by 5,000 per month?”
              </p>
            )}

            {chatMessages.length > 0 && (
              <div
                style={{
                  maxHeight: "350px",
                  overflowY: "auto",
                  padding: "1rem",
                  background: "rgba(15, 23, 42, 0.4)",
                  border: "1px solid rgba(55, 65, 81, 0.5)",
                  borderRadius: "0.5rem",
                  marginBottom: "1rem",
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.75rem",
                }}
              >
                {chatMessages.map((msg, idx) => (
                  <div
                    key={idx}
                    style={{
                      alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
                      background: msg.role === "user" ? "rgba(59, 130, 246, 0.2)" : "rgba(30, 41, 59, 0.8)",
                      border: msg.role === "user" ? "1px solid rgba(59, 130, 246, 0.4)" : "1px solid rgba(96, 165, 250, 0.4)",
                      padding: "0.75rem 1rem",
                      borderRadius: "0.75rem",
                      maxWidth: "85%",
                      fontSize: 14,
                      lineHeight: 1.5,
                      whiteSpace: "pre-wrap",
                      color: msg.role === "user" ? "#dbeafe" : "#cbd5e1",
                    }}
                  >
                    {msg.role === "model" ? formatMessage(msg.parts) : msg.parts}
                  </div>
                ))}
                {qaLoading && (
                  <div
                    style={{
                      alignSelf: "flex-start",
                      background: "rgba(30, 41, 59, 0.8)",
                      border: "1px solid rgba(96, 165, 250, 0.4)",
                      padding: "0.75rem 1rem",
                      borderRadius: "0.75rem",
                      fontSize: 14,
                      color: "#9ca3af",
                      fontStyle: "italic",
                    }}
                  >
                    Typing...
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>
            )}

            <form onSubmit={handleAskQuestion} style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              <textarea
                rows={2}
                value={qaQuestion}
                onChange={(e) => setQaQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    if (!qaLoading && qaQuestion.trim()) {
                      handleAskQuestion();
                    }
                  }
                }}
                placeholder="Type your question about this portfolio..."
                style={{
                  resize: "vertical",
                  padding: "0.6rem 0.75rem",
                  borderRadius: "0.5rem",
                  border: "1px solid #374151",
                  background: "rgba(15, 23, 42, 0.8)",
                  color: "white",
                  fontSize: 14,
                }}
              />
              <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                <button
                  type="submit"
                  disabled={qaLoading || !qaQuestion.trim()}
                  className="btn-secondary"
                  style={{ paddingInline: "1.25rem" }}
                >
                  {qaLoading ? "Wait..." : "Send"}
                </button>
                {qaError && (
                  <span style={{ color: "#fca5a5", fontSize: 12 }}>{qaError}</span>
                )}
              </div>
            </form>
          </section>
          
          {result.notes && (
            <details className="gbp-notes">
              <summary>Methodology & Notes</summary>
              <ul>
                {Object.entries(result.notes)
                  .filter(([k]) => k !== 'ai_summary')
                  .map(([k,v]) =>
                    <li key={k}><strong>{k}:</strong> {v}</li>
                  )}
              </ul>
            </details>
          )}
        </div>
      )}
    </main>
  );
}

function PortfolioSummaryCard({ result }) {
  const { allocation, sip, user_input } = result;
  return (
    <section className="gbp-card gbp-summary">
      <div className="gbp-summary-row">
        <h2 style={{margin:0}}>Result Summary</h2>
        <div style={{fontSize:12, color:"#6b7280"}}>ID: {user_input.id}</div>
      </div>
      <div className="gbp-summary-data">
        <div>
          <div className="gbp-alloc-title">Equity</div>
          <div className="gbp-alloc-main">{(allocation.equity*100).toFixed(0)}%</div>
        </div>
        <div>
          <div className="gbp-alloc-title">Debt</div>
          <div className="gbp-alloc-main">{(allocation.debt*100).toFixed(0)}%</div>
        </div>
        <div>
          <div className="gbp-alloc-title">Alts</div>
          <div className="gbp-alloc-main">{(allocation.alts*100).toFixed(0)}%</div>
        </div>
      </div>
      <div className="gbp-summary-stats">
        <div>
          <span className="gbp-label">Expected Return:</span>
          <span>{(sip.expected_return_annual * 100).toFixed(1)}%</span>
        </div>
        <div>
          <span className="gbp-label">Monthly SIP:</span>
          <span style={{fontWeight:700,color:'white',fontSize:'17px'}}>₹{sip.monthly_sip.toLocaleString("en-IN")}</span>
        </div>
        <div>
          <span className="gbp-label">Horizon:</span>
          <span>{user_input.horizon} yrs</span>
        </div>
        <div>
          <span className="gbp-label">Risk:</span>
          <span>{user_input.risk_profile}</span>
        </div>
      </div>
    </section>
  );
}

function PortfolioTable({ data }) {
  if (!data || !Array.isArray(data) || data.length === 0) return null;
  // Group by asset class
  const classes = {};
  let totalAlloc = 0, totalSip = 0;
  for (const row of data) {
    if (!classes[row.asset_class]) classes[row.asset_class] = [];
    classes[row.asset_class].push(row);
    totalAlloc += row.allocation;
    totalSip += row.monthly_sip;
  }
  const order = ["Equity", "Debt", "Alternatives"];
  return (
    <section className="gbp-card gbp-table-section">
      <h3>Portfolio Diversification</h3>
      <div style={{ overflowX: "auto" }}>
        <table className="gbp-table">
          <thead>
            <tr>
              <th>Asset Class</th>
              <th>Sub-Category</th>
              <th>Allocation</th>
              <th>Monthly SIP</th>
            </tr>
          </thead>
          <tbody>
            {order.map(cls =>
              classes[cls] && [
                <tr key={cls + "_group"} className="gbp-table-group">
                  <td colSpan={4}>{cls} (<span className="gbp-table-perc">
                    {classes[cls].reduce((acc, r) => acc + r.allocation, 0).toFixed(1)}%
                  </span>)
                  </td>
                </tr>,
                ...classes[cls].map((row, i) => (
                  <tr key={cls + "_" + i}>
                    <td></td>
                    <td>{row.sub_category}</td>
                    <td style={{ textAlign: "center" }}>{row.allocation.toFixed(1)}%</td>
                    <td style={{ textAlign: "right", fontFamily: "monospace" }}>
                      ₹{Math.round(row.monthly_sip).toLocaleString("en-IN")}
                    </td>
                  </tr>
                ))
              ]
            )}
            <tr className="gbp-table-total">
              <td></td>
              <td>TOTAL</td>
              <td style={{ textAlign: "center" }}>{totalAlloc.toFixed(1)}%</td>
              <td style={{ textAlign: "right", fontWeight: 700, color: "white", fontSize: "17px" }}>
                ₹{Math.round(totalSip).toLocaleString("en-IN")}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
}