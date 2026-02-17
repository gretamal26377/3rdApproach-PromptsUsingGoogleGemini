import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import ProductServiceList from "shared-lib";
import { api } from "shared-lib";

const StorePage = ({ addToCart }) => {
  const { storeId } = useParams();
  const [store, setStore] = useState(null);
  const [productsServices, setProductsServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStoreData = async () => {
      try {
        setLoading(true); // Set loading to true before fetching data
        const storeData = await api.get(`stores/${storeId}`);
        setStore(storeData);
        const productsServicesData = await api.get(
          `store-products-services/${storeId}`
        );
        setProductsServices(productsServicesData);
        setLoading(false);
      } catch (err) {
        setError(err.message || "Failed to load store data");
        setLoading(false);
      }
    };
    fetchStoreData();
  }, [storeId]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!store) return <p>Store not found</p>;

  return (
    <div className="container mx-auto p-4 space-y-6">
      <div className="bg-white shadow-md rounded-lg p-6">
        <h1 className="text-3xl font-bold">{store.name}</h1>
        {store.store_pic_path && (
          <img
            src={store.store_pic_path}
            alt={store.name}
            className="w-full h-40 object-cover rounded mb-4"
          />
        )}
        <p className="text-gray-600">{store.description}</p>
      </div>

      <section>
        <h2 className="text-2xl font-semibold mb-4">
          Products & Services from {store.name}
        </h2>
        <ProductServiceList
          productsServices={productsServices}
          store={store}
          addToCart={addToCart}
        />
      </section>
    </div>
  );
};

export default StorePage;
