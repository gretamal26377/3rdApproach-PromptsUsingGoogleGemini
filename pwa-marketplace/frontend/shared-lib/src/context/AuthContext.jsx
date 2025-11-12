import React, { useState, useEffect, createContext } from "react";
import authService from "../services/authService";
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
  login: () => {},
  signup: () => {},
  logout: () => {},
});

export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null); // Issue: Change user to customer
  const [isAdmin, setIsAdmin] = useState(false); // Issue: Change all logic for Role approach
  // Purpose: To navigate programmatically. For example, navigate("/login") to trigger navigating to the login page
  //const navigate = useNavigate();

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    if (currentUser) {
      setUser(currentUser);
      setIsLoggedIn(true);
      setIsAdmin(currentUser.is_admin);
    }
  }, []);

  const handleLogin = async (userData) => {
    setIsLoggedIn(true);
    setUser(userData);
    setIsAdmin(userData.is_admin);
    //navigate("/");
  };

  const handleSignup = async (userData) => {
    setIsLoggedIn(true);
    setUser(userData);
    setIsAdmin(userData.is_admin);
    //navigate("/");
  };

  const handleLogout = () => {
    authService.logout();
    setIsLoggedIn(false);
    setUser(null);
    setIsAdmin(false);
    //navigate("/");
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
