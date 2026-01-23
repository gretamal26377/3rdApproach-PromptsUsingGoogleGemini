import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import StoreList from "../components/StoreList";
import { api } from "shared-lib";

// This page shows all stores selling a selected product/service from a category
const CategoryProductServiceStoresPage = ({ addToCart }) => {
  const { productServiceId } = useParams();
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    api.get(`customer/products-services/${productServiceId}/stores`)
      .then((data) => {
        setStores(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load stores");
        setLoading(false);
      });
  }, [productServiceId]);

  if (loading) return <p>Loading stores...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!stores.length) return <p>No stores found for this product/service.</p>;

  return (
    <div className="container mx-auto p-4 space-y-6">
      <h2 className="text-2xl font-semibold mb-4">Stores selling this Product/Service</h2>
      <StoreList stores={stores} addToCart={addToCart} />
    </div>
  );
};

export default CategoryProductServiceStoresPage;
