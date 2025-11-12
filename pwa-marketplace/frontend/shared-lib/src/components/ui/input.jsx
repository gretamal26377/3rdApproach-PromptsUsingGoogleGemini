import * as React from "react";

const Input = React.forwardRef(({ className = "", ...props }, ref) => {
  return (
    <input
      className={`block w-full rounded-md shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 text-sm py-3 ${className}`}
      ref={ref}
      {...props}
    />
  );
});

Input.displayName = "Input";

export default Input;
