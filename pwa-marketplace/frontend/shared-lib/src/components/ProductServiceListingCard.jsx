import React from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "shared-lib";
import { Button } from "shared-lib";
import { Badge } from "shared-lib";
import { ShoppingCart, Store } from "lucide-react";
import { cn } from "shared-lib";

const ProductServiceListingCard = ({ storeProductService, onAddToCart }) => {
  return (
    <Card className="flex flex-col justify-between transition-transform transform hover:scale-105 hover:shadow-lg">
      <CardHeader>
        <CardTitle className="text-xl font-semibold">
          ${storeProductService.price.toFixed(2)}
        </CardTitle>
        <CardDescription className="flex items-center gap-2 text-gray-600">
          <Store className="h-4 w-4" />
          {listing.seller_name}
          {storeProductService.store_name}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-2">
          <Badge variant="outline" className="mb-2 w-fit">
            Stock: {storeProductService.stock_quantity}
          </Badge>
          <Button
            onClick={() => onAddToCart({ storeProductService })}
            className={cn(
              "w-full bg-blue-500 text-white hover:bg-blue-600 transition-colors",
              "flex items-center justify-center gap-2"
            )}
          >
            <ShoppingCart className="h-4 w-4" />
            Add to Cart
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default ProductServiceListingCard;
