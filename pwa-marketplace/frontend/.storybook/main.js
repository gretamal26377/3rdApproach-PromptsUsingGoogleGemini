/** @type { import('@storybook/react-vite').StorybookConfig } */
export default {
  stories: [
    "../admin/src/**/*.stories.@(js|jsx|ts|tsx|mdx)",
    "../customer/src/**/*.stories.@(js|jsx|ts|tsx|mdx)",
    "../shared-lib/src/**/*.stories.@(js|jsx|ts|tsx|mdx)",
  ],
  addons: [
    // "@storybook/addon-docs",
    // "@storybook/addon-onboarding",
    "@storybook/addon-links",
    // "@storybook/addon-essentials",
    // "@storybook/addon-interactions",
    // "storybook-dark-mode", // It's not recognised by Storybook 9.0+, waiting for an update
  ],
  framework: {
    name: "@storybook/react-vite", // or "@storybook/vue-vite", etc.
    options: {},
  },
  /**
  core: {
    builder: "@storybook/builder-vite",
  },
  docs: {
    autodocs: "tag",
  },
  async viteFinal(config) {
    return mergeConfig(config, {
      // Your custom Vite configuration here
    });
  },
  */
};
