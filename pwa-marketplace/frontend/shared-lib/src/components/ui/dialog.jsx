import * as React from "react";

// Dialog context for open/close state
const DialogContext = React.createContext();

export function Dialog({ open, onOpenChange, children }) {
  const [internalOpen, setInternalOpen] = React.useState(false);
  const isControlled = open !== undefined;
  const actualOpen = isControlled ? open : internalOpen;
  const setOpen = isControlled ? onOpenChange : setInternalOpen;

  return (
    <DialogContext.Provider value={{ open: actualOpen, setOpen }}>
      {children}
    </DialogContext.Provider>
  );
}

export function DialogTrigger({ children }) {
  const { setOpen } = React.useContext(DialogContext);
  return React.cloneElement(children, {
    onClick: (e) => {
      if (children.props.onClick) children.props.onClick(e);
      setOpen(true);
    },
  });
}

export function DialogContent({
  children,
  className = "fixed inset-0 z-50 flex items-center justify-center bg-black/40",
  ...props
}) {
  const { open, setOpen } = React.useContext(DialogContext);
  if (!open) return null;
  return (
    <div className={className} {...props}>
      <div className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-700 rounded p-4 max-w-full w-full sm:w-[500px] relative">
        <button
          aria-label="Close dialog"
          className="absolute top-2 right-2 text-gray-400 hover:text-gray-700"
          onClick={() => setOpen(false)}
        >
          ×
        </button>
        {children}
      </div>
    </div>
  );
}

export function DialogHeader({ children, className = "mb-4" }) {
  return <div className={className}>{children}</div>;
}

export function DialogTitle({
  children,
  className = "text-xl font-bold mb-2",
}) {
  return <div className={className}>{children}</div>;
}

export function DialogDescription({
  children,
  className = "text-gray-600 mb-4",
}) {
  return <div className={className}>{children}</div>;
}

export function DialogFooter({
  children,
  className = "flex justify-end gap-2 mt-6",
}) {
  return <div className={className}>{children}</div>;
}
