import React, { useState, useEffect, createContext } from "react";
import authService from "../services/authService";

/**
 * This lines define a JSDoc type annotation for the LoginPayload object.
 * They document the expected structure of this object.
 * They help with code completion, type checking in editors that support JSDoc and
 * improve code readability
 */
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
 * Context to manage authentication state across the application.
 * createContext is used to create a context object that can be used to share data
 * across components without having to pass props down manually at every level.
 * Initially, the context is set with default or placeholder values that later can be
 * updated by authContextValue
 */
export const AuthContext = createContext({
  isLoggedIn: false,
  user: null,
  isAdmin: false,
  isSupervisor: false,
  /**
   * Defines login function signature, it takes a single arg named payload of type LoginPayload and
   * returns a Promise that resolves to any value. This function signature (empty at the moment) accepts
   * a parameter named _payload, which is a convention to indicate that the parameter is intentionally unused.
   * Thus the function is signed but doesn't implemented yet.
   * Structuring this function this way provides a clear contract for how the function should be used in the future
   */
  login: /** @type {(payload: LoginPayload) => Promise<any>} */ (
    async (_payload) => {}
  ),
  signup: /** @type {(payload: SignupPayload) => Promise<any>} */ (
    async (_payload) => {}
  ),
  logout: () => {},
});

/**
 * JSDoc type annotation to document the props parameter of AuthProvider component.
 * This is the ReactNode type representing any valid React child element, including
 * elements, strings, numbers, fragments, portals, etc.
 */
/** @param {{ children: import('react').ReactNode }} props */
export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [isSupervisor, setIsSupervisor] = useState(false);

  const APP_TYPE = import.meta.env.VITE_APP_TYPE || "customer";

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
        if (APP_TYPE === "admin") {
          const roleCode =
            currentUser.role_code ||
            (currentUser.role && currentUser.role.role_code);
          setIsAdmin(roleCode === "admin");
          setIsSupervisor(roleCode === "supervisor");
        } else {
          setIsAdmin(false);
          setIsSupervisor(false);
        }
      }
    };
    fetchUser();
    // Cleanup function to set isMounted to false when component unmounts
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
      if (APP_TYPE === "admin") {
        const roleCode =
          currentUser.role_code ||
          (currentUser.role && currentUser.role.role_code);
        setIsAdmin(roleCode === "admin");
        setIsSupervisor(roleCode === "supervisor");
      } else {
        setIsAdmin(false);
        setIsSupervisor(false);
      }
    }
    return currentUser;
  };

  /** @param {SignupPayload} userData */
  const handleSignup = async (userData) => {
    const currentUser = await authService.signup(userData);
    if (currentUser) {
      setIsLoggedIn(true);
      setUser(currentUser);
      if (APP_TYPE === "admin") {
        const roleCode =
          currentUser.role_code ||
          (currentUser.role && currentUser.role.role_code);
        setIsAdmin(roleCode === "admin");
        setIsSupervisor(roleCode === "supervisor");
      } else {
        setIsAdmin(false);
        setIsSupervisor(false);
      }
    }
    return currentUser;
  };

  const handleLogout = () => {
    authService.logout();
    setIsLoggedIn(false);
    setUser(null);
    setIsAdmin(false);
    setIsSupervisor(false);
    // navigate("/");
  };

  // Linked to createContext, see its comments above
  const authContextValue = {
    isLoggedIn,
    user,
    isAdmin,
    isSupervisor,
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
