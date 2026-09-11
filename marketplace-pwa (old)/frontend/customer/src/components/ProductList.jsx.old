import React from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { cn } from "../lib/utils";
// Issue: addToCart prop is missing here. It should be added to the component props and used in the Button onClick event
const ProductList = ({ products, storeName }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {products.map((product) => (
        <Card
          key={product.id}
          className="transition-transform transform hover:scale-105 hover:shadow-lg"
        >
          <CardHeader>
            <CardTitle className="text-lg font-semibold">
              <Link
                to={`/products/${product.id}`}
                {/** Issue?: Not sure if this path works because I don't see backend call/connection */}
                className="hover:text-blue-500"
              >
                {product.name}
              </Link>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 mb-2">{product.description}</p>
            <Badge variant="outline" className="mb-2">
              Price: ${product.price}
            </Badge>
            {storeName && (
              <Badge variant="secondary" className="mb-2">
                Store: {storeName}
              </Badge>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default ProductList;
