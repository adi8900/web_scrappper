const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

async function request(path, options = {}) {
  const token = getToken();
  const response = await fetch(API + path, {
    cache: "no-store",
    ...options,
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `Błąd HTTP ${response.status}`);
  return data;
}

export async function register(username, email, password) {
  const params = new URLSearchParams({ username, email, password });
  return request(`/api/auth/register?${params}`, { method: "POST" });
}

export async function login(username, password) {
  const params = new URLSearchParams({ username, password });
  const data = await request(`/api/auth/login?${params}`, { method: "POST" });
  if (data.access_token) {
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("username", data.username);
  }
  return data;
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("username");
}

export async function getMe() {
  if (!getToken()) return null;
  try { return await request("/api/auth/me"); }
  catch { return null; }
}

export async function comparePart(query, method = "html") {
  return request(`/api/compare?${new URLSearchParams({ query, method })}`);
}

export async function getHistory() {
  return request("/api/history");
}
