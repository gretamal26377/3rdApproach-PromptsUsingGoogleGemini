import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import Button from "./ui/button";
import { Link } from "react-router-dom";

// Differentiates Workflows by presence of Store or Category Ids
const StoreCard = ({ categoryId, productService, store, addToCart }) => {
  return (
    <Card className="transition-transform transform hover:scale-105 hover:shadow-lg">
      <CardHeader>
        <CardTitle className="text-2xl font-bold">{store.name}</CardTitle>
      </CardHeader>
      <CardContent>
        {store.store_pic_path && (
          <img
            src={store.store_pic_path}
            alt={store.name}
            className="w-full h-32 object-cover rounded mb-2"
          />
        )}
        <p className="text-gray-700 mb-4">{store.description}</p>
        {/* Category Workflow: Show Store selling Product/Service and Add to Cart button */}
        {categoryId ? (
          <>
            {/* When this component called from Admin Frontend, no need to Add to Cart button, so called without AddToCart prop */}
            {addToCart && (
              <Button
                className="w-full bg-green-500 text-white hover:bg-green-600 transition-colors"
                onClick={() => addToCart({ productService, store })}
              >
                Add to Cart
              </Button>
            )}
          </>
        ) : (
          // Store Workflow: Show View Store button
          <>
            <Link to={`/stores/${store.id}`}>
              <Button className="w-full bg-blue-500 text-white hover:bg-blue-600 transition-colors mb-2">
                View Store Products/Services
              </Button>
            </Link>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default StoreCard;
