import React from "react";
import Label from "./label";
import Checkbox from "./checkbox";

/**
 * ToggleSwitch UI component
 * Concordant with project style: rounded, uses Tailwind, accessible, and supports dark mode
 * Props:
 * - checked: boolean (controlled)
 * - onChange: function (event)
 * - label: string (optional)
 * - className: string (optional)
 */
/**
 * @param {{ checked: boolean, onChange: import('react').ChangeEventHandler<HTMLInputElement>, label?: string, className?: string, id?: string, [key: string]: any }} props
 */
export default function ToggleSwitch({
  checked,
  onChange,
  label = "",
  className = "",
  id,
  ...props
}) {
  return (
    <Label
      className={`flex items-center cursor-pointer gap-2 select-none ${className}`}
      htmlFor={id}
    >
      <span className="text-gray-800 dark:text-gray-200 text-sm">{label}</span>
      <span className="relative">
        <Checkbox
          id={id}
          checked={checked}
          onChange={onChange}
          className="sr-only peer"
          {...props}
        />
        <div className="w-10 h-6 bg-gray-300 dark:bg-gray-700 rounded-full peer-focus:ring-2 peer-focus:ring-blue-500 transition-colors duration-200"></div>
        <div
          className={`absolute top-0 left-0 w-6 h-6 bg-white dark:bg-gray-900 rounded-full shadow transform transition-transform duration-200 ${
            checked ? "translate-x-4" : ""
          }`}
        ></div>
      </span>
    </Label>
  );
}
