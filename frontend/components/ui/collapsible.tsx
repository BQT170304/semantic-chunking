import * as React from "react";

import { cn } from "@/lib/utils";

interface CollapsibleProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
  className?: string;
}

const Collapsible: React.FC<CollapsibleProps> = ({
  className,
  open = false,
  onOpenChange,
  children,
}) => {
  const [isOpen, setIsOpen] = React.useState(open);

  React.useEffect(() => {
    setIsOpen(open);
  }, [open]);

  const handleToggle = () => {
    const newOpen = !isOpen;
    setIsOpen(newOpen);
    onOpenChange?.(newOpen);
  };

  const contextValue = { isOpen, toggle: handleToggle };

  return (
    <div className={cn("", className)}>
      <CollapsibleContext.Provider value={contextValue}>
        {children}
      </CollapsibleContext.Provider>
    </div>
  );
};

const CollapsibleContext = React.createContext<{
  isOpen: boolean;
  toggle: () => void;
}>({ isOpen: false, toggle: () => {} });

const CollapsibleTrigger = React.forwardRef<
  React.ElementRef<"button">,
  React.ComponentPropsWithoutRef<"button">
>(({ className, onClick, ...props }, ref) => {
  const { toggle } = React.useContext(CollapsibleContext);

  return (
    <button
      ref={ref}
      className={cn("", className)}
      onClick={(e) => {
        toggle();
        onClick?.(e);
      }}
      {...props}
    />
  );
});
CollapsibleTrigger.displayName = "CollapsibleTrigger";

const CollapsibleContent = React.forwardRef<
  React.ElementRef<"div">,
  React.ComponentPropsWithoutRef<"div">
>(({ className, ...props }, ref) => {
  const { isOpen } = React.useContext(CollapsibleContext);

  return (
    <div
      ref={ref}
      className={cn(
        "overflow-hidden transition-all duration-300 ease-in-out",
        isOpen ? "max-h-screen opacity-100" : "max-h-0 opacity-0",
        className
      )}
      {...props}
    />
  );
});
CollapsibleContent.displayName = "CollapsibleContent";

export { Collapsible, CollapsibleTrigger, CollapsibleContent };
