import { Alert, AlertTitle, AlertDescription } from "../components/ui/alert";

export default {
  title: "UI/Alert",
  component: Alert,
  argTypes: {
    variant: {
      control: "select",
      options: ["default", "destructive", "success"],
    },
    children: { control: "text" },
  },
  tags: ["autodocs"],
};

export const Default = {
  args: {
    variant: "default",
    children: (
      <>
        <AlertTitle>Info</AlertTitle>
        <AlertDescription>This is an info alert</AlertDescription>
      </>
    ),
  },
};

// All these stories are using Alert component as base and pass
// args: as arguments to the component. Typical way to create story variants in Storybook
export const Destructive = {
  args: {
    variant: "destructive",
    children: (
      <>
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>This is a destructive alert</AlertDescription>
      </>
    ),
  },
};

export const Success = {
  args: {
    variant: "success",
    children: (
      <>
        <AlertTitle>Success</AlertTitle>
        <AlertDescription>This is a success alert</AlertDescription>
      </>
    ),
  },
};
