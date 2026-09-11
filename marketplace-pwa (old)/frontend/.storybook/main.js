/** @type { import('@storybook/react-webpack5').StorybookConfig } */
const config = {
  stories: [
    "../admin/src/**/*.stories.@(js|jsx|ts|tsx|mdx)",
    "../customer/src/**/*.stories.@(js|jsx|ts|tsx|mdx)",
    "../shared-lib/src/**/*.stories.@(js|jsx|ts|tsx|mdx)",
  ],
  addons: [
    "@storybook/addon-webpack5-compiler-swc",
    "@storybook/addon-docs",
    // "storybook-dark-mode", // It's not recognised by Storybook 9.0+, waiting for an update
    {
      name: "@storybook/addon-styling-webpack",

      options: {
        rules: [
          {
            test: /\.css$/,
            sideEffects: true,
            use: [
              require.resolve("style-loader"),
              {
                loader: require.resolve("css-loader"),
                options: {
                  importLoaders: 1,
                },
              },
              {
                loader: require.resolve("postcss-loader"),
                options: {
                  implementation: require.resolve("postcss"),
                },
              },
            ],
          },
        ],
      },
    },
  ],
  framework: {
    name: "@storybook/react-webpack5",
    options: {},
  },
  /** For some unknown reason, global autodocs isn't enabled, so I commented this out,
   *  and I added it individually in each story file that I know it works
  parameters: {
    docs: {
      autodocs: true,
    },
  },
   */
};
export default config;
