import * as React from "react";
import Label from "./label";

/**
 * Checkbox UI component with optional label, using shared Label for accessibility and consistency.
 */

/**
 * @typedef {import('react').InputHTMLAttributes<HTMLInputElement>} InputProps
 * @typedef {InputProps & { label?: React.ReactNode, className?: string }} CheckboxProps
 */

/** @type {React.ForwardRefExoticComponent<React.RefAttributes<HTMLInputElement> & CheckboxProps>} */
const Checkbox = React.forwardRef(function Checkbox(
  {
    label,
    className = "h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500",
    id,
    ...props
  },
  ref
) {
  // If label is provided, wrap input in Label for accessibility
  if (label) {
    return (
      <Label htmlFor={id} className="flex items-center gap-2 cursor-pointer">
        <input
          id={id}
          type="checkbox"
          className={`form-checkbox h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 dark:bg-gray-900 dark:border-gray-700 dark:checked:bg-blue-700 ${className}`}
          ref={ref}
          {...props}
        />
        <span>{label}</span>
      </Label>
    );
  }
  // No label: just render the input
  return (
    <input
      id={id}
      type="checkbox"
      className={`form-checkbox h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 dark:bg-gray-900 dark:border-gray-700 dark:checked:bg-blue-700 ${className}`}
      ref={ref}
      {...props}
    />
  );
});

Checkbox.displayName = "Checkbox";

export default Checkbox;
