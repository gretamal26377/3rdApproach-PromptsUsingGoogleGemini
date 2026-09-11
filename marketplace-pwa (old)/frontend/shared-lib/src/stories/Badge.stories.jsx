import Badge from "../components/ui/badge";

export default {
  title: "UI/Badge",
  component: Badge,
  argTypes: {
    variant: {
      control: "select",
      options: ["secondary", "outline", "success", "error"],
    },
    children: { control: "text" },
  },
  tags: ["autodocs"],
};

export const Secondary = {
  args: { variant: "secondary", children: "Secondary Badge" },
};
export const Outline = {
  args: { variant: "outline", children: "Outline Badge" },
};
export const Success = {
  args: { variant: "success", children: "Success Badge" },
};
export const Error = { args: { variant: "error", children: "Error Badge" } };
