import React, { useState, useCallback, useRef } from 'react';
import { api } from 'shared-lib';
import { Link } from 'react-router-dom';
import { debounce } from 'lodash';

const SearchBar = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const debouncedSearch = useCallback(
    debounce(async (searchQuery) => {
      if (searchQuery.length < 2) {
        setResults([]);
        setIsLoading(false);
        return;
      }
      try {
        const searchResults = await api.get(`/search?q=${searchQuery}`);
        setResults(searchResults);
        setError(null);
      } catch (err) {
        setError('Search failed. Please try again.');
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 300),
    []
  );

  const handleChange = (e) => {
    const { value } = e.target;
    setQuery(value);
    setIsLoading(true);
    debouncedSearch(value);
  };

  return (
    <div className="relative w-full max-w-xl mx-auto">
      <input
        type="text"
        value={query}
        onChange={handleChange}
        placeholder="Search for products..."
        className="w-full px-4 py-2 border border-gray-300 rounded-full shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      {isLoading && <div className="absolute right-3 top-2 text-gray-400">Loading...</div>}
      
      {error && <div className="absolute w-full mt-1 text-red-500 bg-white border border-gray-300 rounded-md shadow-lg z-10 p-2">{error}</div>}

      {results.length > 0 && (
        <ul className="absolute w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-10">
          {results.map((product) => (
            <li key={product.base_product_service_id} className="hover:bg-gray-100">
              <Link 
                to={`/products/${product.base_product_service_id}/listings`}
                className="flex items-center p-2"
              >
                <img src={product.image_url || 'https://via.placeholder.com/50'} alt={product.name} className="w-12 h-12 object-cover mr-4 rounded"/>
                <div>
                  <div className="font-semibold">{product.name}</div>
                  <div className="text-sm text-gray-600">from ${product.best_price.toFixed(2)}</div>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SearchBar;
