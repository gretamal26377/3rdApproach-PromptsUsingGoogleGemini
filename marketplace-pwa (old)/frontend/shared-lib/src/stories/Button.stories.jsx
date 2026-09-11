import React from "react";
import { action } from "storybook/actions";
import Button from "../components/ui/button";

export default {
  title: "UI/Button",
  component: Button,
  argTypes: {
    variant: {
      control: { type: "select" },
      options: ["primary", "secondary", "outline", "destructive", "ghost"],
    },
    disabled: { control: "boolean" },
    children: { control: "text" },
    onClick: { action: "clicked" },
    onFocus: { action: "focused" },
    onBlur: { action: "blurred" },
  },
  tags: ["autodocs"],
};

const Template = (args) => <Button {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  variant: "primary",
  children: "Primary Button",
  onClick: action("clicked"),
  onFocus: action("focused"),
  onBlur: action("blurred"),
};

export const Secondary = Template.bind({});
Secondary.args = {
  variant: "secondary",
  children: "Secondary Button",
  onClick: action("clicked"),
  onFocus: action("focused"),
  onBlur: action("blurred"),
};

export const Outline = Template.bind({});
Outline.args = {
  variant: "outline",
  children: "Outline Button",
  onClick: action("clicked"),
  onFocus: action("focused"),
  onBlur: action("blurred"),
};

export const Destructive = Template.bind({});
Destructive.args = {
  variant: "destructive",
  children: "Destructive Button",
  onClick: action("clicked"),
  onFocus: action("focused"),
  onBlur: action("blurred"),
};

export const Ghost = Template.bind({});
Ghost.args = {
  variant: "ghost",
  children: "Ghost Button",
  onClick: action("clicked"),
  onFocus: action("focused"),
  onBlur: action("blurred"),
};

export const Disabled = Template.bind({});
Disabled.args = {
  variant: "primary",
  children: "Disabled Button",
  disabled: true,
  onClick: action("clicked"),
  onFocus: action("focused"),
  onBlur: action("blurred"),
};
