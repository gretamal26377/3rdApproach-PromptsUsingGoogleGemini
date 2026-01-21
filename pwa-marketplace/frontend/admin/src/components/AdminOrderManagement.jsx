import React, { useState, useEffect } from "react";
import { Button } from "shared-lib"; //Issue: ui folder not found
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "shared-lib";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "shared-lib";
import {
  Form,
  // A Component that helps manage layout, accessibility, and sometimes validation styling for the control it wraps
  FormControl,
  FormField, // A Component that defines a Field in the Form
  // A layout Component that groups together the Label, Control, and any messages (like errors) for a single Form Field
  FormItem,
  FormLabel, // A component that displays the Label for a Form Field
  FormMessage, // FormMessage: a component that displays validation messages
} from "shared-lib";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
//zod: a TypeScript-first schema declaration and validation library. Purpose: to validate the form data before submission
import * as z from "zod";
import { Plus, Edit, Trash2, ShoppingCart, AlertCircle } from "lucide-react";
import { cn } from "shared-lib";
import { format } from "date-fns";

// Define the schema for order form validation
const orderSchema = z.object({
  userId: z.coerce
    .number()
    .min(1, { message: "User ID must be a positive number" }),
  totalAmount: z.coerce
    .number()
    .min(0, { message: "Total amount must be zero or greater" }),
  //Issue: Not all fields are being used in the form, but they are defined in the schema
  // items: z.array(z.object({ // Removed nested form, simplified for demo
  //   productId: z.coerce.number().min(1),
  //   quantity: z.coerce.number().min(1),
  // })).min(1, { message: 'Order must contain at least one item' }),
});

// Mock API functions (replace with actual API calls)
const fetchOrders = async () => {
  // Simulate fetching orders from a database
  return [
    {
      id: 1,
      userId: 1,
      orderDate: new Date(),
      totalAmount: 10.99,
      items: [{ productId: 1, quantity: 1 }],
    },
    {
      id: 2,
      userId: 2,
      orderDate: new Date(),
      totalAmount: 19.99,
      items: [{ productId: 2, quantity: 2 }],
    },
  ];
};

const createOrder = async (orderData) => {
  // Simulate creating an order in the database
  console.log("Creating order:", orderData);
  await new Promise((resolve) => setTimeout(resolve, 500)); // Simulate network delay
  const newOrder = {
    id: Math.random().toString(36).substr(2, 9),
    orderDate: new Date(), // Add orderDate here
    ...orderData,
    items: [{ productId: 1, quantity: 1 }], // Mock Items
  };
  return newOrder; // Return mock order with ID and orderDate
};

const updateOrder = async (id, orderData) => {
  // Simulate updating an order in the database
  console.log("Updating order", id, "with:", orderData);
  await new Promise((resolve) => setTimeout(resolve, 500));
  return { id, orderDate: new Date(), ...orderData }; // Return updated order with orderDate
};

const deleteOrder = async (id) => {
  // Simulate deleting an order from the database
  console.log("Deleting order:", id);
  await new Promise((resolve) => setTimeout(resolve, 500));
  return true; // Indicate success
};

