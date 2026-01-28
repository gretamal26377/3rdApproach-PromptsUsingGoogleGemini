import StoreCard from "./StoreCard";

// Differentiates Workflows by presence of Store or Category Ids
const StoreList = ({ categoryId, productServiceId, stores, addToCart }) => {
  // If categoryId is present, show Stores for Category Workflow
  if (categoryId && Array.isArray(stores)) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {stores.map((s) => (
          <StoreCard
            key={s.id}
            categoryId={categoryId}
            productServiceId={productServiceId}
            store={s}
            addToCart={addToCart}
          />
        ))}
      </div>
    );
  }
  // Store Workflow: Show Stores
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {stores.map((s) => (
        <StoreCard key={s.id} store={s} addToCart={addToCart} />
      ))}
    </div>
  );
};

export default StoreList;
