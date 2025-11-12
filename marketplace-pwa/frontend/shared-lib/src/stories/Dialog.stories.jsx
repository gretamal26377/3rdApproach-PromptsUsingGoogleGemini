import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogTrigger,
} from "../components/ui/dialog";
import Button from "../components/ui/button";

export default {
  title: "UI/Dialog",
  component: Dialog,
  tags: ["autodocs"],
};

export const Basic = {
  render: () => (
    <Dialog>
      <DialogTrigger>
        <Button>Open Dialog</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Dialog Title</DialogTitle>
          <DialogDescription>This is a dialog description</DialogDescription>
        </DialogHeader>
        <div className="my-4">Dialog body content goes here</div>
        <DialogFooter>
          <Button>Cancel</Button>
          <Button variant="primary">Confirm</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  ),
};
