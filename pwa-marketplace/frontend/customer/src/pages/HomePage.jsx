import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "shared-lib";
import { Button } from "shared-lib";
import { Card, CardContent, CardHeader, CardTitle } from "shared-lib";
import { Badge } from "shared-lib";
import { Carousel, CarouselContent, CarouselItem } from "shared-lib";
import { ScrollArea } from "shared-lib";
import { cn } from "shared-lib";
import { Store, ShoppingBag, ChevronRight } from "lucide-react";
import { SearchBar } from "shared-lib";

// Mock data for stores and products (replace with actual API calls)

const mockProducts = [
  {
    id: 1,
    name: "Laptop",
    description: "Powerful laptop for work and play",
    price: 1200,
    storeId: 1,
  },
  {
    id: 2,
    name: "Smartphone",
    description: "Latest smartphone with amazing features",
    price: 1000,
    storeId: 1,
  },
  {
    id: 3,
    name: "T-Shirt",
    description: "Comfortable and stylish t-shirt",
    price: 25,
    storeId: 2,
  },
  {
    id: 4,
    name: "Jeans",
    description: "Classic jeans for a perfect fit",
    price: 50,
    storeId: 2,
  },
  {
    id: 5,
    name: "Sofa",
    description: "Cozy sofa for your living room",
    price: 500,
    storeId: 3,
  },
  {
    id: 6,
    name: "Garden Tools Set",
    description: "Essential tools for gardening",
    price: 75,
    storeId: 3,
  },
  {
    id: 7,
    name: "Bestseller Novel",
    description: "A gripping novel by a renowned author",
    price: 20,
    storeId: 4,
  },
  {
    id: 8,
    name: "Mystery Thriller",
    description:
      "An exciting mystery that will keep you on the edge of your seat",
    price: 18,
    storeId: 4,
  },
  {
    id: 9,
    name: "Running Shoes",
    description: "High-performance shoes for running",
    price: 100,
    storeId: 5,
  },
  {
    id: 10,
    name: "Basketball",
    description: "Official size basketball",
    price: 30,
    storeId: 5,
  },
  {
    id: 11,
    name: "Organic Apples",
    description: "Fresh, locally grown organic apples",
    price: 5,
    storeId: 6,
  },
  {
    id: 12,
    name: "Whole Wheat Bread",
    description: "Healthy and delicious whole wheat bread",
    price: 4,
    storeId: 6,
  },
];


const HomePage = () => {
  const [stores, setStores] = useState([]);
  const [products, setProducts] = useState(mockProducts);
  const [featuredStores, setFeaturedStores] = useState([]);

  useEffect(() => {
    // Fetch featured stores from backend using generic get()
    api.get('customer/featured-stores')
      // data: Gets featured stores from api.get()
      .then((data) => {
        setFeaturedStores(data);
      })
      .catch((err) => {
        setFeaturedStores([]);
      });
    // Optionally: fetch all stores/products here as well
    // setStores([]); // If you want to fetch all stores, implement a real API call
    setProducts(mockProducts); // Keep mock for products for now
  }, []);

  const navigate = useNavigate();

  const handleSelect = (item) => navigate(item.path);

  return (
    <div className="container mx-auto p-4 space-y-8 bg-background text-text dark:bg-background-dark dark:text-text-dark min-h-screen">
      {/* Hero Section */}
      <div className="text-center">
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-800 dark:text-text-dark mb-4">
          Discover Amazing Products/Services and Stores
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-200 mb-8">
          Explore a wide variety of Products/Services from trusted Stores
        </p>
      </div>

      {/* Sticky Search Bar (now below CustomerNav, with top offset) */}
      <div className="flex justify-center sticky top-[5.5rem] md:top-20 z-20 bg-background text-text dark:bg-background-dark dark:text-text-dark py-2">
        <div className="w-full max-w-md relative">
          <SearchBar
            onSelect={handleSelect}
            placeholder="Search for Products/Services, Stores and Categories..."
          />
        </div>
      </div>

      {/* Featured Stores Carousel */}
      <section className="bg-white dark:bg-gray-900 rounded-lg p-4">
        <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2 text-text dark:text-text-dark">
          <Store className="h-6 w-6 text-blue-500" />
          Featured Stores
        </h2>
        <Carousel className="w-full overflow-hidden">
          <CarouselContent>
            {featuredStores.map((store) => (
              <CarouselItem
                key={store.id}
                className="md:basis-1/2 lg:basis-1/3"
              >
                <Card className="transition-transform transform hover:scale-105 hover:shadow-lg bg-background dark:bg-gray-800">
                  <CardHeader>
                    <CardTitle className="text-lg font-semibold text-text dark:text-text">
                      {store.name}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {store.store_pic_path && (
                      <img
                        src={store.store_pic_path}
                        alt={store.name}
                        className="w-full h-32 object-cover rounded mb-2"
                      />
                    )}
                    <p className="text-gray-700 dark:text-gray-200">
                      {store.description}
                    </p>
                  </CardContent>
                </Card>
              </CarouselItem>
            ))}
          </CarouselContent>
        </Carousel>
        <div className="text-center mt-4">
          <Button variant="outline" asChild>
            <Link to="/stores">
              View all Stores <ChevronRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </section>

      {/* Product Categories (Horizontal Scroll) */}
      <section className="bg-white dark:bg-gray-900 rounded-lg p-4">
        <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2 text-text dark:text-text">
          <ShoppingBag className="h-6 w-6 text-blue-500" />
          Product Categories
        </h2>
        <ScrollArea className="w-full">
          <div className="flex gap-4 p-4">
            {/** Issue: It must be modified to be a dynamic list of Categories coming from DB Model and links to the Category pages */}
            <Badge variant="secondary" className="whitespace-nowrap">
              Electronics
            </Badge>
            <Badge variant="secondary" className="whitespace-nowrap">
              Fashion
            </Badge>
            <Badge variant="secondary" className="whitespace-nowrap">
              Home & Garden
            </Badge>
            <Badge variant="secondary" className="whitespace-nowrap">
              Books
            </Badge>
            <Badge variant="secondary" className="whitespace-nowrap">
              Sports
            </Badge>
            <Badge variant="secondary" className="whitespace-nowrap">
              Groceries
            </Badge>
            <Badge variant="secondary" className="whitespace-nowrap">
              Toys
            </Badge>
            <Badge variant="secondary" className="whitespace-nowrap">
              Furniture
            </Badge>
            <Badge variant="secondary" className="whitespace-nowrap">
              Beauty
            </Badge>
          </div>
        </ScrollArea>
        <div className="text-center mt-4">
          <Button variant="outline" asChild>
            <a href="/products">
              View all Products <ChevronRight className="ml-2 h-4 w-4" />
              {/** Issue?: Not sure if this path works because I don't see backend call/connection */}
            </a>
          </Button>
        </div>
      </section>

      {/* Featured Products */}
      <section className="bg-white dark:bg-gray-900 rounded-lg p-4">
        <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2 text-text dark:text-text">
          <ShoppingBag className="h-6 w-6 text-blue-500" />
          Featured Products
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.slice(0, 6).map((product) => (
            <Card
              key={product.id}
              className="transition-transform transform hover:scale-105 hover:shadow-lg bg-background dark:bg-gray-800"
            >
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-text dark:text-text">
                  {product.name}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 dark:text-gray-200 mb-2">
                  {product.description}
                </p>
                <Badge variant="outline">Price: ${product.price}</Badge>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
};

export default HomePage;
