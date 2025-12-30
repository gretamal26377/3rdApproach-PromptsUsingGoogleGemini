import React from "react";
import { hydrateRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "shared-lib";
import App from "../App";
import * as serviceWorkerRegistration from "../serviceWorker";
import "../../../globals.css";

export { render };

// pageContext: Parameter passed by vite-plugin-ssr. Purpose: To pass information about the page being rendered,
// such as the URL, route parameters, and any other data needed for client-side rendering 
function render(pageContext) {  // eslint-disable-line no-unused-vars
  hydrateRoot(
    document.getElementById("root"),
    <React.StrictMode>
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </React.StrictMode>
  );
  serviceWorkerRegistration.register();
}
