import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { ProductServiceListingCard } from "shared-lib";
import { api } from "shared-lib";
// import { set } from "lodash";

const ProductServiceListingsPage = ({ addToCart }) => {
  const { baseProductServiceId } = useParams();
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProductListings = async () => {
      try {
        const listingsData = await api.get(
          `/products-services/${baseProductServiceId}/listings`
        );
        setListings(listingsData);
      } catch (err) {
        setError(err.message || "Failed to load product listings");
      }
      setLoading(false);
    };
    fetchProductListings();
  }, [baseProductServiceId]);

  if (loading) return <p>Loading listings...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!listings.length)
    return <p>No listings found for this product/service</p>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">{listings[0]?.name}</h1>
      <p className="text-lg text-gray-600 mb-6">{listings[0]?.description}</p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {listings.map((listing) => (
          <ProductServiceListingCard
            key={listing.id}
            listing={listing}
            onAddToCart={addToCart}
          />
        ))}
      </div>
    </div>
  );
};

export default ProductServiceListingsPage;
