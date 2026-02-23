import api from "./api.js";

const APP_TYPE = import.meta.env.VITE_APP_TYPE || "customer";

const authService = {
  login: async (email, password) => {
    const payload =
      APP_TYPE === "customer"
        ? { customer_email: email, customer_password: password }
        : { user_email: email, user_password: password };

    const response = await api.post(`${APP_TYPE}/login`, payload);
    return response;
  },

  signup: async (data) => {
    if (APP_TYPE === "customer") {
      const payload = {
        customer_name: data.customer_name,
        customer_email: data.customer_email,
        customer_password: data.customer_password,
        customer_phone: data.customer_phone,
        customer_addresses: Array.isArray(data.addresses)
          ? data.addresses.map((addr) => ({
              address_line1: addr.addressLine1,
              address_line2: addr.addressLine2,
              country_id: addr.countryId,
              city_town_id: addr.cityTownId,
              state_region_id: addr.stateRegionId,
              postal_code: addr.postalCode,
            }))
          : [],
      };

      // Create Customer, then immediately log in to set the HttpOnly cookie
      await api.post(`${APP_TYPE}/register`, payload);
      await authService.login(
        payload.customer_email,
        payload.customer_password
      );
      return authService.getCurrentUser();
    }

    // Admin signup: Create a new User under the Admin namespace
    const adminPayload = {
      user_name: data.user_name,
      user_email: data.user_email,
      user_password: data.user_password,
      user_phone: data.user_phone,
      user_organisation_id: data.user_organisation_id,
      user_role_code: data.user_role_code,
      user_store_ids: Array.isArray(data.user_store_ids)
        ? data.user_store_ids
        : [],
    };

    return api.post(`${APP_TYPE}/users`, adminPayload);
  },

  logout: () => {
    // With HttpOnly auth cookies, logout is typically handled server-side (e.g., by expiring the cookie).
    // Optionally, you could call a logout endpoint here if implemented
  },

  getCurrentUser: async () => {
    try {
      // Backend will read the auth_token HttpOnly cookie and decode it
      // This api call is passed an empty body {} since the token is in the cookie
      const response = await api.post(`${APP_TYPE}/decode`, {});
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
