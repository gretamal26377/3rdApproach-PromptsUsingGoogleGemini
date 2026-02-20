import * as React from "react";

/**
 * ScrollArea Component for displaying scrollable content, with support for forwarding refs and additional props
 * JSDoc types for checkJS/TypeScript: children is a React node, className is a string, and ...props can be any other HTML attributes for a div element
 */

/**
 * @typedef {{ children?: React.ReactNode, className?: string, direction?: "vertical" | "horizontal" | "both" } & React.HTMLAttributes<HTMLDivElement>} ScrollAreaProps
 */

/** @type {React.ForwardRefExoticComponent<React.PropsWithoutRef<ScrollAreaProps> & React.RefAttributes<HTMLDivElement>>} */
const ScrollArea = React.forwardRef(
  /**
   * @param {ScrollAreaProps} props
   * @param {React.Ref<HTMLDivElement>} ref
   */
  ({ className = "", direction = "vertical", children, ...props }, ref) => {
    // Determine overflow classes based on direction
    let overflowClass = "";
    if (direction === "vertical") {
      overflowClass = "overflow-y-auto";
    } else if (direction === "horizontal") {
      overflowClass = "overflow-x-auto";
    } else if (direction === "both") {
      overflowClass = "overflow-auto";
    }
    return (
      <div
        ref={ref}
        className={`bg-gray-50 dark:bg-gray-900 rounded w-full max-w-full sm:max-w-md md:max-w-lg lg:max-w-2xl xl:max-w-4xl h-auto max-h-[80vh] ${overflowClass} ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  }
);

ScrollArea.displayName = "ScrollArea";

export default ScrollArea;
