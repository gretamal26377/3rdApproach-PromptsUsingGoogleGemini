import * as React from "react";

export function Card({ children, className, ...props }) {
  return (
    <div
      className={`bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 rounded shadow p-4 $className`}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className = "mb-2" }) {
  return <div className={className}>{children}</div>;
}

export function CardTitle({ children, className = "text-lg font-semibold" }) {
  return <div className={className}>{children}</div>;
}

export function CardContent({ children, className = "mb-2" }) {
  return <div className={className}>{children}</div>;
}

export function CardFooter({ children, className = "pt-2 border-t mt-2" }) {
  return <div className={className}>{children}</div>;
}
