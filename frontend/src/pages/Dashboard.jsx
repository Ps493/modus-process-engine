import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";

export default function Dashboard() {
  const [top, setTop] = useState([]);
  const [humanLed, setHumanLed] = useState([]);
  const [all, setAll] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.topAiPotential(10), api.humanLed(), api.listProcesses()])
      .then(([topRes, humanRes, allRes]) => {
        setTop(topRes);
        setHumanLed(humanRes);
        setAll(allRes);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading dashboard...</p>;
  if (error) return <p className="error">Error: {error}. Is the backend running?</p>;

  const analysed = all.filter((p) => p.automation_score !== null);
  const avgScore = analysed.length
    ? (analysed.reduce((s, p) => s + p.automation_score, 0) / analysed.length).toFixed(1)
    : "—";

  return (
    <div>
      <section className="stats-row">
        <StatCard label="Total Processes" value={all.length} />
        <StatCard label="Analysed" value={analysed.length} />
        <StatCard label="Avg Automation Score" value={avgScore} />
        <StatCard label="Predominantly Human-Led" value={humanLed.length} />
      </section>

      <section className="panel">
        <h2>Top 10 — Highest AI Opportunity</h2>
        <ProcessTable rows={top} />
      </section>

      <section className="panel">
        <h2>Should Remain Predominantly Human-Led</h2>
        <ProcessTable rows={humanLed.slice(0, 10)} />
        {humanLed.length > 10 && (
          <p className="muted">+ {humanLed.length - 10} more — see All Processes</p>
        )}
      </section>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="stat-card">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

function ProcessTable({ rows }) {
  if (!rows.length) return <p className="muted">No data yet — run the seed script.</p>;
  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Process</th><th>Category</th><th>Automation Potential</th>
          <th>Automation Score</th><th>Priority Score</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((p) => (
          <tr key={p.process_id}>
            <td><Link to={`/processes/${p.process_id}`}>{p.name}</Link></td>
            <td>{p.category}</td>
            <td><span className={`badge badge-${p.automation_potential?.toLowerCase()}`}>{p.automation_potential}</span></td>
            <td>{p.automation_score?.toFixed(1)}</td>
            <td>{p.priority_score?.toFixed(1)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
