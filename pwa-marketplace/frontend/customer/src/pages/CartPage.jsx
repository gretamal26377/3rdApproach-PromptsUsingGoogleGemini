import React from "react";
import Cart from "../components/Cart";

const CartPage = ({ cart, addToCart, removeFromCart, clearCart }) => {
  return (
    <div>
      <Cart
        cart={cart}
        addToCart={addToCart}
        removeFromCart={removeFromCart}
        clearCart={clearCart}
      />
    </div>
  );
};

export default CartPage;
