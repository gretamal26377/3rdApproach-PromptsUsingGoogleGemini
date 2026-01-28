import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import StoreList from "../../../shared-lib/src/components/StoreList";
import { api } from "shared-lib";

// This page shows all Stores selling a selected Product/Service from a Category
const CategoryProductServiceStoresPage = ({ addToCart }) => {
  const { categoryId, productServiceId } = useParams();
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    api.get(`products-services/${productServiceId}/stores`)
      .then((data) => {
        setStores(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load Stores");
        setLoading(false);
      });
  }, [productServiceId]);

  if (loading) return <p>Loading Stores...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!stores.length) return <p>No Stores found for this Product/Service</p>;

  return (
    <div className="container mx-auto p-4 space-y-6">
      <h2 className="text-2xl font-semibold mb-4">Stores selling this Product/Service</h2>
      <StoreList categoryId={categoryId} productServiceId={productServiceId} stores={stores} addToCart={addToCart} />
    </div>
  );
};

export default CategoryProductServiceStoresPage;
