import * as React from "react";

/**
 * Card Component for displaying content in a card layout, with support for header, title, content, footer, and description sections
 * JSDoc types for checkJS/TypeScript:
 * children?: React.ReactNode: This means that the component can accept any valid React node as children, which will be rendered inside the card. This allows for flexible content within the card.
 * className?: string: This means that the component can accept an optional className prop, which is a string. This allows users to pass custom CSS classes to style the card as needed.
 * Record<string, any>: This means that the component can accept any additional props, which will be passed down to the root element.
 * This is useful for allowing users to add custom attributes or event handlers without TypeScript complaining about it
 * @param {{children?: React.ReactNode, className?: string} & Record<string, any>} props
 */
export function Card(props) {
  const { children, className = "", ...rest } = props;
  return (
    <div
      className={`bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 rounded shadow p-4 ${className}`}
      {...rest}
    >
      {children}
    </div>
  );
}

/**
 * @param {{children?: React.ReactNode, className?: string}} props
 */
export function CardHeader(props) {
  const { children, className = "mb-2" } = props;
  return <div className={className}>{children}</div>;
}

/**
 * @param {{children?: React.ReactNode, className?: string}} props
 */
export function CardTitle(props) {
  const { children, className = "text-lg font-semibold" } = props;
  return <div className={className}>{children}</div>;
}

/**
 * @param {{children?: React.ReactNode, className?: string}} props
 */
export function CardContent(props) {
  const { children, className = "mb-2" } = props;
  return <div className={className}>{children}</div>;
}

/**
 * @param {{children?: React.ReactNode, className?: string}} props
 */
export function CardFooter(props) {
  const { children, className = "pt-2 border-t mt-2" } = props;
  return <div className={className}>{children}</div>;
}

/**
 * @param {{children?: React.ReactNode, className?: string}} props
 */
export function CardDescription(props) {
  const {
    children,
    className = "text-sm text-gray-500 dark:text-gray-400 mb-2",
  } = props;
  return <div className={className}>{children}</div>;
}
