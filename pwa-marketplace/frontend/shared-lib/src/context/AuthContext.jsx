import React, { useState, useEffect, createContext } from "react";
import authService from "../services/authService";

/**
 * @typedef {Object} LoginPayload
 * @property {string} email
 * @property {string} password
 */

/**
 * @typedef {Object} SignupPayload
 * @property {string} [customer_name]
 * @property {string} [customer_email]
 * @property {string} [customer_password]
 * @property {string} [customer_phone]
 * @property {string} [user_name]
 * @property {string} [user_email]
 * @property {string} [user_password]
 * @property {string} [user_phone]
 * @property {string} [user_role_code]
 * @property {string|number} [user_organisation_id]
 * @property {string|number} [user_store_id]
 */
// import { useNavigate } from "react-router-dom";

/**
Context to manage authentication state across the application.
createContext is used to create a context object that can be used to share data
across components without having to pass props down manually at every level.
Initially, the context is set with default or placeholder values that later can be
updated by authContextValue
*/
export const AuthContext = createContext({
  isLoggedIn: false,
  user: null,
  isAdmin: false,
  login: /** @type {(payload: LoginPayload) => Promise<any>} */ (
    async (_payload) => {}
  ),
  signup: /** @type {(payload: SignupPayload) => Promise<any>} */ (
    async (_payload) => {}
  ),
  logout: () => {},
});

/** @param {{ children: import('react').ReactNode }} props */
export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null); // Issue: Change user to customer
  const [isAdmin, setIsAdmin] = useState(false); // Issue: Change all logic for Role approach
  // Purpose: To navigate programmatically. For example, navigate("/login") to trigger navigating to the login page
  //const navigate = useNavigate();

  // On component mount, check if user is already logged in. Runs only once when the component is first rendered
  useEffect(() => {
    let isMounted = true;
    const fetchUser = async () => {
      const currentUser = await authService.getCurrentUser();
      if (isMounted && currentUser) {
        setUser(currentUser);
        setIsLoggedIn(true);
        setIsAdmin(currentUser.is_admin || false);
      }
    };
    fetchUser();
    return () => {
      isMounted = false;
    };
  }, []);

  /** @param {LoginPayload} userData */
  const handleLogin = async (userData) => {
    await authService.login(userData.email, userData.password);
    const currentUser = await authService.getCurrentUser();
    if (currentUser) {
      setIsLoggedIn(true);
      setUser(currentUser);
      setIsAdmin(currentUser.is_admin || false);
    }
    return currentUser;
  };

  /** @param {SignupPayload} userData */
  const handleSignup = async (userData) => {
    const currentUser = await authService.signup(userData);
    if (currentUser) {
      setIsLoggedIn(true);
      setUser(currentUser);
      setIsAdmin(currentUser.is_admin || false);
    }
    return currentUser;
  };

  const handleLogout = () => {
    authService.logout();
    setIsLoggedIn(false);
    setUser(null);
    // setIsAdmin(false);
    // navigate("/");
  };

  // Linked to createContext, see its comments above
  const authContextValue = {
    isLoggedIn,
    user,
    isAdmin,
    login: handleLogin,
    signup: handleSignup,
    logout: handleLogout,
  };

  return (
    <AuthContext.Provider value={authContextValue}>
      {children}
    </AuthContext.Provider>
  );
};
