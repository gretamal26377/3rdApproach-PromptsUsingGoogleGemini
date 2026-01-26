import React from "react";
import StoreCard from "./StoreCard";

const StoreList = ({ stores, addToCart }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {stores.map((store) => (
        <StoreCard key={store.id} store={store} addToCart={addToCart} />
      ))}
    </div>
  );
};

export default StoreList;
