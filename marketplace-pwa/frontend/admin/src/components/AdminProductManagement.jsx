import React, { useState, useEffect } from "react";
import { Button } from "shared-lib";
import { Input } from "shared-lib";
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
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "shared-lib";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Plus, Edit, Trash2, AlertCircle, ShoppingBag } from "lucide-react";
import { cn } from "shared-lib";

// Define the schema for product form validation
const productSchema = z.object({
  name: z.string().min(2, { message: "Name must be at least 2 characters." }),
  description: z
    .string()
    .min(10, { message: "Description must be at least 10 characters." }),
  price: z.coerce
    .number()
    .min(0.01, { message: "Price must be greater than 0." }),
  storeId: z.coerce
    .number()
    .min(1, { message: "Store ID must be a positive number." }),
});

// Mock API functions (replace with actual API calls)
const fetchProducts = async () => {
  // Simulate fetching products from a database
  return [
    {
      id: 1,
      name: "Product 1",
      description: "Description 1",
      price: 10.99,
      storeId: 1,
    },
    {
      id: 2,
      name: "Product 2",
      description: "Description 2",
      price: 19.99,
      storeId: 2,
    },
  ];
};

const createProduct = async (productData) => {
  // Simulate creating a product in the database
  console.log("Creating product:", productData);
  await new Promise((resolve) => setTimeout(resolve, 500)); // Simulate network delay
  return { id: Math.random().toString(36).substr(2, 9), ...productData }; // Return mock product with ID
};

const updateProduct = async (id, productData) => {
  // Simulate updating a product in the database
  console.log("Updating product", id, "with:", productData);
  await new Promise((resolve) => setTimeout(resolve, 500));
  return { id, ...productData }; // Return updated product
};

const deleteProduct = async (id) => {
  // Simulate deleting a product from the database
  console.log("Deleting product:", id);
  await new Promise((resolve) => setTimeout(resolve, 500));
  return true; // Indicate success
};

const AdminProductManagement = () => {
  const [products, setProducts] = useState([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editProductId, setEditProductId] = (useState < string) | (null > null);
  const [isLoading, setIsLoading] = useState(false);
  const [deleteProductId, setDeleteProductId] =
    (useState < string) | (null > null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [error, setError] = (useState < string) | (null > null);

  const form = useForm({
    resolver: zodResolver(productSchema),
    defaultValues: {
      name: "",
      description: "",
      price: 0,
      storeId: 1,
    },
  });

  useEffect(() => {
    const loadProducts = async () => {
      setIsLoading(true);
      try {
        const productsData = await fetchProducts();
        setProducts(
          productsData.map((p) => ({
            ...p,
            id: Math.random().toString(36).substr(2, 9),
          }))
        ); //mock id
      } catch (err) {
        setError(err.message || "Failed to load products");
      } finally {
        setIsLoading(false);
      }
    };
    loadProducts();
  }, []); // [] to run once on mount

  const handleCreateOrUpdateProduct = async (data) => {
    setIsLoading(true);
    try {
      if (editProductId) {
        // Update existing product
        const updatedProduct = await updateProduct(editProductId, data);
        setProducts(
          products.map((p) => (p.id === editProductId ? updatedProduct : p))
        );
      } else {
        // Create new product
        const newProduct = await createProduct(data);
        setProducts([...products, { ...newProduct, id: newProduct.id }]);
      }
      setIsDialogOpen(false);
      form.reset();
      setEditProductId(null);
    } catch (err) {
      setError(err.message || "Failed to create/update product");
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditProduct = (product) => {
    setEditProductId(product.id);
    form.reset(product);
    setIsDialogOpen(true);
  };

  const openCreateDialog = () => {
    setEditProductId(null);
    form.reset({ name: "", description: "", price: 0, storeId: 1 }); // Reset form with default values
    setIsDialogOpen(true);
  };

  const handleDeleteProduct = async () => {
    if (!deleteProductId) return;
    setIsLoading(true);
    try {
      await deleteProduct(deleteProductId);
      setProducts(products.filter((p) => p.id !== deleteProductId));
      setIsDeleteDialogOpen(false);
      setDeleteProductId(null);
    } catch (err) {
      setError(err.message || "Failed to delete the product");
    } finally {
      setIsLoading(false);
    }
  };

  const confirmDeleteProduct = (id) => {
    setDeleteProductId(id);
    setIsDeleteDialogOpen(true);
  };

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-6 flex items-center gap-2">
        <ShoppingBag className="h-8 w-8 text-blue-500" />
        Product Management
      </h1>

      <div className="flex justify-end mb-4">
        <Button
          onClick={openCreateDialog}
          className="bg-blue-500 hover:bg-blue-600 text-white"
        >
          <Plus className="mr-2 h-4 w-4" /> Add Product
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
        <p>Loading products...</p> // Replace with a more sophisticated loader if desired
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Price</TableHead>
              <TableHead>Store ID</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {products.map((product) => (
              <TableRow key={product.id} className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800">
                <TableCell>{product.name}</TableCell>
                <TableCell>{product.description}</TableCell>
                <TableCell>${product.price.toFixed(2)}</TableCell>
                <TableCell>{product.storeId}</TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleEditProduct(product)}
                      className="hover:bg-gray-100"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="destructive"
                      size="icon"
                      onClick={() => confirmDeleteProduct(product.id)}
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
      {/** onOpenChange is used to control the dialog open state, any change in the dialog window will update isDialogOpen state through setIsDialogOpen */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>
              {editProductId ? "Edit Product" : "Add Product"}
            </DialogTitle>
            <DialogDescription>
              {editProductId
                ? "Make changes to the product below. Click save when you're done"
                : "Enter product details below"}
            </DialogDescription>
          </DialogHeader>
          <Form {...form}>
            <form
              // handleCreateOrUpdateProduct is called when form is submitted with the form data as a prop, despite form data is not explicitly passed in between parentheses
              onSubmit={form.handleSubmit(handleCreateOrUpdateProduct)}
              className="space-y-6"
            >
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Product Name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description</FormLabel>
                    <FormControl>
                      <Input placeholder="Product Description" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="price"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Price</FormLabel>
                    <FormControl>
                      <Input type="number" placeholder="0.00" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                // Issue: We need to change it using a search bar to select the store by name
                name="storeId"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Store ID</FormLabel>
                    <FormControl>
                      <Input type="number" placeholder="1" {...field} />
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
                    setEditProductId(null);
                  }}
                  disabled={isLoading}
                  className="mr-2"
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Saving..." : "Save Product"}
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
              product
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsDeleteDialogOpen(false);
                setDeleteProductId(null);
              }}
              disabled={isLoading}
              className="mr-2"
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteProduct}
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

export default AdminProductManagement;
