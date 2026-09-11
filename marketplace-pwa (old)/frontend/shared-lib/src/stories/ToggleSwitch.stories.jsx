import React from "react";
// Not compatible with Storybook 9.0+. We must wait for an update to use it
// import { useArgs } from "@storybook/preview-api";
// import { useArgs } from "@storybook/blocks";
import ToggleSwitch from "../components/ui/toggle-switch";

export default {
  title: "UI/ToggleSwitch",
  component: ToggleSwitch,
  tags: ["autodocs"],
  parameters: {
    docs: {
      description: {
        component: "Docs: A toggle switch component for boolean settings",
      },
      page: null, // Use default autodocs page
      label: "Docs",
    },
  },
  argTypes: {
    checked: { control: "boolean" },
    label: { control: "text" },
  },
};

const Template = (args) => {
  // const [{ checked }, updateArgs] = useArgs();

  // const handleChange = (e) => {
  //  updateArgs({ checked: e.target.checked });
  // };

  return <ToggleSwitch {...args} />;
  // return <ToggleSwitch {...args} checked={checked} onChange={handleChange} />;
};

export const Default = Template.bind({});
Default.args = {
  checked: false,
  label: "Enable feature",
};

/*
export const Checked = Template.bind({});
Checked.args = {
  checked: true,
  label: "Enabled",
};
*/
