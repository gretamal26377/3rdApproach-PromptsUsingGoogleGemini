// Needed by Storybook 9.0+ for PostCSS configuration
export default {
  plugins: {
    // tailwindcss: {}, // Uncomment this line if using Tailwind CSS 3.x
    "@tailwindcss/postcss": {}, // Needed for Tailwind CSS 4+
    autoprefixer: {},
  },
};
