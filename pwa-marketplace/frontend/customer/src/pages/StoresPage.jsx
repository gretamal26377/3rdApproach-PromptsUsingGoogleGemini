import React, { useEffect, useState } from "react";
import StoreList from "../components/StoreList";
import { api } from "shared-lib";

const StoresPage = () => {
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStores = async () => {
      try {
        setLoading(true);
        const data = await api.get("/stores");
        setStores(data);
      } catch (err) {
        setError(err.message || "Failed to load stores");
      } finally {
        setLoading(false);
      }
    };
    fetchStores();
  }, []);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="container mx-auto p-4">
      <div className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 rounded shadow p-4">
        <h1 className="text-3xl font-bold mb-6">All Stores</h1>
        <StoreList stores={stores} />
      </div>
    </div>
  );
};

export default StoresPage;
