import React, { useState, useEffect, useContext } from "react";
import { Routes, Route, useLocation, Link } from "react-router-dom";
import { AuthContext } from "shared-lib";
import CustomerRoutes from "./Routes";
import { Button } from "shared-lib";
import { ShoppingCart } from "lucide-react";
import { authService } from "shared-lib";
import { DarkModeToggle } from "shared-lib";

// This is for testing purposes to see if the shared-lib is correctly imported
import * as SharedLib from "shared-lib";
console.log(SharedLib); // This will log all exports from shared-lib

function CustomerNav({ cart, handleLogout }) {
  const { isLoggedIn, isAdmin } = useContext(AuthContext);
  return (
    <nav className="bg-white dark:bg-gray-900 shadow-md p-4 text-gray-800 dark:text-gray-200">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-xl font-bold text-gray-800">
          PWA-Marketplace
        </Link>
        <div className="flex items-center gap-4">
          {isLoggedIn ? (
            <>
              <Link to="/cart" className="relative">
                <ShoppingCart className="h-6 w-6 text-gray-700" />
                {cart.length > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-700 text-white rounded-full text-xs w-5 h-5 flex items-center justify-center">
                    {cart.reduce((total, item) => total + item.quantity, 0)}
                  </span>
                )}
              </Link>
              {isAdmin && (
                <Link to="/admin" className="text-gray-700 hover:text-blue-500">
                  Admin
                </Link>
              )}
              <Button variant="outline" onClick={handleLogout}>
                Logout
              </Button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-gray-700 hover:text-blue-500">
                Login
              </Link>
              <Link to="/signup" className="text-gray-700 hover:text-blue-500">
                Signup
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

function AppContent() {
  const { isLoggedIn, user, isAdmin, login, logout } = useContext(AuthContext);
  const [cart, setCart] = useState([]);
  const location = useLocation();

  useEffect(() => {
    const storedCart = localStorage.getItem("cart");
    const fetchUser = async () => {
      const user = await authService.getCurrentUser();
      if (user) {
        login(user); // Use the login function from AuthContext to update the state
      }
    };
    fetchUser();
    if (storedCart) {
      setCart(JSON.parse(storedCart));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem("cart", JSON.stringify(cart));
  }, [cart]);

  const addToCart = (product) => {
    setCart((prevCart) => {
      const existingItem = prevCart.find((item) => item.id === product.id);
      if (existingItem) {
        return prevCart.map((item) =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      } else {
        return [...prevCart, { ...product, quantity: 1 }];
      }
    });
  };

  // fullRemove define a default value of false if this function is called without this parameter
  const removeFromCart = (productId, fullRemove = false) => {
    setCart((prevCart) => {
      const existingItem = prevCart.find((item) => item.id === productId);
      if (fullRemove || (existingItem && existingItem.quantity === 1)) {
        // Remove the item entirely
        return prevCart.filter((item) => item.id !== productId);
      } else {
        return prevCart.map((item) =>
          item.id === productId
            ? { ...item, quantity: item.quantity - 1 }
            : item
        );
      }
    });
  };

  const clearCart = () => {
    setCart([]);
  };

  return (
    <div className="bg-background text-text dark:bg-background-dark dark:text-text-dark min-h-screen">
      <CustomerNav cart={cart} handleLogout={logout} />
      <DarkModeToggle />

      {/* main: This is an HTML5 semantic element that represents the dominant/main content of the document's <body> */}
      <main className="container mx-auto p-4">
        <CustomerRoutes
          cart={cart}
          addToCart={addToCart}
          removeFromCart={removeFromCart}
          clearCart={clearCart}
        />
      </main>

      <footer className="bg-gray-200 dark:bg-gray-800 text-center p-4 mt-8 text-gray-600 dark:text-gray-300">
        {/* p: This is an HTML5 semantic element that represents a paragraph */}
        <p>
          {/* &copy;: This is an HTML entity that represents the copyright symbol
          {new Date().getFullYear()}: This JS expression gets the current year */}
          &copy; {new Date().getFullYear()} PWA-Marketplace. All rights reserved
        </p>
      </footer>
    </div>
  );
}

const App = () => <AppContent />;

export default App;
