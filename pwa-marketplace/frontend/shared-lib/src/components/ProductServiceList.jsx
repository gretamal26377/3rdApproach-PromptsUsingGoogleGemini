// @ts-nocheck
import React from "react";
import ProductServiceCard from "./ProductServiceCard";

const ProductServiceList = ({ productsServices, store, addToCart }) => {
  return (
    <div className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 rounded shadow p-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {productsServices.map((productService) => (
          <ProductServiceCard
            // key: Used as a unique identifier for each ProductServiceCard component in the list, usually used alongside the map function
            key={`${productService.id}-${store.id}`}
            productService={productService}
            store={store}
            onAddToCart={addToCart}
          />
        ))}
      </div>
    </div>
  );
};

export default ProductServiceList;
