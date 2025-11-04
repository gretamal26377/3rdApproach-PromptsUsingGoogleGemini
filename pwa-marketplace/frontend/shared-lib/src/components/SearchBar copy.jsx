import React, { useState, useRef, useEffect, useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Search } from "lucide-react";

// Props:
// - items: { stores: [], products: [] } or a flattened array of items with { type, id, title, description, path, price }
// - fetcher(query): optional async function(query) => { stores:[], products:[] } for server-side search
// - placeholder, className, onSelect(item)

const defaultPlaceholder = "Search for products/services or stores...";

export default function SearchBar({
  items = null,
  fetcher = null,
  placeholder = defaultPlaceholder,
  className = "",
  onSelect = null,
  maxHeight = 240,
}) {
  const [query, setQuery] = useState("");
  const [showResults, setShowResults] = useState(false);
  const [data, setData] = useState(items);
  const [announcement, setAnnouncement] = useState("");
  const wrapperRef = useRef(null);
  const resultsRef = useRef(null);
  const [highlighted, setHighlighted] = useState(-1);

  const navigate = useNavigate();

  useEffect(() => {
    if (!items && fetcher) {
      let mounted = true;
      fetcher("")
        .then((res) => mounted && setData(res))
        .catch(() => {});
      return () => (mounted = false);
    } else {
      setData(items);
    }
  }, [items, fetcher]);

  useEffect(() => {
    function onDocClick(e) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setShowResults(false);
      }
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  const { filteredStores, filteredProducts, flattenedResults } = useMemo(() => {
    const stores =
      (data && data.stores) ||
      (Array.isArray(data) ? data.filter((i) => i.type === "store") : []);
    const products =
      (data && data.products) ||
      (Array.isArray(data) ? data.filter((i) => i.type === "product") : []);
    const q = (query || "").trim().toLowerCase();

    const fs = stores.filter((s) =>
      q === ""
        ? true
        : ((s.name || s.title || "") + " " + (s.description || ""))
            .toLowerCase()
            .includes(q)
    );
    const fp = products.filter((p) =>
      q === ""
        ? true
        : ((p.name || p.title || "") + " " + (p.description || ""))
            .toLowerCase()
            .includes(q)
    );

    const flatStores = fs.map((s) => ({
      type: "store",
      id: s.id,
      title: s.name || s.title,
      description: s.description || "",
      path: s.path || `/stores/${s.id}`,
    }));
    const flatProducts = fp.map((p) => ({
      type: "product",
      id: p.id,
      title: p.name || p.title,
      description: p.description || "",
      path: p.path || `/products/${p.id}`,
      price: p.price,
    }));
    return {
      filteredStores: fs,
      filteredProducts: fp,
      flattenedResults: [...flatStores, ...flatProducts],
    };
  }, [data, query]);

  useEffect(() => {
    if (!showResults || query.trim() === "") {
      setAnnouncement("");
      return;
    }
    const storeCount = filteredStores.length || 0;
    const productCount = filteredProducts.length || 0;
    let msg = `${storeCount} store${
      storeCount !== 1 ? "s" : ""
    } and ${productCount} product${productCount !== 1 ? "s" : ""} found`;
    if (highlighted >= 0 && flattenedResults[highlighted]) {
      msg += ` Selected ${flattenedResults[highlighted].title}.`;
    }
    setAnnouncement(msg);
  }, [
    filteredStores,
    filteredProducts,
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
    if (el && typeof el.scrollIntoView === "function") {
      el.scrollIntoView({ block: "nearest" });
    }
  }, [highlighted]);

  const handleKeyDown = (e) => {
    if (!showResults) return;
    const count = flattenedResults.length;
    if (count === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlighted((prev) => {
        const current = prev < 0 ? 0 : prev;
        return (current + 1) % count;
      });
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlighted((prev) => {
        const current = prev < 0 ? 0 : prev;
        return (current - 1 + count) % count;
      });
    } else if (e.key === "Enter") {
      e.preventDefault();
      const idx = highlighted >= 0 ? highlighted : 0;
      if (flattenedResults[idx]) {
        const item = flattenedResults[idx];
        setShowResults(false);
        if (onSelect) return onSelect(item);
        return navigate(item.path);
      }
    } else if (e.key === "Escape") {
      setShowResults(false);
    }
  };

  const handleChange = (e) => {
    setQuery(e.target.value);
    setShowResults(true);
  };

  const itemClass = (isHighlighted) =>
    `block px-2 py-2 rounded hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-900 dark:text-gray-100 ${
      isHighlighted ? "bg-gray-100 dark:bg-gray-800" : ""
    }`;

  return (
    <div className={`w-full max-w-md relative ${className}`} ref={wrapperRef}>
      <input
        type="text"
        value={query}
        onChange={handleChange}
        onFocus={() => setShowResults(true)}
        onKeyDown={handleKeyDown}
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

      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {announcement}
      </div>

      {showResults && query.trim() !== "" && (
        <div
          id="search-results"
          ref={resultsRef}
          role="listbox"
          aria-label="Search results"
          className="absolute left-0 right-0 mt-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-50 overflow-auto"
          style={{ maxHeight }}
        >
          <div className="p-2">
            <div>
              <h3 className="text-sm font-semibold px-2 py-1 text-gray-700 dark:text-gray-200">
                Stores ({filteredStores.length})
              </h3>
              {filteredStores.length === 0 ? (
                <div className="px-2 py-1 text-sm text-gray-500 dark:text-gray-400">
                  No stores found
                </div>
              ) : (
                filteredStores.map((s) => {
                  const globalIndex = flattenedResults.findIndex(
                    (it) => it.type === "store" && it.id === s.id
                  );
                  const isHighlighted = globalIndex === highlighted;
                  return (
                    <Link
                      key={s.id}
                      to={s.path || `/stores/${s.id}`}
                      onClick={() => setShowResults(false)}
                      data-global-index={globalIndex}
                      id={`result-${globalIndex}`}
                      role="option"
                      aria-selected={isHighlighted}
                      className={itemClass(isHighlighted)}
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{s.name || s.title}</span>
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          View
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        {s.description}
                      </div>
                    </Link>
                  );
                })
              )}
            </div>

            <hr className="my-2 border-gray-200 dark:border-gray-700" />

            <div>
              <h3 className="text-sm font-semibold px-2 py-1 text-gray-700 dark:text-gray-200">
                Products & Services ({filteredProducts.length})
              </h3>
              {filteredProducts.length === 0 ? (
                <div className="px-2 py-1 text-sm text-gray-500 dark:text-gray-400">
                  No products found
                </div>
              ) : (
                filteredProducts.map((p) => {
                  const globalIndex = flattenedResults.findIndex(
                    (it) => it.type === "product" && it.id === p.id
                  );
                  const isHighlighted = globalIndex === highlighted;
                  return (
                    <Link
                      key={p.id}
                      to={p.path || `/products/${p.id}`}
                      onClick={() => setShowResults(false)}
                      data-global-index={globalIndex}
                      id={`result-${globalIndex}`}
                      role="option"
                      aria-selected={isHighlighted}
                      className={itemClass(isHighlighted)}
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{p.name || p.title}</span>
                        {p.price != null && (
                          <span className="text-sm text-gray-500 dark:text-gray-400">
                            ${p.price}
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        {p.description}
                      </div>
                    </Link>
                  );
                })
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
