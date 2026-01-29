import React from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import Button from "./ui/button";
import Badge from "./ui/badge";
import { ShoppingCart } from "lucide-react";
import { cn } from "../lib/utils";

// Differentiates Workflows by presence of Category Id

const ProductServiceCard = ({
  item
  categoryId,
  onAddToCart,
}) => {
  const navigate = useNavigate();
  const handleViewStores = () => {
    // Navigate to Category Workflow page for this Item = Product/Service
    navigate(`/category/${categoryId}/products-services/stores`, {
      state: { item },
    });
  };
  return (
    <Card className="transition-transform transform hover:scale-105 hover:shadow-lg">
      <CardHeader>
        <CardTitle className="text-xl font-semibold">
          {item.name}
        </CardTitle>
      </CardHeader>
      {!categoryId ? (
        // Store Workflow: Show Item = Store Product/Service details
        <CardContent>
          <p className="text-gray-700 mb-2">
            {item.description}
          </p>
          <Badge variant="outline" className="mb-2">
            Price: ${item.price}
          </Badge>
        </CardContent>
      ) : (
        // Category Workflow: Show button to view all Stores selling this Item = Product/Service
        <>
          <Button
            className="w-full bg-purple-500 text-white hover:bg-purple-600 transition-colors mb-2"
            onClick={handleViewStores}
          >
            Stores Selling Product/Service
          </Button>
        </>
      )}
      {/* Store Workflow: Show Add to Cart button for this Item = Store Product/Service */}
      {/* When this component called from Admin Frontend, no need to Add to Cart button, so called without onAddToCart prop */}
      {!categoryId && onAddToCart && (
        <Button
          onClick={() => onAddToCart({ item })}
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
