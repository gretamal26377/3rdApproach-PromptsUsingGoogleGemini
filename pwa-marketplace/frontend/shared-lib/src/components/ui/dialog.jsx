import * as React from "react";
import Button from "./button";

// Dialog context for open/close state
const DialogContext = React.createContext(
  /** @type {{ open: boolean, setOpen: (open: boolean) => void }} */ ({
    open: false,
    setOpen: (open) => {},
  })
);

/**
 * Dialog Component to manage open/close State and provide context to its Children
 * @param {{ open?: boolean, onOpenChange?: (open: boolean) => void, children?: React.ReactNode }} props
 */
export function Dialog({ open, onOpenChange, children }) {
  const [internalOpen, setInternalOpen] = React.useState(false);
  const isControlled = open !== undefined;
  const actualOpen = isControlled ? open : internalOpen;
  // Ensure setOpen is always a function; default controlled handler to a no-op if not provided
  const setOpen = isControlled ? onOpenChange ?? (() => {}) : setInternalOpen;

  return (
    <DialogContext.Provider value={{ open: actualOpen, setOpen }}>
      {children}
    </DialogContext.Provider>
  );
}

/**
 * DialogTrigger component
 * @param {{ children: React.ReactElement }} props
 */
export function DialogTrigger({ children }) {
  const { setOpen } = React.useContext(DialogContext);
  return React.cloneElement(children, {
    onClick: /** @param {React.MouseEvent} e */ (e) => {
      if (children.props.onClick) children.props.onClick(e);
      // ?.: Optional chaining to call setOpen only if it exists. If not, it will simply do nothing instead of throwing an error
      setOpen?.(true);
    },
  });
}

/**
 * DialogContent component
 * @param {{ children?: React.ReactNode, className?: string, [key: string]: any }} props
 */
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
        <Button
          aria-label="Close dialog"
          className="absolute top-2 right-2 text-gray-400 hover:text-gray-700 px-2 py-0 h-7 w-7 min-w-0 min-h-0 rounded-full text-lg"
          type="button"
          onClick={() => setOpen?.(false)}
          variant="ghost"
        >
          ×
        </Button>
        {children}
      </div>
    </div>
  );
}

/**
 * DialogHeader component
 * @param {{ children?: React.ReactNode, className?: string }} props
 */
export function DialogHeader({ children, className = "mb-4" }) {
  return <div className={className}>{children}</div>;
}

/**
 * DialogTitle component
 * @param {{ children?: React.ReactNode, className?: string }} props
 */
export function DialogTitle({
  children,
  className = "text-xl font-bold mb-2",
}) {
  return <div className={className}>{children}</div>;
}

/**
 * DialogDescription component
 * @param {{ children?: React.ReactNode, className?: string }} props
 */
export function DialogDescription({
  children,
  className = "text-gray-600 mb-4",
}) {
  return <div className={className}>{children}</div>;
}

/**
 * DialogFooter component
 * @param {{ children?: React.ReactNode, className?: string }} props
 */
export function DialogFooter({
  children,
  className = "flex justify-end gap-2 mt-6",
}) {
  return <div className={className}>{children}</div>;
}
