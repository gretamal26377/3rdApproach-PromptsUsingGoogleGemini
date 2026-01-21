import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import ProductServiceCard from "../components/ProductServiceCard";
import { api } from "shared-lib";

const ProductServicePage = ({ addToCart }) => {
  const { productServiceId } = useParams();
  const [productService, setProductService] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProductServiceData = async () => {
      try {
        const productServiceData = await api.get(`products-services/${productServiceId}`);
        setProductService(productServiceData);
        setLoading(false);
      } catch (err) {
        setError(err.message || "Failed to load product/service data");
        setLoading(false);
      }
    };
    fetchProductServiceData();
  }, [productServiceId]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!productService) return <p>Product/Service not found</p>;

  return (
    <div>
      <ProductServiceCard productService={productService} onAddToCart={addToCart} />
    </div>
  );
};

export default ProductServicePage;
