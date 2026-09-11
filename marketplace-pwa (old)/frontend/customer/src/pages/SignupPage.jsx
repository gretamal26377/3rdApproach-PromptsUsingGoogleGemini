import React, { useContext } from "react";
import { AuthContext } from "shared-lib";
import { Signup } from "shared-lib";
import { useNavigate } from "react-router-dom";

const SignupPage = () => {
  // Purpose: To bring the signup function from the AuthContext to this Component
  const { signup } = useContext(AuthContext);
  // Purpose: To navigate programmatically. For example, navigate("/login") to trigger navigating to the login page
  const navigate = useNavigate();

  const handleSignupSuccess = (user) => {
    signup(user);
    /**
     * Keep in mind that navigate redirect has priority over any component rerendering
     * (and its father and sons component rerenderings) triggered by setting any
     * var state, actually these rerenderings will be cancelled and those components are unmounted
     */
    navigate("/"); // Redirect to home page after signup
  };

  return (
    <Signup onSignup={handleSignupSuccess} /> // Pass signup function
  );
};

export default SignupPage;
