import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client.js";

const DEFAULT_ORG = "Kesari Retail Group";
const DEFAULT_INDUSTRY = "Retail";

export default function AddProcess() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    org_name: DEFAULT_ORG,
    industry: DEFAULT_INDUSTRY,
    name: "",
    category: "",
    business_purpose_raw: "",
  });
  const [status, setStatus] = useState("idle"); // idle | analysing | done | error
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus("analysing");
    setError(null);
    try {
      const analysis = await api.createProcess(form);
      setResult(analysis);
      setStatus("done");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  };

  return (
    <div>
      <h1>Add a New Process</h1>
      <p className="muted">
        This is the live "surprise record" flow. Any process entered here goes through
        the exact same pipeline as the 100 seed processes: validation → storage →
        evidence retrieval → AI analysis → deterministic scoring → persistence.
      </p>

      <form className="panel form" onSubmit={handleSubmit}>
        <label>
          Organisation
          <input value={form.org_name} onChange={(e) => setForm({ ...form, org_name: e.target.value })} required />
        </label>
        <label>
          Industry
          <input value={form.industry} onChange={(e) => setForm({ ...form, industry: e.target.value })} required />
        </label>
        <label>
          Process Name
          <input
            placeholder="e.g. Curbside Pickup Coordination"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
        </label>
        <label>
          Category (optional)
          <input
            placeholder="e.g. Store Operations"
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value })}
          />
        </label>
        <label>
          Description
          <textarea
            rows={4}
            placeholder="What does this process do, at a business level?"
            value={form.business_purpose_raw}
            onChange={(e) => setForm({ ...form, business_purpose_raw: e.target.value })}
            required
          />
        </label>
        <button type="submit" disabled={status === "analysing"}>
          {status === "analysing" ? "Analysing (retrieving evidence + calling model)..." : "Analyse This Process"}
        </button>
      </form>

      {status === "error" && <p className="error">Error: {error}</p>}

      {status === "done" && result && (
        <section className="panel">
          <h2>Analysis Complete</h2>
          <p>
            <strong>{result.process_name}</strong> was stored, analysed, scored, and is now
            queryable through the same dashboard and ranking endpoints as every other process —
            no code was changed, no restart occurred.
          </p>
          <button onClick={() => navigate(`/processes/${result.process_id}`)}>
            View Full Analysis →
          </button>
        </section>
      )}
    </div>
  );
}
