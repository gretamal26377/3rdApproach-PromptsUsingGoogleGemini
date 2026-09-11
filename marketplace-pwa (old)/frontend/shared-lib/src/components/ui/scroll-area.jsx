import * as React from "react";

const ScrollArea = React.forwardRef(
  // The scrolling here is managed by the className "overflow-x-auto" and -x- makes it horizontal
  ({ className = "overflow-x-auto", children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={`overflow-auto bg-gray-50 dark:bg-gray-900 rounded w-full max-w-full sm:max-w-md md:max-w-lg lg:max-w-2xl xl:max-w-4xl h-auto max-h-[80vh] ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  }
);

ScrollArea.displayName = "ScrollArea";

export default ScrollArea;
