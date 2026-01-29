import React, { useState, useEffect, useContext } from "react";
import { Routes, Route, useLocation, Link } from "react-router-dom";
import { AuthContext } from "shared-lib";
import CustomerRoutes from "./Routes";
import { Button } from "shared-lib";
import { ShoppingCart, Menu, X } from "lucide-react";
import { authService } from "shared-lib";
import { DarkModeToggle } from "shared-lib";

// This is for testing purposes to see if the shared-lib is correctly imported
// import * as SharedLib from "shared-lib";
// console.log(SharedLib); // This will log all exports from shared-lib

function CustomerNav({ cart, handleLogout }) {
  // Access authentication state from AuthContext
  const { isLoggedIn } = useContext(AuthContext);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const closeMenu = () => setIsMenuOpen(false);
  const handleLogoutAndCloseMenu = () => {
    handleLogout();
    closeMenu();
  };

  const navLinks = (
    <>
      {isLoggedIn ? (
        <>
          <Button variant="outline" onClick={handleLogoutAndCloseMenu}>
            Logout
          </Button>
        </>
      ) : (
        <>
          <Link
            to="/login"
            className="text-gray-700 dark:text-gray-300 hover:text-blue-500"
            onClick={closeMenu}
          >
            Login
          </Link>
          <Link
            to="/signup"
            className="text-gray-700 dark:text-gray-300 hover:text-blue-500"
            onClick={closeMenu}
          >
            Signup
          </Link>
        </>
      )}
    </>
  );

  return (
    <nav className="sticky top-0 z-30 bg-white dark:bg-gray-900 shadow-md p-4 text-gray-800 dark:text-gray-200">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-xl font-bold" onClick={closeMenu}>
          Home
        </Link>
        <div className="flex items-center gap-4">
          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-4">{navLinks}</div>
          {/* Cart Icon - always visible when logged in */}
          {isLoggedIn && (
            <Link to="/cart" className="relative" onClick={closeMenu}>
              <ShoppingCart className="h-6 w-6 text-gray-700 dark:text-gray-300" />
              {cart.length > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-700 text-white rounded-full text-xs w-5 h-5 flex items-center justify-center">
                  {/* reduce: calculate total quantity of items in cart. Equivalent to total = total + item.quantity where item.quantity iterates over each item in cart */}
                  {cart.reduce((total, item) => total + item.quantity, 0)}
                </span>
              )}
            </Link>
          )}

          <DarkModeToggle />

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              aria-label="Toggle menu"
            >
              {isMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>
      {/* Mobile Menu Panel */}
      {isMenuOpen && (
        <div className="md:hidden mt-4">
          <div className="flex flex-col items-center gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            {navLinks}
          </div>
        </div>
      )}
    </nav>
  );
}

function AppContent() {
  // Access authentication state from AuthContext
  const { isLoggedIn, user, login, logout } = useContext(AuthContext);
  const [cart, setCart] = useState([]);
  const location = useLocation();

  useEffect(() => {
    const storedCart = localStorage.getItem("cart");
    const fetchUser = async () => {
      const customer = await authService.getCurrentUser();
      if (customer) {
        login(customer); // Use the login function from AuthContext to update the state
      }
    };
    fetchUser();
    if (storedCart) {
      // Initialize cart state from localStorage converting a JSON string back to JS Object
      setCart(JSON.parse(storedCart));
    }
  }, []);

  // Sync cart state to localStorage saving cart data there whenever it adds or removes items
  useEffect(() => {
    // Store cart as a JSON string in localStorage
    localStorage.setItem("cart", JSON.stringify(cart));
  }, [cart]);



  // Use StoresProductsServices.id as the unique identifier for Cart Items
  const addToCart = ({ storeProductService }) => {
    setCart((prevCart) => {
      const existingItem = prevCart.find(
        (item) => item.storeProductService.id === storeProductService.id
      );
      // ??: If storeProductService is null or undefined then assume no stock limit through built-in global JS math value: Infinity
      const stock = storeProductService.stock ?? Infinity; // fallback if stock is undefined
      const currentQty = existingItem ? existingItem.quantity : 0;
      if (currentQty + 1 > stock) {
        // Optionally, show a message to the user (e.g., toast, alert)
        alert('Not enough stock available for this Item');
        return prevCart;
      }
      if (existingItem) {
        return prevCart.map((item) =>
          item.storeProductService.id === storeProductService.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      } else {
        return [
          ...prevCart,
          {
            storeProductService,
            quantity: 1,
            active: true,
          },
        ];
      }
    });
  };

  // Inactivate all items in the cart (set active: false)
  const inactivateCartItems = () => {
    setCart((prevCart) => prevCart.map(item => ({ ...item, active: false })));
  };

  const removeFromCart = ({ storeProductService, fullRemove = false }) => {
    setCart((prevCart) => {
      const existingItem = prevCart.find(
        (item) => item.storeProductService.id === storeProductService.id
      );
      if (existingItem && existingItem.active) {
        if (fullRemove || existingItem.quantity === 1) {
          // Inactivate the item instead of removing it to keep cart history
          return prevCart.map((item) =>
            item.storeProductService.id === storeProductService.id
              ? { ...item, active: false }
              : item
          );
        } else {
          return prevCart.map((item) =>
            item.storeProductService.id === storeProductService.id
              ? { ...item, quantity: item.quantity - 1 }
              : item
          );
        }
      }
      // If item doesn't exist or is not active, return previous cart unmodified
      return prevCart;
    });
  };

  const clearCart = () => {
    setCart([]);
  };

  // Only show active items in the cart to the customer
  const activeCart = cart.filter(item => item.active !== false);

  return (
    <div className="bg-background text-text dark:bg-background-dark dark:text-text-dark min-h-screen">
      {/* The sticky search bar is rendered inside HomePage, which is rendered below CustomerNav */}
      <CustomerNav cart={activeCart} handleLogout={logout} />

      {/* main: This is an HTML5 semantic element that represents the dominant/main content of the document's <body> */}
      <main className="container mx-auto p-4">
        {/* A component can be invoked with any amount of props and then it receives just the ones it defines */}
        <CustomerRoutes
          cart={cart}
          addToCart={addToCart}
          removeFromCart={removeFromCart}
          clearCart={clearCart}
          inactivateCartItems={inactivateCartItems}
        />
      </main>

      <footer className="bg-white dark:bg-gray-900 text-center p-4 mt-8 text-gray-600 dark:text-gray-300">
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
