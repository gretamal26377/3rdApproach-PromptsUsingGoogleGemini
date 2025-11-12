import React from "react";
import { Link } from "react-router-dom";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "shared-lib";
import { Button } from "shared-lib";
import { cn } from "shared-lib";
import StoreCard from "./StoreCard";

const StoreList = ({ stores }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {stores.map((store) => (
        <StoreCard key={store.id} store={store} />
      ))}
    </div>
  );
};

export default StoreList;
