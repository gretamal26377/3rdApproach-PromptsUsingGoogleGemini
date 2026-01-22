// Customer-specific routes
import React from "react";
import { Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage";
import { LoginPage } from "shared-lib";
import SignupPage from "./pages/SignupPage";
import StoresPage from "./pages/StoresPage";
import StorePage from "./pages/StorePage";
import ProductServicePage from "./pages/ProductServicePage";
import { ProductServiceListingsPage } from "shared-lib";
import CartPage from "./pages/CartPage";

export default function CustomerRoutes({ cart, addToCart, removeFromCart, clearCart, inactivateCartItems }) {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/stores" element={<StoresPage />} />
      {/* This route allows users navigate to a specific store by providing storeId parameter in the URL.
        The StorePage component can then use storeId to fetch that store's data. addToCart prop allows
        StorePage component adding products from the store to the customer's cart */}
      <Route
        path="/stores/:storeId"
        element={<StorePage addToCart={addToCart}  />}
      />
      {/* Issue?: Im not sure whether this route will be used here at Customer or Admin Frontend */}
      <Route
        path="/products-services/:productId"
        element={<ProductServicePage addToCart={addToCart} />}
      />
      <Route
        path="/products-services/:baseProductServiceId/listings"
        element={<ProductServiceListingsPage addToCart={addToCart} />}
      />
      <Route
        path="/cart"
        element={
          <CartPage
            cart={cart}
            addToCart={addToCart}
            removeFromCart={removeFromCart}
            clearCart={clearCart}
            inactivateCartItems={inactivateCartItems}
          />
        }
      />
    </Routes>
  );
}

    />
  }
/>
    </Routes>
  );
}
