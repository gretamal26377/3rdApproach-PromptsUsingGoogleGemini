import StoreCard from "./StoreCard";

// Differentiates Workflows by presence of Store or Category Ids
const StoreList = ({ categoryId, productService, stores, addToCart }) => {
  // If categoryId is present, show Stores selling Product/Service for Category Workflow
  if (categoryId) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {stores.map((s) => (
          <StoreCard
            key={s.id}
            categoryId={categoryId}
            productService={productService}
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
