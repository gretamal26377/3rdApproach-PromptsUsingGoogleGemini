// Context
// Exported using * to export all named exports from a module,
// but also, because it uses named exports (export const AuthContext = ...),
// it allows importing specific exports from the module.
// For some unknown reason, the AuthContext is not being exported using the * syntax
// export * from "./context/AuthContext";
export { AuthContext } from "./context/AuthContext";
export { AuthProvider } from "./context/AuthContext";
// Components
export { default as Login } from "./components/Login";
export { default as Signup } from "./components/Signup";

// UI components
export * from "./components/ui/alert";
export { default as Badge } from "./components/ui/badge";
export { default as Button } from "./components/ui/button";
export * from "./components/ui/card";
export * from "./components/ui/carousel";
export { default as Checkbox } from "./components/ui/checkbox";
export { default as DarkModeToggle } from "./components/ui/DarkModeToggle";
export * from "./components/ui/dialog";
export * from "./components/ui/form";
export { default as Input } from "./components/ui/input";
export { default as Label } from "./components/ui/label";
export { default as ScrollArea } from "./components/ui/scroll-area";
export * from "./components/ui/table";

// Pages
export { default as LoginPage } from "./pages/LoginPage";

// Services
export { default as api } from "./services/api";
export { default as authService } from "./services/authService";

// Lib utilities
export * from "./lib/utils";
