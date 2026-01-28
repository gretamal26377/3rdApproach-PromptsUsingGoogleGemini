// @ts-nocheck
import React from "react";
import { useParams, useLocation } from "react-router-dom";
import ProductServiceCard from "./ProductServiceCard";

// Differentiates Workflows by presence of Store or Category Ids
const ProductServiceList = ({ productsServices, store, addToCart }) => {
  const { categoryId } = useParams();
  const location = useLocation();
  const { state } = location;

  // Use state if available, otherwise fallback to prop
  const productsServices =
    state?.categoryProductsServices || propProductsServices || [];

  return (
    <div className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 rounded shadow p-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {productsServices.map((productService) => {
          // Category Workflow: Show all Products/Services for the given Category
          if (categoryId) {
            return (
              <ProductServiceCard
                // key: Used as a unique identifier for each ProductServiceCard component in the list, usually used alongside the map function
                key={`${productService.id}-${categoryId}`}
                productService={productService}
                categoryId={categoryId}
                onAddToCart={addToCart}
              />
            );
          }
          // Store Workflow: Show Product/Service for the given Store
          return (
            <ProductServiceCard
              key={`${productService.id}-${store.id || "no-store"}`}
              productService={productService}
              store={store}
              onAddToCart={addToCart}
            />
          );
        })}
      </div>
    </div>
  );
};

export default ProductServiceList;