const AdminOrderManagement = () => {
  const [orders, setOrders] = useState([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false); // Tracks whether the create/edit order dialog is open
  const [editOrderId, setEditOrderId] = useState(null); // Stores the ID of the order being edited, or null for a new order
  const [isLoading, setIsLoading] = useState(false); // Indicates whether a network request (create, update, delete) is in progress
  const [deleteOrderId, setDeleteOrderId] = useState(null); // Stores the ID of the order to be deleted
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false); // Tracks whether the delete confirmation dialog is open
  const [error, setError] = useState(null); // Stores any error message to display to the user

  // Initialize the form using react-hook-form and zod for validation
  // The form is used for creating and editing orders
  const form = useForm({
    resolver: zodResolver(orderSchema),
    defaultValues: {
      userId: 1,
      totalAmount: 0,
      //items: [{ productId: 1, quantity: 1 }],
    },
  });

  // This useEffect hook fetches the initial list of orders when the component mounts
  useEffect(() => {
    const loadOrders = async () => {
      setIsLoading(true);
      try {
        const ordersData = await fetchOrders();
        setOrders(
          ordersData.map((order) => ({
            ...order,
            id: Math.random().toString(36).substr(2, 9),
          }))
        ); //mock id
        //"order =>" is the same as "(order) =>". Parentheses are optional when there is only one parameter
      } catch (err) {
        setError(err.message || "Failed to load orders");
      } finally {
        setIsLoading(false);
      }
    };
    loadOrders();
  }, []);

  const handleCreateOrUpdateOrder = async (data) => {
    setIsLoading(true);
    try {
      if (editOrderId) {
        // Update existing order
        const updatedOrder = await updateOrder(editOrderId, data);
        setOrders(
          orders.map((order) =>
            order.id === editOrderId ? updatedOrder : order
          )
        );
      } else {
        // Create new order
        const newOrder = await createOrder(data);
        setOrders([...orders, newOrder]);
      }
      setIsDialogOpen(false);
      form.reset();
      setEditOrderId(null);
    } catch (err) {
      setError(err.message || "Failed to create/update order");
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditOrder = (order) => {
    setEditOrderId(order.id);
    form.reset({
      userId: order.userId,
      totalAmount: order.totalAmount,
      //items: order.items,
    });
    setIsDialogOpen(true);
  };

  // Open the dialog for creating a new order
  const openCreateDialog = () => {
    setEditOrderId(null);
    form.reset({ userId: 1, totalAmount: 0 }); // Reset form with default values
    setIsDialogOpen(true);
  };

  const handleDeleteOrder = async () => {
    if (!deleteOrderId) return;
    setIsLoading(true);
    try {
      await deleteOrder(deleteOrderId);
      setOrders(orders.filter((o) => o.id !== deleteOrderId));
      setIsDeleteDialogOpen(false);
      setDeleteOrderId(null);
    } catch (err) {
      setError(err.message || "Failed to delete the order.");
    } finally {
      setIsLoading(false);
    }
  };

  const confirmDeleteOrder = (id) => {
    setDeleteOrderId(id);
    setIsDeleteDialogOpen(true);
  };

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-6 flex items-center gap-2">
        <ShoppingCart className="h-8 w-8 text-blue-500" />
        Order Management
      </h1>

      <div className="flex justify-end mb-4">
        <Button
          onClick={openCreateDialog}
          className="bg-blue-500 hover:bg-blue-600 text-white"
        >
          <Plus className="mr-2 h-4 w-4" /> Add Order
        </Button>
      </div>

      {error && (
        <Dialog>
          <DialogContent>
            <AlertCircle className="h-4 w-4 text-red-700" />
            <DialogTitle>Error</DialogTitle>
            <DialogDescription>{error}</DialogDescription>
          </DialogContent>
        </Dialog>
      )}

      {isLoading ? (
        <p>Loading orders...</p> // Replace with a more sophisticated loader if desired
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Order ID</TableHead>
              <TableHead>User ID</TableHead>
              <TableHead>Order Date</TableHead>
              <TableHead>Total Amount</TableHead>
              <TableHead>Items</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {orders.map((order) => (
              <TableRow key={order.id} className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800">
                <TableCell>{order.id}</TableCell>
                <TableCell>{order.userId}</TableCell>
                <TableCell>{format(order.orderDate, "PPPpp")}</TableCell>
                <TableCell>${order.totalAmount.toFixed(2)}</TableCell>
                <TableCell>
                  {/** Issue: It should display product names instead of IDs */}
                  {order.items
                    .map((item) => `${item.productId} x ${item.quantity}`)
                    .join(", ")}
                </TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleEditOrder(order)}
                      className="hover:bg-gray-100"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="destructive"
                      size="icon"
                      onClick={() => confirmDeleteOrder(order.id)}
                      className="hover:bg-red-800"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>
              {editOrderId ? "Edit Order" : "Add Order"}
            </DialogTitle>
            <DialogDescription>
              {editOrderId
                ? "Make changes to the order below. Click save when you're done."
                : "Enter order details below."}
            </DialogDescription>
          </DialogHeader>
          <Form {...form}>
            <form
              onSubmit={form.handleSubmit(handleCreateOrUpdateOrder)}
              className="space-y-6"
            >
              <FormField
                // form.control: A reference to the form control object created by react-hook-form
                control={form.control}
                name="userId"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>User ID</FormLabel>
                    <FormControl>
                      <Input type="number" placeholder="1" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="totalAmount"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Total Amount</FormLabel>
                    <FormControl>
                      <Input type="number" placeholder="0.00" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="items"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Items</FormLabel>
                    <FormControl>
                      {/** "?." is optional chaining, it checks if field.value is defined before trying to map over it */}
                      "
                      {field.value?.map((item, index) => (
                        <div key={index} className="flex gap-2 mb-2">
                          <Input
                            type="number"
                            placeholder="Product ID"
                            value={item.productId}
                            onChange={(e) => {
                              const newItems = [...field.value];
                              {
                                /** Copy the existing items and update the productId with the new value input by the user */
                              }
                              newItems[index] = {
                                ...item,
                                productId: parseInt(e.target.value, 10),
                              };
                              {
                                /** Issue: Hand updated item ID back to the form. Check what happen if updated ID isn't in the DB when form is submitted */
                              }
                              field.onChange(newItems);
                            }}
                            className="w-1/2"
                          />
                          <Input
                            type="number"
                            placeholder="Quantity"
                            value={item.quantity}
                            onChange={(e) => {
                              const newItems = [...field.value];
                              {
                                /** Issue: Validate this quantity regard to the product stock and
                                 * adding Product Amount to the Form
                                 */
                              }
                              newItems[index] = {
                                ...item,
                                quantity: parseInt(e.target.value, 10),
                              };
                              field.onChange(newItems);
                            }}
                            className="w-1/2"
                          />
                        </div>
                      ))}
                      {/** Add a new item to the order/form causing the UI to render an additional item input */}
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          // Add/pushes a new item to the order/form and also causes the UI to render this added item
                          field.onChange([
                            // Handle when current value is undefined by defaulting to an empty array if it is undefined
                            ...(field.value || []),
                            // Issue: Fix the default value of productId to be a valid product ID
                            { productId: 0, quantity: 1 },
                          ])
                        }
                      >
                        Add Item
                      </Button>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setIsDialogOpen(false);
                    form.reset();
                    setEditOrderId(null);
                  }}
                  disabled={isLoading}
                  className="mr-2"
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Saving..." : "Save Order"}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Are you sure?</DialogTitle>
            <DialogDescription>
              This action cannot be undone. This will permanently delete this
              order
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsDeleteDialogOpen(false);
                setDeleteOrderId(null);
              }}
              disabled={isLoading}
              className="mr-2"
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteOrder}
              disabled={isLoading}
            >
              {isLoading ? "Deleting..." : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AdminOrderManagement;
