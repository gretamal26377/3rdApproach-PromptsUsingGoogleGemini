import api from "./api.js";

const authService = {
  login: async (username, password) => {
    const response = await api.post("login", { username, password });
    return response;
  },

  //Issue: We must separate admin and customer signup as they require/ask for different information
  signup: async (username, email, password) => {
    const response = await api.post("register", { username, email, password });
    return response;
  },

  logout: () => {
    // With HttpOnly auth cookies, logout is typically handled server-side (e.g., by expiring the cookie).
    // Optionally, you could call a logout endpoint here if implemented.
  },

  /**
  getToken: () => {
    // Token is stored in HttpOnly cookie; not accessible from JS
    return null;
  },
  */

  getCurrentUser: async () => {
    try {
      // Backend will read the auth_token HttpOnly cookie and decode it
      const response = await api.post("decode", {});
      if (response && response.customer) {
        return response.customer;
      }
      return null;
    } catch (error) {
      console.error("Error decoding token:", error);
      return null;
    }
  },
};

export default authService;
