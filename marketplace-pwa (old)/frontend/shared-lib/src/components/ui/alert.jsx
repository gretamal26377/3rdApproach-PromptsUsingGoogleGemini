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

export function AlertTitle({ children, className = "font-bold" }) {
  return <div className={className}>{children}</div>;
}

export function AlertDescription({ children, className = "" }) {
  return <div className={className}>{children}</div>;
}
