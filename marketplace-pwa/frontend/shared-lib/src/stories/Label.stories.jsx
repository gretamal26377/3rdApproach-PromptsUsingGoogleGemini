import Label from "../components/ui/label";

export default {
  title: "UI/Label",
  component: Label,
  argTypes: {
    htmlFor: { control: "text" },
    children: { control: "text" },
  },
  tags: ["autodocs"],
};

export const Default = {
  args: {
    htmlFor: "Input",
    children: "Label Text",
  },
};
