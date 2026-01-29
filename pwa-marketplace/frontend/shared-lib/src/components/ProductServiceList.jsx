// @ts-nocheck
import React from "react";
import { useParams, useLocation } from "react-router-dom";
import ProductServiceCard from "./ProductServiceCard";

// Differentiates Workflows by presence of Category Id

const ProductServiceList = ({ storesProductsServices, addToCart }) => {
  const { categoryId } = useParams();
  const location = useLocation();
  const { state } = location;

  // Use state if available, otherwise fallback to prop
  const list =
    state?.categoryStoresProductsServices || storesProductsServices || [];
  return (
    <div className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 rounded shadow p-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Category Workflow: Show all Products/Services for the given Category */}
        {categoryId
          ? list.map((productService) => (
              <ProductServiceCard
                // key: Used as a unique identifier for each ProductServiceCard component in the list, usually used alongside the map function
                key={`${productService.id}`}
                item={productService}
                categoryId={categoryId}
                onAddToCart={addToCart}
              />
            ))
          : // Store Workflow: Show Product/Service for the given Store
            list.map((storeProductService) => {
              return (
                <ProductServiceCard
                  key={`${storeProductService.id}`}
                  item={storeProductService}
                  onAddToCart={addToCart}
                />
              );
            })}
      </div>
    </div>
  );
};

export default ProductServiceList;
