import ScrollArea from "../components/ui/scroll-area";

export default {
  title: "UI/ScrollArea",
  component: ScrollArea,
  tags: ["autodocs"],
};

export const Basic = {
  render: () => (
    <ScrollArea className="h-32 w-64 border p-2">
      <div
        style={{ height: "200px" }}
        className="text-gray-800 dark:text-gray-100"
      >
        This is a scrollable area. This text is added this way in order to see
        the scrollbar: Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut
        enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
        aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit
        in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui
        officia deserunt mollit anim id est laborum
      </div>
    </ScrollArea>
  ),
};
