const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const formatApiError = (detail) => {
  if (!detail) return "API request failed";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || JSON.stringify(item)).join(". ");
  }
  return "API request failed";
};

const apiFetch = async (endpoint, options = {}) => {
  const token = localStorage.getItem("trippilot_token");
  
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };
  
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  
  const config = {
    ...options,
    headers,
  };
  
  if (config.body && typeof config.body === "object") {
    config.body = JSON.stringify(config.body);
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
  
  if (!response.ok) {
    let errorDetail = "API request failed";
    try {
      const errJson = await response.json();
      errorDetail = formatApiError(errJson.detail);
    } catch (e) {}
    throw new Error(errorDetail);
  }
  
  // Return PDF blob for file downloads
  const contentType = response.headers.get("Content-Type") || "";
  if (contentType.includes("application/pdf")) {
    return response.blob();
  }
  
  return response.json();
};

export const api = {
  post: (endpoint, body, options = {}) => apiFetch(endpoint, { method: "POST", body, ...options }),
  get: (endpoint, options = {}) => apiFetch(endpoint, { method: "GET", ...options }),
  delete: (endpoint, options = {}) => apiFetch(endpoint, { method: "DELETE", ...options }),
};
