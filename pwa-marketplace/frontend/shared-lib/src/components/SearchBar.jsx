import React, {
  useState,
  useRef,
  useEffect,
  useMemo,
  useCallback,
} from "react";
import { Link, useNavigate } from "react-router-dom";
import { Search } from "lucide-react";
import { debounce } from "lodash";
import { api } from "shared-lib";

// Props:
// - placeholder, className, onSelect(item)

const defaultPlaceholder =
  "Search for products/services, stores or categories...";

export default function SearchBar({
  placeholder = defaultPlaceholder,
  className = "",
  onSelect = null,
  maxHeight = 400, // Increased max height to accommodate more sections
}) {
  const [query, setQuery] = useState("");
  const [showResults, setShowResults] = useState(false);
  const [data, setData] = useState({
    products_services: [],
    stores: [],
    categories: [],
  });
  const [announcement, setAnnouncement] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const wrapperRef = useRef(null); // Purpose: Detecting clicks outside the component
  const [highlighted, setHighlighted] = useState(-1);

  const navigate = useNavigate();

  const debouncedSearch = useCallback(
    debounce(async (searchQuery) => {
      if (searchQuery.length < 2) {
        setData({ products_services: [], stores: [], categories: [] });
        setIsLoading(false);
        return;
      }
      try {
        const results = await api.getSearch(`/search?q=${searchQuery}`);
        setData(
          results || { products_services: [], stores: [], categories: [] }
        );
      } catch (error) {
        console.error("Search failed:", error);
        setData({ products_services: [], stores: [], categories: [] });
      } finally {
        setIsLoading(false);
      }
    }, 300), // 300ms debounce to reduce API calls to when user stops typing for >= 300ms
    [] // No dependencies, created only once
  );

  useEffect(() => {
    function onDocClick(e) {
      // If click is outside the search bar component, close the results dropdown
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setShowResults(false);
      }
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  const { products_services, stores, categories, flattenedResults } =
    useMemo(() => {
      // data?: It's modern JS syntax called Optional Chaining. It tells JS if data isn't null or undefined, then return it.
      //        If it is then return []. This prevents runtime errors when trying to access properties of null/undefined
      const ps = (data?.products_services || []).map((p) => ({
        type: "product_service",
        id: p.base_product_service_id,
        title: p.name,
        price: `From $${p.lowest_price.toFixed(2)}`,
        path: `/products-services/${p.base_product_service_id}/listings`,
        thumbnailUrl: p.thumbnail_url,
        stock: p.stock,
      }));

      const s = (data?.stores || []).map((st) => ({
        type: "store",
        id: st.id,
        title: st.name,
        description: st.description,
        path: `/stores/${st.id}`,
      }));

      const c = (data?.categories || []).map((cat) => ({
        type: "category",
        id: cat.id,
        title: cat.name,
        description: cat.description,
        path: `/categories/${cat.id}`, // Assuming a category page route
      }));

      return {
        products_services: ps,
        stores: s,
        categories: c,
        flattenedResults: [...ps, ...s, ...c],
      };
    }, [data]);

  useEffect(() => {
    if (!showResults || query.trim() === "") {
      setAnnouncement("");
      return;
    }
    const productCount = products_services.length || 0;
    const storeCount = stores.length || 0;
    const categoryCount = categories.length || 0;

    let msg = `${productCount} products/services, ${storeCount} stores, and ${categoryCount} categories found`;

    if (highlighted >= 0 && flattenedResults[highlighted]) {
      msg += ` Selected ${flattenedResults[highlighted].title}.`;
    }
    setAnnouncement(msg);
  }, [
    products_services,
    stores,
    categories,
    highlighted,
    showResults,
    query,
    flattenedResults,
  ]);

  useEffect(() => {
    if (!showResults) return;
    setHighlighted((prev) => {
      const count = flattenedResults.length;
      if (count === 0) return -1;
      if (prev < 0) return 0;
      return prev % count;
    });
  }, [flattenedResults, showResults]);

  useEffect(() => {
    if (highlighted < 0) return;
    if (!wrapperRef.current) return;
    const el = wrapperRef.current.querySelector(
      `[data-global-index="${highlighted}"]`
    );
    // if element exists and has scrollIntoView function, scroll it into view
    if (el && typeof el.scrollIntoView === "function") {
      el.scrollIntoView({ block: "nearest" });
    }
  }, [highlighted]);

  const handlePressedKey = (e) => {
    if (!showResults) return;
    const count = flattenedResults.length;
    if (count === 0) return;

    if (e.key === "ArrowDown") {
      // preventDefault(): Stops the default action of the key press
      e.preventDefault();
      setHighlighted((prev) => (prev + 1) % count);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlighted((prev) => (prev - 1 + count) % count);
    } else if (e.key === "Enter") {
      e.preventDefault();
      const idx = highlighted >= 0 ? highlighted : 0;
      if (flattenedResults[idx]) {
        const item = flattenedResults[idx];
        setShowResults(false);
        // If onSelect prop is provided, call it with the selected item, if not navigate to item's path
        if (onSelect) return onSelect(item);
        return navigate(item.path);
      }
    } else if (e.key === "Escape") {
      setShowResults(false);
    }
  };

  const handleChange = (e) => {
    const newQuery = e.target.value;
    setQuery(newQuery);
    setShowResults(true);
    setIsLoading(true);
    debouncedSearch(newQuery);
  };

  const itemClass = (isHighlighted) =>
    `block px-2 py-2 rounded hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-900 dark:text-gray-100 ${
      isHighlighted ? "bg-gray-100 dark:bg-gray-800" : ""
    }`;

  return (
    // Associate wrapperRef with the container div to detect outside clicks and highlighted item scrolling
    <div className={`w-full max-w-md relative ${className}`} ref={wrapperRef}>
      <input
        type="text"
        value={query}
        onChange={handleChange}
        onFocus={() => setShowResults(true)}
        onKeyDown={handlePressedKey}
        placeholder={placeholder}
        aria-label={placeholder}
        aria-haspopup="listbox"
        aria-expanded={showResults}
        aria-controls="search-results"
        aria-activedescendant={
          highlighted >= 0 ? `result-${highlighted}` : undefined
        }
        className="w-full pr-10 bg-white text-gray-900 dark:bg-gray-900 dark:text-gray-100 border rounded px-3 py-2"
      />
      {/* "...": It's used as a loading indicator that appears on the input's right side, every time a search is in progress */}
      {isLoading && (
        <div className="absolute right-3 top-2.5 text-gray-400">...</div>
      )}

      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {announcement}
      </div>

      {showResults && query.trim() !== "" && (
        <div
          id="search-results"
          role="listbox"
          aria-label="Search results"
          className="absolute left-0 right-0 mt-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-50 overflow-auto"
          style={{ maxHeight }}
        >
          <div className="p-2">
            {isLoading && (
              <div className="px-2 py-1 text-sm text-gray-500 dark:text-gray-400">
                Searching...
              </div>
            )}

            {!isLoading && flattenedResults.length === 0 && (
              <div className="px-2 py-1 text-sm text-gray-500 dark:text-gray-400">
                No results found for "{query}"
              </div>
            )}

            {!isLoading && products_services.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold px-2 py-1 text-gray-700 dark:text-gray-200">
                  Products & Services ({products_services.length})
                </h3>
                {products_services.map((ps) => {
                  const globalIndex = flattenedResults.findIndex(
                    (it) => it.type === "product_service" && it.id === ps.id
                  );
                  const isHighlighted = globalIndex === highlighted;
                  return (
                    <Link
                      key={`product_service-${ps.id}`}
                      to={ps.path}
                      onClick={() => setShowResults(false)}
                      data-global-index={globalIndex}
                      id={`result-${globalIndex}`}
                      role="option" // Aria role for accessibility
                      aria-selected={isHighlighted}
                      className={itemClass(isHighlighted)}
                    >
                      <div className="flex items-center gap-2 justify-between">
                        <div className="flex items-center gap-2">
                          {ps.thumbnailUrl && (
                            <img
                              src={ps.thumbnailUrl}
                              alt={ps.title}
                              className="w-8 h-8 object-cover rounded"
                            />
                          )}
                          <span className="font-medium">{ps.title}</span>
                        </div>
                        <div className="flex flex-col items-end min-w-[70px]">
                          {ps.price != null && (
                            <span className="text-sm text-gray-500 dark:text-gray-400">
                              {ps.price}
                            </span>
                          )}
                          {ps.stock != null && (
                            <span className="text-xs text-gray-400 dark:text-gray-500">
                              Stock: {ps.stock}
                            </span>
                          )}
                        </div>
                      </div>
                    </Link>
                  );
                })}
              </div>
            )}

            {!isLoading && stores.length > 0 && (
              <>
                <hr className="my-2 border-gray-200 dark:border-gray-700" />
                <div>
                  <h3 className="text-sm font-semibold px-2 py-1 text-gray-700 dark:text-gray-200">
                    Stores ({stores.length})
                  </h3>
                  {stores.map((s) => {
                    const globalIndex = flattenedResults.findIndex(
                      (it) => it.type === "store" && it.id === s.id
                    );
                    const isHighlighted = globalIndex === highlighted;
                    return (
                      <Link
                        key={`store-${s.id}`}
                        to={s.path}
                        onClick={() => setShowResults(false)}
                        data-global-index={globalIndex}
                        id={`result-${globalIndex}`}
                        role="option"
                        aria-selected={isHighlighted}
                        className={itemClass(isHighlighted)}
                      >
                        <div className="flex justify-between items-center">
                          <span className="font-medium">{s.title}</span>
                          <span className="text-sm text-gray-500 dark:text-gray-400">
                            View
                          </span>
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                          {s.description}
                        </div>
                      </Link>
                    );
                  })}
                </div>
              </>
            )}

            {!isLoading && categories.length > 0 && (
              <>
                <hr className="my-2 border-gray-200 dark:border-gray-700" />
                <div>
                  <h3 className="text-sm font-semibold px-2 py-1 text-gray-700 dark:text-gray-200">
                    Categories ({categories.length})
                  </h3>
                  {categories.map((c) => {
                    const globalIndex = flattenedResults.findIndex(
                      (it) => it.type === "category" && it.id === c.id
                    );
                    const isHighlighted = globalIndex === highlighted;
                    return (
                      <Link
                        key={`category-${c.id}`}
                        to={c.path}
                        onClick={() => setShowResults(false)}
                        data-global-index={globalIndex}
                        id={`result-${globalIndex}`}
                        role="option"
                        aria-selected={isHighlighted}
                        className={itemClass(isHighlighted)}
                      >
                        <div className="flex justify-between items-center">
                          <span className="font-medium">{c.title}</span>
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                          {c.description}
                        </div>
                      </Link>
                    );
                  })}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
