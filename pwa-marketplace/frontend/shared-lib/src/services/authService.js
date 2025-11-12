import api from "./api.js";

const authService = {
  login: async (username, password) => {
    const response = await api.post("login", { username, password });
    if (response.token) {
      // By security reasons, only the token is stored in localStorage and not the user object
      localStorage.setItem("token", response.token);
    }
    return response;
  },

  signup: async (username, email, password) => {
    const response = await api.post("register", { username, email, password });
    if (response.token) {
      localStorage.setItem("token", response.token);
    }
    return response;
  },

  logout: () => {
    localStorage.removeItem("token");
  },

  getToken: () => {
    return localStorage.getItem("token");
  },

  getCurrentUser: async () => {
    // Issue?: Perhaps to set a try/catch block here to handle errors when calling the backend?
    const token = authService.getToken();
    if (token) {
      try {
        // Call the /decode endpoint and token will be passed as JSON data 2nd body parameter and not as 3rd token parameter in deed because of security reasons given by Copilot
        const response = await api.post("decode", { token }); // Call the /decode endpoint
        if (response && response.user) {
          return response.user; // Return the user object from the backend
        } else {
          return null; // Or handle the error as appropriate
        }
      } catch (error) {
        console.error("Error decoding token:", error);
        return null; // Handle the error
      }
    }
    return null;
  },
};

export default authService;
