const API_BASE = "/api/v1";

const Auth = {
  getAccess() {
    return localStorage.getItem("access_token");
  },
  getRefresh() {
    return localStorage.getItem("refresh_token");
  },
  setTokens({ access, refresh }) {
    localStorage.setItem("access_token", access);
    if (refresh) {
      localStorage.setItem("refresh_token", refresh);
    }
  },
  clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },
  isLoggedIn() {
    return Boolean(this.getAccess());
  },
  logout() {
    this.clearTokens();
    window.location.href = "/login/";
  },
  requireLogin() {
    if (!this.isLoggedIn()) {
      window.location.href = "/login/";
    }
  },
};

async function refreshAccessToken() {
  const refresh = Auth.getRefresh();
  if (!refresh) return false;

  const response = await fetch(`${API_BASE}/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });

  if (!response.ok) {
    return false;
  }
  const data = await response.json();
  Auth.setTokens({ access: data.access });
  return true;
}

/**
 * Wraps fetch(): attaches the JWT, and on a 401 tries exactly one silent
 * refresh + retry before giving up and forcing a re-login.
 */
async function apiFetch(path, options = {}) {
  const access = Auth.getAccess();
  const headers = { ...(options.headers || {}) };
  if (access) {
    headers["Authorization"] = `Bearer ${access}`;
  }
  if (options.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  let response = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (response.status === 401 && Auth.getRefresh()) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      headers["Authorization"] = `Bearer ${Auth.getAccess()}`;
      response = await fetch(`${API_BASE}${path}`, { ...options, headers });
    } else {
      Auth.logout();
      throw new Error("Session expired. Please log in again.");
    }
  }

  return response;
}

async function apiJson(path, options = {}) {
  const response = await apiFetch(path, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error("Request failed");
    error.status = response.status;
    error.data = data;
    throw error;
  }
  return data;
}

function formatErrors(errorData) {
  if (!errorData) return "Something went wrong.";
  if (typeof errorData === "string") return errorData;
  if (errorData.detail) return errorData.detail;

  const parts = [];
  for (const [field, messages] of Object.entries(errorData)) {
    const text = Array.isArray(messages) ? messages.join(" ") : messages;
    parts.push(field === "non_field_errors" ? text : `${field}: ${text}`);
  }
  return parts.join(" | ") || "Something went wrong.";
}
