import React from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "shared-lib";
import { Button } from "shared-lib";
import { Badge } from "shared-lib";
import { ShoppingCart } from "lucide-react";
import { cn } from "shared-lib";

const ProductCard = ({ product, onAddToCart }) => {
  return (
    <Card className="transition-transform transform hover:scale-105 hover:shadow-lg">
      <CardHeader>
        <CardTitle className="text-xl font-semibold">{product.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-gray-700 mb-2">{product.description}</p>
        <Badge variant="outline" className="mb-2">
          Price: ${product.price}
        </Badge>
        <Button
          onClick={() => onAddToCart(product)}
          className={cn(
            "w-full bg-blue-500 text-white hover:bg-blue-600 transition-colors",
            "flex items-center justify-center gap-2"
          )}
        >
          <ShoppingCart className="h-4 w-4" />
          Add to Cart
        </Button>
      </CardContent>
    </Card>
  );
};

export default ProductCard;
