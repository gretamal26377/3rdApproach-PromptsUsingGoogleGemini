import React from "react";
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from "../components/ui/form";
import Input from "../components/ui/input";
import Button from "../components/ui/button";

export default {
  title: "UI/Form",
  component: Form,
  tags: ["autodocs"],
};

export const Basic = {
  render: () => {
    const [email, setEmail] = React.useState("");
    const [submitted, setSubmitted] = React.useState(false);
    const handleSubmit = (e) => {
      e.preventDefault();
      setSubmitted(true);
    };
    return (
      <Form onSubmit={handleSubmit}>
        <FormField>
          <FormItem>
            <FormLabel htmlFor="email">Email</FormLabel>
            <FormControl>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </FormControl>
            {submitted && !email && (
              <FormMessage>Email is required</FormMessage>
            )}
          </FormItem>
        </FormField>
        <div className="flex gap-2 mt-4">
          <Button type="submit" variant="primary">
            Submit
          </Button>
          <Button type="button" variant="secondary">
            Cancel
          </Button>
          <Button
            type="reset"
            variant="outline"
            onClick={() => {
              setEmail("");
              setSubmitted(false);
            }}
          >
            Clear
          </Button>
        </div>
      </Form>
    );
  },
};
