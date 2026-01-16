import React, { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import Login from "../components/Login"; // Import Login Component
import { useNavigate } from "react-router-dom";

const LoginPage = () => {
  // Purpose: To bring the login function from the AuthContext to this component
  const { login } = useContext(AuthContext);
  // Purpose: To navigate programmatically. For example, navigate("/login") to trigger navigating to the login page
  // const navigate = useNavigate();

  const handleLoginSuccess = (user) => {
    // keep an eye this login function from AuthContext is different from defined in authService.login
    login(user);
    // After successful login, comeback to father component that called this component
    // navigate("/");
  };

  return (
    <Login onLogin={handleLoginSuccess} /> // Pass the login function as a prop to Login component
  );
};

export default LoginPage;
