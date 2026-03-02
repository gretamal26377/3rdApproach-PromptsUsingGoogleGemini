// Admin-specific routes
import React from "react";
import { Route, Routes } from "react-router-dom";
import PlatformAdminDashboard from "./components/PlatformAdminDashboard";
import PlatformAdminUserManagement from "./components/PlatformAdminUserManagement";
import PlatformAdminOrgStoreManagement from "./components/PlatformAdminOrgStoreManagement";
import PlatformAdminProductServiceManagement from "./components/PlatformAdminProductServiceManagement";
import PlatformAdminOrderManagement from "./components/PlatformAdminOrderManagement";
import { LoginPage } from "shared-lib";

export default function AdminRoutes() {
  return (
    <Routes>
      <Route path="/admin" element={<PlatformAdminDashboard />} />
      <Route path="/admin/users" element={<PlatformAdminUserManagement />} />
      <Route
        path="/admin/orgs-stores"
        element={<PlatformAdminOrgStoreManagement />}
      />
      <Route
        path="/admin/products-services"
        element={<PlatformAdminProductServiceManagement />}
      />
      <Route path="/admin/orders" element={<PlatformAdminOrderManagement />} />
      <Route path="/admin/login" element={<LoginPage />} />
    </Routes>
  );
}
