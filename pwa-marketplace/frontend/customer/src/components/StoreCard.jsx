import React from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "shared-lib";
import { Button } from "shared-lib";
import { Link } from "react-router-dom";
import { cn } from "shared-lib";

const StoreCard = ({ store, addToCart }) => {
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
        <Link to={`/stores/${store.id}`}>
          <Button className="w-full bg-blue-500 text-white hover:bg-blue-600 transition-colors mb-2">
            View Store Products
          </Button>
        </Link>
        {addToCart && (
          <Button
            className="w-full bg-green-500 text-white hover:bg-green-600 transition-colors"
            onClick={() => addToCart(store)}
          >
            Add to Cart
          </Button>
        )}
      </CardContent>
    </Card>
  );
};

export default StoreCard;
