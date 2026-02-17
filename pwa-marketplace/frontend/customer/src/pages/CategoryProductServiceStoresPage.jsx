import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import StoreList from "shared-lib";
import { api } from "shared-lib";
import { useLocation } from "react-router-dom";

// This page shows all Stores selling a selected Product/Service from a Category
const CategoryProductServiceStoresPage = ({ addToCart }) => {
  const { categoryId } = useParams();
  const [productServiceStores, setProductServiceStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const location = useLocation();
  const { state } = location;
  const productService = state?.productService || null;
  useEffect(() => {
    setLoading(true);
    api.get(`products-services/${productService.id}/stores`)
      .then((data) => {
        setProductServiceStores(data.product_service_stores);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load Stores");
        setLoading(false);
      });
  }, [productService]);

  if (loading) return <p>Loading Stores...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!productServiceStores.length) return <p>No Stores found for this Product/Service</p>;

  return (
    <div className="container mx-auto p-4 space-y-6">
      <h2 className="text-2xl font-semibold mb-4">Stores selling this Product/Service</h2>
      <StoreList categoryId={categoryId} stores={productServiceStores} addToCart={addToCart} />
    </div>
  );
};

export default CategoryProductServiceStoresPage;
