import * as React from "react";

const Checkbox = React.forwardRef(({ className = "h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500", ...props }, ref) => (
  <input
    type="checkbox"
    className={`form-checkbox h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 dark:bg-gray-900 dark:border-gray-700 dark:checked:bg-blue-700 ${className}`}
    ref={ref}
    {...props}
  />
));

Checkbox.displayName = "Checkbox";

export default Checkbox;
