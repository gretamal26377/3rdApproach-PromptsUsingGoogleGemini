import React from "react";

/**
 * ToggleSwitch UI component
 * Concordant with project style: rounded, uses Tailwind, accessible, and supports dark mode
 * Props:
 * - checked: boolean (controlled)
 * - onChange: function (event)
 * - label: string (optional)
 * - className: string (optional)
 */
export default function ToggleSwitch({
  checked,
  onChange,
  label = "",
  className = "",
}) {
  return (
    <label
      className={`flex items-center cursor-pointer gap-2 select-none ${className}`}
    >
      {/* <span> for the label */}
      <span className="text-gray-800 dark:text-gray-200 text-sm">{label}</span>
      {/* <span> for the toggle switch */}
      {/* Diff between <div> and <span> is that <span> is inline by default and
          <div> is a block starting in a new line */}
      <span className="relative">
        <input
          type="checkbox"
          checked={checked}
          onChange={onChange}
          className="sr-only peer"
        />
        {/* <div> for the track */}
        <div className="w-10 h-6 bg-gray-300 dark:bg-gray-700 rounded-full peer-focus:ring-2 peer-focus:ring-blue-500 transition-colors duration-200"></div>
        {/* <div> for the thumb */}
        <div
          className={`absolute top-0 left-0 w-6 h-6 bg-white dark:bg-gray-900 rounded-full shadow transform transition-transform duration-200 ${
            checked ? "translate-x-4" : ""
          }`}
        ></div>
      </span>
    </label>
  );
}
