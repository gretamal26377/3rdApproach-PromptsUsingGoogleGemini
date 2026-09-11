/**
 * Utility function to join class names conditionally
 * ... at the beginning of classes array is named the "rest parameter", which
 * allows the function to accept any number of arguments
 */
export function cn(...classes) {
  /**
   * Boolean is shorthand for an arrow function like: item => Boolean(item)
   * When used as a filter callback, it keeps only the truthy values in an array
   * That is the opposite of falsy values like null, undefined, 0, false, NaN, and "" (empty string)
   */
  return classes.filter(Boolean).join(" ");
}
