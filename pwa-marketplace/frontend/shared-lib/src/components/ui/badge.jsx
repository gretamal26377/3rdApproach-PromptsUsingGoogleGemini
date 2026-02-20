import * as React from "react";

const base = "inline-block px-2 py-1 rounded-full text-xs font-semibold";
const variants = {
  outline: "bg-white border border-gray-300 text-gray-800",
  secondary: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  success: "bg-green-100 text-green-800",
  error: "bg-red-100 text-red-800",
};

/**
 * Badge Component for displaying small status indicators or labels, with support for multiple variants and additional props
 * JSDoc types for checkJS/TypeScript: children is a React node, className is a string, variant is one of the keys in the variants object, and ...props can be any other HTML attributes for a span element
 */
const Badge = (
  /** @type {{children?: React.ReactNode, className?: string, variant?: "outline"|"secondary"|"success"|"error", [key: string]: any}} */
  { children, className = "", variant = "secondary", ...props }
) => (
  <span
    className={[base, variants[variant] || "", className].join(" ")}
    {...props}
  >
    {children}
  </span>
);

export default Badge;
