// @ts-nocheck
import React, { useContext } from "react";
import { AuthContext } from "shared-lib";
import { Signup } from "shared-lib";
import { useNavigate } from "react-router-dom";

const SignupPage = () => {
  // Purpose: To bring the signup function from the AuthContext to this Component
  const { signup } = useContext(AuthContext);
  // Purpose: To navigate programmatically. For example, navigate("/login") to trigger navigating to the login page
  const navigate = useNavigate();
  
  const APP_TYPE = (import.meta.env.VITE_APP_TYPE || "customer").toLowerCase();

  const handleSignup = async (payload) => {
    const created = await signup(payload);
    // Redirect only for the customer app; admins typically stay on the user creation screen
    if (APP_TYPE === "customer") {
      /**
       * Keep in mind that navigate redirect has priority over any component rerendering
       * (and its father and sons component rerendering) triggered by setting any
       * var state, actually these rerendering will be cancelled and those components are unmounted
       */
      navigate("/");
    }
    // Return the created customer or user in case the caller component needs it
    return created;
  };

  return (
    <Signup onSignup={handleSignup} /> // Pass signup function
  );
};

export default SignupPage;
