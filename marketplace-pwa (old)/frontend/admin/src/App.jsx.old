import React, { useContext } from "react";
import { useLocation } from "react-router-dom";
import { AuthContext } from "../shared/context/AuthContext.jsx";
import AdminRoutes from "./Routes.jsx";
import { Button } from "../shared/components/ui/button.js";

function AdminNav() {
  const { isLoggedIn, isAdmin, logout } = useContext(AuthContext);
  return (
    <nav className="bg-white shadow-md p-4">
      <div className="container mx-auto flex justify-between items-center">
        <a href="/admin" className="text-xl font-bold text-gray-800">
          Admin Panel
        </a>
        <div className="flex items-center gap-4">
          {isLoggedIn && isAdmin && (
            <Button variant="outline" onClick={logout}>
              Logout
            </Button>
          )}
        </div>
      </div>
    </nav>
  );
}

function AppContent() {
  const location = useLocation();
  return (
    <div className="min-h-screen bg-gray-100">
      <AdminNav />

      <main className="container mx-auto p-4">
        <AdminRoutes />
      </main>

      <footer className="bg-gray-200 text-center p-4 mt-8">
        <p className="text-gray-600">
          &copy; {new Date().getFullYear()} Marketplace Admin Web App. All
          rights reserved
        </p>
      </footer>
    </div>
  );
}

const App = () => <AppContent />;

export default App;
