import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import ProductCard from "../components/ProductCard";
import { api } from "shared-lib";

const ProductPage = ({ addToCart }) => {
  const { productId } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProductData = async () => {
      try {
        const productData = await api.get(`/products/${productId}`);
        setProduct(productData);
        setLoading(false);
      } catch (err) {
        setError(err.message || "Failed to load product data.");
        setLoading(false);
      }
    };
    fetchProductData();
  }, [productId]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!product) return <p>Product not found.</p>;

  return (
    <div>
      <ProductCard product={product} onAddToCart={addToCart} />
    </div>
  );
};

export default ProductPage;
