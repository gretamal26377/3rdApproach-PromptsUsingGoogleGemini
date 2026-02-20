import * as React from "react";
/**
 * Label Component for form fields, with support for forwarding refs and additional props
 */

const Label = React.forwardRef(
  /**
   * @param {any} props
   * @param {React.Ref<HTMLLabelElement>} ref
   */
  (props, ref) => {
    const {
      className = "block text-sm font-medium text-gray-700",
      htmlFor,
      children,
      ...rest
    } = props;
    return (
      <label
        ref={ref}
        htmlFor={htmlFor}
        className={`block text-gray-700 dark:text-gray-200 mb-2 ${className}`}
        {...rest}
      >
        {children}
      </label>
    );
  }
);

Label.displayName = "Label";

export default Label;
