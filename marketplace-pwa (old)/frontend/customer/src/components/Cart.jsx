import React from "react";
import { Button } from "shared-lib";
import { ShoppingCart, XCircle, PlusCircle, MinusCircle } from "lucide-react";
import { cn } from "shared-lib";
import Checkout from "./Checkout";
import { useState } from "react";

const Cart = ({ cart, addToCart, removeFromCart, clearCart }) => {
  const [isCheckout, setIsCheckout] = useState(false);

  if (cart.length === 0) {
    return (
      <div className="text-center py-8">
        <ShoppingCart className="h-12 w-12 mx-auto mb-4 text-gray-500" />
        <p className="text-gray-600">Your cart is empty</p>
      </div>
    );
  }

  const total = cart.reduce((acc, item) => acc + item.price * item.quantity, 0);

  const handleCheckout = (formData) => {
    // In a real application, you would send this data to your backend
    console.log("Checkout data:", formData);
    console.log(`Order placed for $${total.toFixed(2)}!`);
    clearCart();
    setIsCheckout(false); // Hide checkout form
    alert(`Order placed successfully!  Total was $${total.toFixed(2)}`);
  };

  return (
    <div className="container mx-auto p-4 space-y-4">
      <h2 className="text-2xl font-semibold">Your Cart</h2>
      <div className="space-y-2">
        {cart.map((item) => (
          <div
            key={item.id}
            className="flex items-center justify-between border-b pb-2 last:border-b-0"
          >
            <div>
              <h3 className="font-medium">{item.name}</h3>
              <p className="text-sm text-gray-500">Price: ${item.price}</p>
              <div className="flex items-center gap-2 mt-1">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={removeFromCart(item.id)} // decrease quantity by 1
                  className="hover:bg-gray-100"
                >
                  <MinusCircle className="h-4 w-4" />
                </Button>
                <span className="text-gray-700">Quantity: {item.quantity}</span>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => addToCart(item)}
                  className="hover:bg-gray-100"
                >
                  <PlusCircle className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div className="text-right">
              <p className="text-lg font-semibold">
                ${(item.price * item.quantity).toFixed(2)}
              </p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={(removeFromCart(item.id), true)} // remove item completely
              className="text-gray-500 hover:text-red-700"
            >
              <XCircle className="h-5 w-5" />
            </Button>
          </div>
        ))}
      </div>
      <div className="flex justify-between items-center mt-4">
        <h2 className="text-xl font-bold">Total: ${total.toFixed(2)}</h2>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={clearCart}
            className="bg-yellow-500 text-white hover:bg-yellow-600 transition-colors"
          >
            Clear Cart
          </Button>
          <Button
            className="bg-green-500 text-white hover:bg-green-600 transition-colors"
            onClick={() => setIsCheckout(true)}
          >
            Checkout
          </Button>
        </div>
      </div>

      {isCheckout && <Checkout total={total} onCheckout={handleCheckout} />}
    </div>
  );
};

export default Cart;
