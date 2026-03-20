import { getToken } from "./auth";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

async function request(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail || "Request failed";
    throw new Error(detail);
  }
  return data;
}

export const api = {
  signup: (payload) => request("/auth/signup", { method: "POST", body: JSON.stringify(payload) }),
  login: (payload) => request("/auth/login", { method: "POST", body: JSON.stringify(payload) }),
  listRoles: () => request("/roles/"),
  selectedRoles: () => request("/roles/selected"),
  selectRoles: (roleIds) => request("/roles/select", { method: "POST", body: JSON.stringify({ role_ids: roleIds }) }),
  dashboard: () => request("/dashboard/me"),
  dashboardRoleHistory: (roleId) => request(`/dashboard/role-history/${roleId}`),
  startSession: (roleId) => request("/interview/sessions/start", { method: "POST", body: JSON.stringify({ role_id: roleId }) }),
  submitAnswer: (sessionId, payload) =>
    request(`/interview/sessions/${sessionId}/answer`, { method: "POST", body: JSON.stringify(payload) }),
  nextQuestion: (sessionId, category) =>
    request(`/interview/sessions/${sessionId}/next-question${category ? `?category=${encodeURIComponent(category)}` : ""}`, {
      method: "POST",
    }),
};
