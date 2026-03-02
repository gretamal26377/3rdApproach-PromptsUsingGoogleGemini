// Admin-specific routes
import React from "react";
import { Route, Routes } from "react-router-dom";
import OrgAdminDashboard from "./components/OrgAdminDashboard";
import OrgAdminUserManagement from "./components/OrgAdminUserManagement";
import OrgAdminOrgStoreManagement from "./components/OrgAdminOrgStoreManagement";
import OrgAdminProductServiceManagement from "./components/OrgAdminProductServiceManagement";
import OrgAdminOrderManagement from "./components/OrgAdminOrderManagement";
import { LoginPage } from "shared-lib";

export default function AdminRoutes() {
  return (
    <Routes>
      <Route path="/admin" element={<OrgAdminDashboard />} />
      <Route path="/admin/users" element={<OrgAdminUserManagement />} />
      <Route
        path="/admin/orgs-stores"
        element={<OrgAdminOrgStoreManagement />}
      />
      <Route
        path="/admin/products-services"
        element={<OrgAdminProductServiceManagement />}
      />
      <Route path="/admin/orders" element={<OrgAdminOrderManagement />} />
      <Route path="/admin/login" element={<LoginPage />} />
    </Routes>
  );
}
