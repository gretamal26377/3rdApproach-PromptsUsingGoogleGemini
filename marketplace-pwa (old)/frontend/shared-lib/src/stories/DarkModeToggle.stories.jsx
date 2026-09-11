import React from "react";
import DarkModeToggle from "../components/ui/DarkModeToggle";

export default {
  title: "UI/DarkModeToggle",
  component: DarkModeToggle,
  tags: ["autodocs"],
  parameters: {
    docs: {
      description: {
        component:
          "Docs: A toggle button for switching between light and dark mode",
      },
      page: null, // Use default autodocs page
      label: "Docs",
    },
  },
};

const Template = (args) => <DarkModeToggle {...args} />;

export const Default = Template.bind({});
Default.args = {};
