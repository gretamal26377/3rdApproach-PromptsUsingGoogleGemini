// This line defines the base URL for the API. It's set via env var and if not provided, defaults to a local server URL

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:5001/api";

const SEARCH_API_BASE_URL =
  import.meta.env.VITE_SEARCH_API_BASE_URL ||
  "http://localhost:5002/api-search";

const api = {
  get: async (endpoint, token = null) => {
    // Token is optional. If no provided, it will be set by default to null
    const headers = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
      method: "GET",
      headers,
    });
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }
    return response.json();
  },

  // Dedicated method for search requests
  getSearch: async (endpoint, token = null) => {
    const headers = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    const response = await fetch(`${SEARCH_API_BASE_URL}/${endpoint}`, {
      method: "GET",
      headers,
    });
    if (!response.ok) {
      throw new Error(`Search API request failed: ${response.status}`);
    }
    return response.json();
  },

  // post is used for creating new resources
  post: async (endpoint, data, token = null) => {
    const headers = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
      method: "POST",
      headers,
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }
    return response.json();
  },

  // put is used to update an existing resource
  put: async (endpoint, data, token = null) => {
    const headers = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
      method: "PUT",
      headers,
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }
    return response.json();
  },

  delete: async (endpoint, token = null) => {
    const headers = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
      method: "DELETE",
      headers,
    });
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }
    return response.json();
  },
};

export default api;
