import React from "react";

/**
 * Dropdown UI component for consistent select styling.
 * Accepts all native <select> props and children <option> elements.
 *
 * Usage:
 * <Dropdown value={...} onChange={...} ...>
 *   <option value="">Select...</option>
 *   <option value="foo">Foo</option>
 * </Dropdown>
 */
const Dropdown = React.forwardRef(({ className = "", children, ...props }, ref) => (
  <select
    ref={ref}
    className={
      [
        // Base Tailwind styles for consistent look & feel
        "w-full rounded-md border border-gray-300 px-3 py-2 text-sm bg-white dark:bg-gray-900",
        "focus:outline-none focus:ring-2 focus:ring-blue-500",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        className
      ].join(" ")
    }
    {...props}
  >
    {children}
  </select>
));

Dropdown.displayName = "Dropdown";

export default Dropdown;
