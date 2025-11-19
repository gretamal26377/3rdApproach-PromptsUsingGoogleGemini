import React from "react";
import { hydrateRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "shared-lib";
import App from "../App";
import * as serviceWorkerRegistration from "../serviceWorker";
import "../../../globals.css";

export { render };

function render(pageContext) {
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
