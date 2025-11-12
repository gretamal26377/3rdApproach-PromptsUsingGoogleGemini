import * as React from "react";

const base = "inline-block px-2 py-1 rounded-full text-xs font-semibold";
const variants = {
  outline: "bg-white border border-gray-300 text-gray-800",
  secondary: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  success: "bg-green-100 text-green-800",
  error: "bg-red-100 text-red-800",
};

const Badge = ({ children, className = "", variant = "secondary", ...props }) => (
  <span className={[base, variants[variant] || "", className].join(" ")} {...props}>
    {children}
  </span>
);

export default Badge;
