import * as React from "react";

const base =
  "flex items-start gap-3 p-4 rounded border text-sm bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200";
const variants = {
  default:
    "bg-blue-50 border-blue-200 text-blue-800 dark:bg-blue-950 dark:border-blue-700 dark:text-blue-200",
  destructive:
    "bg-red-50 border-red-200 text-red-800 dark:bg-red-950 dark:border-red-700 dark:text-red-200",
  success:
    "bg-green-50 border-green-200 text-green-800 dark:bg-green-950 dark:border-green-700 dark:text-green-200",
};

/**
 * @typedef {{children?: React.ReactNode, className?: string, variant?: "default"|"destructive"|"success"}} AlertProps
 */

/**
 * Alert Component for displaying important messages or notifications, with support for multiple variants and additional props
 * JSDoc types for checkJS/TypeScript: children is a React node, className is a string, variant is one of "default", "destructive", or "success", and ...props can be any other HTML attributes for a div element
 * @param {AlertProps & React.HTMLAttributes<HTMLDivElement>} props
 */
export function Alert({
  children,
  className = "",
  variant = "default",
  ...props
}) {
  return (
    <div
      className={[base, variants[variant] || "", className].join(" ")}
      {...props}
    >
      {children}
    </div>
  );
}

/**
 * AlertTitle Component for displaying the title of an alert, with support for custom styling through className
 * JSDoc types for checkJS/TypeScript: children is a React node, className is a string, and ...props can be any other HTML attributes for a div element
 * @param {{children?: React.ReactNode, className?: string}} props
 */
export function AlertTitle({ children, className = "font-bold" }) {
  return <div className={className}>{children}</div>;
}

/**
 * @param {{children?: React.ReactNode, className?: string}} props
 */
export function AlertDescription({ children, className = "" }) {
  return <div className={className}>{children}</div>;
}
