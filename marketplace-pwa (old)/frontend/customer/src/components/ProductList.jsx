import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "shared-lib"; // Adjust path if needed
import { Badge } from "shared-lib";
import { Button } from "shared-lib";
import { ShoppingCart } from "lucide-react";
import { cn } from "shared-lib";
import ProductCard from "./ProductCard";

const ProductList = ({ products, addToCart }) => {
  return (
    <div className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 rounded shadow p-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            onAddToCart={addToCart}
          />
        ))}
      </div>
    </div>
  );
};

export default ProductList;
