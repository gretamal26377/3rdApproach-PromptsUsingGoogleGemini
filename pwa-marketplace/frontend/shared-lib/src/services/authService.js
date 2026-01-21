import api from "./api.js";

const APP_TYPE = import.meta.env.VITE_APP_TYPE || "customer";
const AUTH_BASE = APP_TYPE === "admin" ? "admin" : "customer";

const authService = {
  login: async (email, password) => {
    const payload =
      AUTH_BASE === "customer"
        ? { customer_email: email, customer_password: password }
        : { user_email: email, user_password: password };

    const response = await api.post(`${AUTH_BASE}/login`, payload);
    return response;
  },

  signup: async (data) => {
    if (AUTH_BASE === "customer") {
      const payload = {
        customer_name: data.customer_name,
        customer_email: data.customer_email,
        customer_password: data.customer_password,
        customer_phone: data.customer_phone,
      };

      // Create customer, then immediately log them in to set the HttpOnly cookie
      await api.post(`${AUTH_BASE}/register`, payload);
      await authService.login(
        payload.customer_email,
        payload.customer_password
      );
      return authService.getCurrentUser();
    }

    // Admin signup: create a new user under the admin namespace
    const adminPayload = {
      user_name: data.user_name,
      user_email: data.user_email,
      user_password: data.user_password,
      user_phone: data.user_phone,
      user_role_code: data.user_role_code,
      user_organisation_id: data.user_organisation_id,
      user_store_id: data.user_store_id,
    };

    return api.post(`${AUTH_BASE}/users`, adminPayload);
  },

  logout: () => {
    // With HttpOnly auth cookies, logout is typically handled server-side (e.g., by expiring the cookie).
    // Optionally, you could call a logout endpoint here if implemented
  },

  getCurrentUser: async () => {
    try {
      // Backend will read the auth_token HttpOnly cookie and decode it
      // This api call is passed an empty body {} since the token is in the cookie
      const response = await api.post(`${AUTH_BASE}/decode`, {});
      if (response && (response.customer || response.user)) {
        return response.customer || response.user;
      }
      return null;
    } catch (error) {
      console.error("Error decoding token:", error);
      return null;
    }
  },
};

export default authService;
