const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  listProcesses: () => request("/api/processes"),
  getProcess: (id) => request(`/api/processes/${id}`),
  createProcess: (payload) =>
    request("/api/processes", { method: "POST", body: JSON.stringify(payload) }),
  topAiPotential: (limit = 10) => request(`/api/query/top-ai-potential?limit=${limit}`),
  humanLed: () => request("/api/query/human-led"),
  evidenceFor: (processName) =>
    request(`/api/query/evidence/${encodeURIComponent(processName)}`),
  health: () => request("/api/health"),
};
