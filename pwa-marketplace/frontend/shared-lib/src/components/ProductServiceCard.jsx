import React from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import Button from "./ui/button";
import Badge from "./ui/badge";
import { ShoppingCart } from "lucide-react";
import { cn } from "../lib/utils";

// Differentiates Workflows by presence of Store or Category Ids
const ProductServiceCard = ({
  productService,
  categoryId,
  store,
  onAddToCart,
}) => {
  const navigate = useNavigate();
  const handleViewStores = () => {
    // Navigate to Category Workflow page for this Product/Service
    navigate(`/category/${categoryId}/products-services/stores`, {
      state: { productService },
    });
  };
  return (
    <Card className="transition-transform transform hover:scale-105 hover:shadow-lg">
      <CardHeader>
        <CardTitle className="text-xl font-semibold">
          {productService.name}
        </CardTitle>
      </CardHeader>
      {store ? (
        <CardContent>
          <p className="text-gray-700 mb-2">{productService.description}</p>
          <Badge variant="outline" className="mb-2">
            Price: ${productService.price}
          </Badge>
        </CardContent>
      ) : (
        // Category Workflow: Show button to view all Stores selling this Product/Service
        <>
          <Button
            className="w-full bg-purple-500 text-white hover:bg-purple-600 transition-colors mb-2"
            onClick={handleViewStores}
          >
            Stores Selling This Product/Service
          </Button>
        </>
      )}
      {/* Store Workflow: Show Add to Cart button */}
      {/* When this component called from Admin Frontend, no need to Add to Cart button, so called without onAddToCart prop */}
      {onAddToCart && (
        <Button
          onClick={() => onAddToCart({ productService, store })}
          className={cn(
            "w-full bg-blue-500 text-white hover:bg-blue-600 transition-colors",
            "flex items-center justify-center gap-2"
          )}
        >
          <ShoppingCart className="h-4 w-4" />
          Add to Cart
        </Button>
      )}
    </Card>
  );
};

export default ProductServiceCard;
