import { useState } from "react";
import "./App.css";

const API_BASE_URL =
  "https://clausecheck-git-main-hraj7as-projects.vercel.app";

function App() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [question, setQuestion] = useState("");
  const [qaResult, setQaResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);

  async function analyzeContract() {
    if (!file) {
      setError("Please upload a DOCX contract first.");
      return;
    }

    setLoading(true);
    setError("");
    setAnalysis(null);
    setQaResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      const rawText = await response.text();

      let data;
      try {
        data = JSON.parse(rawText);
      } catch {
        throw new Error(rawText.slice(0, 300));
      }

      if (!response.ok) {
        throw new Error(data.detail || "Analysis failed.");
      }

      setAnalysis(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

 async function askQuestion() {
      if (!analysis) {
        setError("Analyze a contract before asking questions.");
        return;
      }

      if (!question.trim()) {
        setError("Please enter a question.");
        return;
      }

    setAsking(true);
    setError("");
    setQaResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
          contract_text: analysis.contract_text,
          extraction: analysis.extraction,
          risk_analysis: analysis.risk_analysis,
        }),
      });

      const rawText = await response.text();

      let data;
      try {
        data = JSON.parse(rawText);
      } catch {
        throw new Error(rawText.slice(0, 300));
      }

      if (!response.ok) {
        throw new Error(data.detail || "Question answering failed.");
      }

      setQaResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setAsking(false);
    }
  }

  const summary = analysis?.dashboard_summary;
  const extraction = analysis?.extraction;
  const risk = analysis?.risk_analysis;

  return (
    <div className="app">
      {/* ── Navigation Bar ── */}
      <nav className="navbar">
        <div className="navbar-inner">
          <a href="#top" className="brand" onClick={() => setMenuOpen(false)}>
            <div className="brand-icon">
              <svg
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
                <polyline points="10 9 9 9 8 9" />
              </svg>
            </div>
            <div className="brand-text">
              <span className="brand-name">CLM Platform</span>
              <span className="brand-sub">AI Contract Intelligence</span>
            </div>
          </a>

          <button
            className={`menu-toggle ${menuOpen ? "open" : ""}`}
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle navigation menu"
          >
            <span />
            <span />
            <span />
          </button>

          <div className={`navbar-links ${menuOpen ? "open" : ""}`}>
            <a
              href="#upload"
              className="nav-link"
              onClick={() => setMenuOpen(false)}
            >
              Analyze
            </a>
            {analysis && (
              <a
                href="#results"
                className="nav-link"
                onClick={() => setMenuOpen(false)}
              >
                Results
              </a>
            )}
            {analysis && (
              <a
                href="#qa"
                className="nav-link"
                onClick={() => setMenuOpen(false)}
              >
                Ask AI
              </a>
            )}
            <span className="nav-badge">Beta</span>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <header className="hero" id="top">
        <div className="hero-inner">
          <p className="hero-eyebrow">
            AI-Powered · Contract Lifecycle Management
          </p>
          <h1 className="hero-title">Contract Review Dashboard</h1>
          <p className="hero-desc">
            Upload a contract to extract key terms, identify risks, and ask
            questions about the document using AI.
          </p>
        </div>
      </header>

      {/* ── Main Content ── */}
      <main className="container">
        {/* Upload */}
        <section className="card upload-section" id="upload">
          <div className="section-header">
            <h2>Upload Contract</h2>
            <p className="section-hint">
              DOCX format is supported for this version
            </p>
          </div>

          <div className="upload-wrapper">
            <label className="file-input-wrapper">
              <input
                type="file"
                accept=".docx"
                onChange={(e) => setFile(e.target.files[0])}
                className="file-input"
              />
              <span className="file-input-label">
                {file ? (
                  <>
                    <span className="file-check">✓</span> {file.name}
                  </>
                ) : (
                  <>
                    <span className="upload-icon">
                      <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <polyline points="16 16 12 12 8 16" />
                        <line x1="12" y1="12" x2="12" y2="21" />
                        <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3" />
                      </svg>
                    </span>
                    Click to select or drag a DOCX file
                  </>
                )}
              </span>
            </label>
            <button
              onClick={analyzeContract}
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? (
                <>
                  <span className="spinner" /> Analyzing...
                </>
              ) : (
                "Analyze Contract"
              )}
            </button>
          </div>

          {error && (
            <div className="alert alert-error">
              <span className="alert-icon">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
              </span>
              {error}
            </div>
          )}
        </section>

        {/* Results */}
        {analysis && (
          <div id="results">
            {/* Metrics */}
            <section className="metrics-section">
              <div className="metrics-grid">
                <div className="metric-card">
                  <span className="metric-label">Risk Level</span>
                  <div
                    className={`metric-value risk-badge ${summary?.overall_risk_level?.toLowerCase()}`}
                  >
                    {summary?.overall_risk_level || "Unknown"}
                  </div>
                </div>
                <div className="metric-card">
                  <span className="metric-label">Risk Score</span>
                  <div className="metric-value">
                    {summary?.risk_score ?? "N/A"}
                  </div>
                </div>
                <div className="metric-card">
                  <span className="metric-label">Parties</span>
                  <div className="metric-value">
                    {summary?.parties_count ?? 0}
                  </div>
                </div>
                <div className="metric-card">
                  <span className="metric-label">Missing Clauses</span>
                  <div className="metric-value">
                    {summary?.missing_clauses_count ?? 0}
                  </div>
                </div>
              </div>
            </section>

            {/* Overview */}
            <section className="card overview-card">
              <h2 className="card-title">
                {summary?.contract_title || analysis.filename}
              </h2>
              <p className="overview-text">{summary?.risk_summary}</p>
            </section>

            {/* Key Info + Payment */}
            <section className="grid-section">
              <div className="card info-card">
                <h2 className="card-title">Key Contract Information</h2>
                <div className="info-list">
                  <Info
                    label="Effective Date"
                    value={summary?.effective_date}
                  />
                  <Info
                    label="Expiration Date"
                    value={summary?.expiration_date}
                  />
                  <Info label="Governing Law" value={summary?.governing_law} />
                  <Info label="Jurisdiction" value={summary?.jurisdiction} />
                </div>
              </div>

              <div className="card info-card">
                <h2 className="card-title">Payment Terms</h2>
                <div className="info-list">
                  <Info
                    label="Summary"
                    value={extraction?.payment_terms?.summary}
                  />
                  <Info
                    label="Payment Frequency"
                    value={extraction?.payment_terms?.payment_frequency}
                  />
                  <Info
                    label="Late Payment Penalty"
                    value={extraction?.payment_terms?.late_payment_penalty}
                  />
                </div>
              </div>
            </section>

            {/* Contracting Parties */}
            <section className="card">
              <h2 className="card-title">Contracting Parties</h2>
              <div className="table-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Party</th>
                      <th>Role</th>
                      <th>Evidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(extraction?.contracting_parties || []).map((party, i) => (
                      <tr key={i}>
                        <td>{party.party_name}</td>
                        <td>{party.role}</td>
                        <td>{party.evidence}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Top Risks */}
            <section className="card">
              <h2 className="card-title">Top Risks</h2>
              <div className="risks-list">
                {(risk?.risks || []).slice(0, 5).map((item, i) => (
                  <div className="risk-item" key={i}>
                    <div className="risk-item-header">
                      <h3 className="risk-title">{item.risk_title}</h3>
                      <span
                        className={`risk-level ${item.risk_level?.toLowerCase()}`}
                      >
                        {item.risk_level}
                      </span>
                    </div>
                    <p className="risk-explanation">{item.explanation}</p>
                    <div className="risk-details">
                      <p>
                        <strong>Evidence:</strong> {item.evidence}
                      </p>
                      <p>
                        <strong>Recommendation:</strong> {item.recommendation}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Missing Clauses */}
            <section className="card">
              <h2 className="card-title">Missing Clauses</h2>
              <div className="table-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Clause</th>
                      <th>Risk Level</th>
                      <th>Why It Matters</th>
                      <th>Recommendation</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(risk?.missing_clauses || []).map((clause, i) => (
                      <tr key={i}>
                        <td>{clause.clause_name}</td>
                        <td>
                          <span
                            className={`risk-level ${clause.risk_level?.toLowerCase()}`}
                          >
                            {clause.risk_level}
                          </span>
                        </td>
                        <td>{clause.why_it_matters}</td>
                        <td>{clause.recommendation}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Q&A */}
            <section className="card qa-section" id="qa">
              <h2 className="card-title">Ask Questions About This Contract</h2>
              <p className="section-hint">
                Ask anything about the contract in plain language.
              </p>
              <div className="qa-wrapper">
                <input
                  type="text"
                  value={question}
                  placeholder="Example: What are the payment terms?"
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) =>
                    e.key === "Enter" && !asking && askQuestion()
                  }
                  className="qa-input"
                />
                <button
                  onClick={askQuestion}
                  disabled={asking}
                  className="btn btn-primary"
                >
                  {asking ? (
                    <>
                      <span className="spinner" /> Answering...
                    </>
                  ) : (
                    "Ask"
                  )}
                </button>
              </div>

              {qaResult && (
                <div className="answer-box">
                  <h3>Answer</h3>
                  <p className="answer-text">{qaResult.answer}</p>
                  <div className="answer-details">
                    <div className="answer-detail-item">
                      <strong>Evidence</strong>
                      <p>{qaResult.evidence}</p>
                    </div>
                    <div className="answer-detail-item">
                      <strong>Source</strong>
                      <p>{qaResult.source}</p>
                    </div>
                    <div className="answer-detail-item">
                      <strong>Confidence</strong>
                      <p>{qaResult.confidence}</p>
                    </div>
                  </div>
                </div>
              )}
            </section>
          </div>
        )}
      </main>

      {/* ── Footer ── */}
      <footer className="footer">
        <div className="footer-inner">
          <p>© 2024 Cerebrum Training · AI Contract Lifecycle Management</p>
        </div>
      </footer>
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div className="info-item">
      <span className="info-label">{label}</span>
      <p className="info-value">{value || "Not found"}</p>
    </div>
  );
}

export default App;
