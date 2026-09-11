import * as React from "react";

export function Table({
  children,
  className = "min-w-full bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200",
  ...props
}) {
  return (
    <table className={className} {...props}>
      {children}
    </table>
  );
}

export function TableHeader({ children, className = "bg-gray-50" }) {
  return (
    <thead
      className={`bg-gray-50 dark:bg-gray-900 text-gray-700 dark:text-gray-200 ${className}`}
    >
      {children}
    </thead>
  );
}

export function TableBody({
  children,
  className = "bg-white divide-y divide-gray-200",
}) {
  return (
    <tbody
      className={`bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 ${className}`}
    >
      {children}
    </tbody>
  );
}

export function TableRow({ children, className = "hover:bg-gray-100" }) {
  return <tr className={className}>{children}</tr>;
}

export function TableHead({
  children,
  className = "px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider",
}) {
  return <th className={className}>{children}</th>;
}

export function TableCell({
  children,
  className = "px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-400",
}) {
  return <td className={className}>{children}</td>;
}
