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

const StoreCard = ({ store }) => {
  return (
    <Card className="transition-transform transform hover:scale-105 hover:shadow-lg">
      <CardHeader>
        <CardTitle className="text-2xl font-bold">{store.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-gray-700 mb-4">{store.description}</p>
        <Link to={`/stores/${store.id}`}>
          <Button className="w-full bg-blue-500 text-white hover:bg-blue-600 transition-colors">
            View Store Products
          </Button>
        </Link>
      </CardContent>
    </Card>
  );
};

export default StoreCard;
