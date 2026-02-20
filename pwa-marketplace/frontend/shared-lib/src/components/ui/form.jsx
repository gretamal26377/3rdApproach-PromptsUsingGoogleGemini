import * as React from "react";
import Label from "./label";
import { Alert } from "./alert";

/**
 * @param {{children?: React.ReactNode, className?: string} & React.FormHTMLAttributes<HTMLFormElement>} props
 */
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

/**
 * @param {{children?: React.ReactNode}} props
 */
export function FormField({ children }) {
  return <div className="space-y-2">{children}</div>;
}

/**
 * @param {{children?: React.ReactNode, className?: string}} props
 */
export function FormItem({ children, className = "space-y-1" }) {
  return <div className={className}>{children}</div>;
}

/**
 * @param {{children?: React.ReactNode, htmlFor?: string, className?: string}} props
 */
// Use the shared Label component for consistency
export function FormLabel({ children, htmlFor, className = "" }) {
  return (
    <Label htmlFor={htmlFor} className={className}>
      {children}
    </Label>
  );
}

/**
 * @param {{children?: React.ReactNode}} props
 */
export function FormControl({ children }) {
  return <div>{children}</div>;
}

/**
 * @param {{children?: React.ReactNode, className?: string}} props
 */
// Use Alert for error messages for consistent look & feel
export function FormMessage({ children, className = "text-xs mt-1" }) {
  return children ? (
    <Alert variant="destructive" className={className}>
      {children}
    </Alert>
  ) : null;
}
