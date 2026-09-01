import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";

export default function ProcessList() {
  const [processes, setProcesses] = useState([]);
  const [error, setError] = useState(null);
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [sortKey, setSortKey] = useState("priority_score");
  const [sortDir, setSortDir] = useState("desc");

  useEffect(() => {
    api.listProcesses().then(setProcesses).catch((e) => setError(e.message));
  }, []);

  const categories = useMemo(
    () => ["All", ...new Set(processes.map((p) => p.category).filter(Boolean))],
    [processes]
  );

  const filtered = useMemo(() => {
    let rows = categoryFilter === "All" ? processes : processes.filter((p) => p.category === categoryFilter);
    rows = [...rows].sort((a, b) => {
      const av = a[sortKey] ?? -Infinity;
      const bv = b[sortKey] ?? -Infinity;
      return sortDir === "desc" ? bv - av : av - bv;
    });
    return rows;
  }, [processes, categoryFilter, sortKey, sortDir]);

  if (error) return <p className="error">Error: {error}</p>;

  return (
    <div>
      <div className="panel-header-row">
        <h2>All Processes ({filtered.length})</h2>
        <div className="controls">
          <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
            {categories.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <select value={sortKey} onChange={(e) => setSortKey(e.target.value)}>
            <option value="priority_score">Sort: Priority Score</option>
            <option value="automation_score">Sort: Automation Score</option>
          </select>
          <button onClick={() => setSortDir(sortDir === "desc" ? "asc" : "desc")}>
            {sortDir === "desc" ? "↓ High to Low" : "↑ Low to High"}
          </button>
        </div>
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th>Process</th><th>Category</th><th>Automation Potential</th>
            <th>Automation Score</th><th>Priority Score</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((p) => (
            <tr key={p.process_id}>
              <td><Link to={`/processes/${p.process_id}`}>{p.name}</Link></td>
              <td>{p.category}</td>
              <td><span className={`badge badge-${p.automation_potential?.toLowerCase()}`}>{p.automation_potential || "—"}</span></td>
              <td>{p.automation_score?.toFixed(1) ?? "—"}</td>
              <td>{p.priority_score?.toFixed(1) ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
