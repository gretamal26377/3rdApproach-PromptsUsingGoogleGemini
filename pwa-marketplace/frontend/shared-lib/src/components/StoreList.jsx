import StoreCard from "./StoreCard";

// Differentiates Workflows by presence of Category Id

const StoreList = ({ categoryId, stores, addToCart }) => {
  // Category Workflow: If categoryId is present, shows Stores selling Product/Service in that Category
  if (categoryId) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {stores.map((s) => (
          <StoreCard
            key={s.id}
            categoryId={categoryId}
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
