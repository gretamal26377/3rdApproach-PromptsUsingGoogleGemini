import * as React from "react";

export function Carousel({
  children,
  className = "relative w-full overflow-hidden",
  ...props
}) {
  // Find CarouselContent child
  const contentChild = React.Children.toArray(children).find(
    (child) => child.type && child.type.name === "CarouselContent"
  );
  if (!contentChild) {
    return (
      <div className={className} {...props}>
        No CarouselContent found
      </div>
    );
  }
  const itemCount = React.Children.count(contentChild.props.children);
  const [activeIndex, setActiveIndex] = React.useState(0);

  // Auto-advance slides every 3 seconds
  React.useEffect(() => {
    if (itemCount <= 1) return;
    const interval = setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % itemCount);
    }, 3000);
    return () => clearInterval(interval);
  }, [itemCount]);

  const goToPrev = () =>
    setActiveIndex((prev) => (prev - 1 + itemCount) % itemCount);
  const goToNext = () => setActiveIndex((prev) => (prev + 1) % itemCount);

  // Clone CarouselContent and inject props
  const content = React.cloneElement(contentChild, {
    activeIndex,
    itemCount,
  });

  return (
    <div
      className={`carousel-container bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 relative max-w-full sm:max-w-lg mx-auto`}
      style={{ position: "relative" }}
      {...props}
    >
      {/* Desktop: Transparent, fully rounded navigation buttons offset outside container, vertically centered */}
      <>
        <button
          type="button"
          onClick={goToPrev}
          className="hidden sm:flex items-center justify-center absolute -left-16 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-white/30 dark:bg-gray-800/30 text-gray-800 dark:text-gray-200 shadow hover:bg-white/40 dark:hover:bg-gray-800/40 transition-colors border border-white/20 dark:border-gray-700/20 backdrop-blur-sm"
          style={{ zIndex: 1 }}
          aria-label="Previous Slide"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
            className="w-7 h-7"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M15.75 19.5L8.25 12l7.5-7.5"
            />
          </svg>
        </button>
        <button
          type="button"
          onClick={goToNext}
          className="hidden sm:flex items-center justify-center absolute -right-16 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-white/30 dark:bg-gray-800/30 text-gray-800 dark:text-gray-200 shadow hover:bg-white/40 dark:hover:bg-gray-800/40 transition-colors border border-white/20 dark:border-gray-700/20 backdrop-blur-sm"
          style={{ zIndex: 1 }}
          aria-label="Next Slide"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
            className="w-7 h-7"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M8.25 4.5l7.5 7.5-7.5 7.5"
            />
          </svg>
        </button>
      </>
      {/* Slides/content wrapper with overflow-hidden */}
      <div className="overflow-hidden w-full">{content}</div>
      {/* Mobile Buttons (bottom, full width, transparent, fully rounded) */}
      <div className="flex sm:hidden justify-between items-center absolute left-0 right-0 bottom-2 px-4 z-10">
        <button
          type="button"
          onClick={goToPrev}
          className="w-10 h-10 rounded-full bg-white/30 dark:bg-gray-800/30 text-gray-800 dark:text-gray-200 shadow hover:bg-white/40 dark:hover:bg-gray-800/40 transition-colors flex items-center justify-center border border-white/20 dark:border-gray-700/20 backdrop-blur-sm"
          aria-label="Previous Slide"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
            className="w-6 h-6"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M15.75 19.5L8.25 12l7.5-7.5"
            />
          </svg>
        </button>
        <button
          type="button"
          onClick={goToNext}
          className="w-10 h-10 rounded-full bg-white/30 dark:bg-gray-800/30 text-gray-800 dark:text-gray-200 shadow hover:bg-white/40 dark:hover:bg-gray-800/40 transition-colors flex items-center justify-center border border-white/20 dark:border-gray-700/20 backdrop-blur-sm"
          aria-label="Next Slide"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
            className="w-6 h-6"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M8.25 4.5l7.5 7.5-7.5 7.5"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}

export function CarouselContent({
  children,
  className = "flex transition-transform duration-300 ease-in-out",
  activeIndex = 0,
  itemCount = 1,
  ...props
}) {
  // Calculate transform based on activeIndex
  const transform = `translateX(-${activeIndex * (100 / itemCount)}%)`;
  return (
    <div
      className={className}
      style={{ width: `${itemCount * 100}%`, transform }}
      {...props}
    >
      {React.Children.map(children, (child) =>
        React.cloneElement(child, { style: { width: `${100 / itemCount}%` } })
      )}
    </div>
  );
}

export function CarouselItem({
  children,
  className = "flex-shrink-0 w-full",
  ...props
}) {
  return (
    <div className={className} {...props}>
      {children}
    </div>
  );
}
