import * as React from "react";

export function Form({ children, className = "space-y-4", ...props }) {
  return (
    <form
      className={`bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 p-4 rounded shadow ${className}`}
      {...props}
    >
      {children}
    </form>
  );
}

export function FormField({ children }) {
  return <div className="space-y-2">{children}</div>;
}

export function FormItem({ children, className = "space-y-1" }) {
  return <div className={className}>{children}</div>;
}

export function FormLabel({
  children,
  htmlFor,
  className = "block text-sm font-medium text-gray-700",
}) {
  return (
    <label
      htmlFor={htmlFor}
      className={`block text-gray-700 dark:text-gray-200 mb-2 ${className}`}
    >
      {children}
    </label>
  );
}

export function FormControl({ children }) {
  return <div>{children}</div>;
}

export function FormMessage({
  children,
  className = "text-xs text-red-700 mt-1",
}) {
  return children ? (
    <div className={`text-red-700 dark:text-red-300 ${className}`}>
      {children}
    </div>
  ) : null;
}
