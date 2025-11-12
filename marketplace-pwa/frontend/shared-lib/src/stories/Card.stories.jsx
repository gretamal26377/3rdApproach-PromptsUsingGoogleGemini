import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from "../components/ui/card";
import Button from "../components/ui/button";

export default {
  title: "UI/Card",
  component: Card,
  tags: ["autodocs"],
  argTypes: {
    buttonVariant: {
      control: { type: "select" },
      options: ["primary", "secondary", "outline", "destructive", "ghost"],
      description: "Variant of the Button in the CardFooter",
      defaultValue: "primary",
    },
    buttonDisabled: {
      control: "boolean",
      description: "Disabled state for the Button",
      defaultValue: false,
    },
    buttonChildren: {
      control: "text",
      description: "Button label",
      defaultValue: "Action",
    },
    buttonClassName: {
      control: "text",
      description: "Additional Tailwind classes for the Button",
      defaultValue: "",
    },
    className: {
      control: "text",
      description: "Additional Tailwind classes for the Card",
      defaultValue: "",
    },
  },
};

export const Basic = {
  args: {
    buttonVariant: "primary",
    buttonDisabled: false,
    buttonChildren: "Action",
    buttonClassName: "",
    className: "",
  },
  // render: () => (...) is a flexible way to define a Storybook story with custom JSX.
  // Use it when you need more control than args: pattern provides
  render: (args) => (
    <Card className={args.className}>
      <CardHeader>
        <CardTitle>Card Title</CardTitle>
      </CardHeader>
      <CardContent>This is the card content</CardContent>
      <CardFooter>
        <Button
          variant={args.buttonVariant}
          disabled={args.buttonDisabled}
          className={args.buttonClassName}
        >
          {args.buttonChildren}
        </Button>
      </CardFooter>
    </Card>
  ),
};
