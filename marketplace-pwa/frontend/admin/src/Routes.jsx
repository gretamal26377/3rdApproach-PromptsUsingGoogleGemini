// Admin-specific routes
import React from "react";
import { Route, Routes } from "react-router-dom";
import AdminDashboard from "./components/AdminDashboard";
import AdminUserManagement from "./components/AdminUserManagement";
import AdminStoreManagement from "./components/AdminStoreManagement";
import AdminProductManagement from "./components/AdminProductManagement";
import AdminOrderManagement from "./components/AdminOrderManagement";
import { LoginPage } from "shared-lib";

export default function AdminRoutes() {
  return (
    <Routes>
      <Route path="/admin" element={<AdminDashboard />} />
      <Route path="/admin/users" element={<AdminUserManagement />} />
      <Route path="/admin/stores" element={<AdminStoreManagement />} />
      <Route path="/admin/products" element={<AdminProductManagement />} />
      <Route path="/admin/orders" element={<AdminOrderManagement />} />
      <Route path="/admin/login" element={<LoginPage />} />
    </Routes>
  );
}
