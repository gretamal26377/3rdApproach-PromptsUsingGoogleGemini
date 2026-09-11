import * as React from "react";

const Label = React.forwardRef(
  (
    {
      className = "block text-sm font-medium text-gray-700",
      htmlFor,
      children,
      ...props
    },
    ref
  ) => {
    return (
      <label
        ref={ref}
        htmlFor={htmlFor}
        className={`block text-gray-700 dark:text-gray-200 mb-2 ${className}`}
        {...props}
      >
        {children}
      </label>
    );
  }
);

Label.displayName = "Label";

export default Label;
