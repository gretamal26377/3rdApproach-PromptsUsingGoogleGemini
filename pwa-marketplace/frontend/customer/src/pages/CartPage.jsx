import React from "react";
import Cart from "../components/Cart";

const CartPage = ({ cart, addToCart, removeFromCart, clearCart, inactivateCartItems }) => {
  return (
    <div>
      <Cart
        cart={cart}
        addToCart={addToCart}
        removeFromCart={removeFromCart}
        clearCart={clearCart}
        inactivateCartItems={inactivateCartItems}
      />
    </div>
  );
};

export default CartPage;
