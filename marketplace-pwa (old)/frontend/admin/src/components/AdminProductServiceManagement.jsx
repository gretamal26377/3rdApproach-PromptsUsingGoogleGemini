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

// Define the schema for productService form validation
const productServiceSchema = z.object({
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
const fetchProductsServices = async () => {
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

const createProductService = async (productServiceData) => {
  // Simulate creating a product in the database
  console.log("Creating Product/Service:", productServiceData);
  await new Promise((resolve) => setTimeout(resolve, 500)); // Simulate network delay
  return { id: Math.random().toString(36).substr(2, 9), ...productServiceData }; // Return mock product with ID
};

const updateProductService = async (id, productServiceData) => {
  // Simulate updating a product in the database
  console.log("Updating Product/Service", id, "with:", productServiceData);
  await new Promise((resolve) => setTimeout(resolve, 500));
  return { id, ...productServiceData }; // Return updated product/service
};

const deleteProductService = async (id) => {
  // Simulate deleting a product from the database
  console.log("Deleting Product/Service:", id);
  await new Promise((resolve) => setTimeout(resolve, 500));
  return true; // Indicate success
};

const AdminProductServiceManagement = () => {
  const [productsServices, setProductsServices] = useState([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editProductServiceId, setEditProductServiceId] =
    (useState < string) | (null > null);
  const [isLoading, setIsLoading] = useState(false);
  const [deleteProductServiceId, setDeleteProductServiceId] =
    (useState < string) | (null > null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [error, setError] = (useState < string) | (null > null);

  const form = useForm({
    resolver: zodResolver(productServiceSchema),
    defaultValues: {
      name: "",
      description: "",
      price: 0,
      storeId: 1,
    },
  });

  useEffect(() => {
    const loadProductsServices = async () => {
      setIsLoading(true);
      try {
        const productsServicesData = await fetchProductsServices();
        setProductsServices(
          productsServicesData.map((ps) => ({
            ...ps,
            id: Math.random().toString(36).substr(2, 9),
          }))
        ); //mock id
      } catch (err) {
        setError(err.message || "Failed to load Products/Services");
      } finally {
        setIsLoading(false);
      }
    };
    loadProductsServices();
  }, []); // [] to run once on mount

  const handleCreateOrUpdateProductService = async (data) => {
    setIsLoading(true);
    try {
      if (editProductServiceId) {
        // Update existing product/service
        const updatedProductService = await updateProductService(
          editProductServiceId,
          data
        );
        setProductsServices(
          productsServices.map((ps) =>
            ps.id === editProductServiceId ? updatedProductService : ps
          )
        );
      } else {
        // Create new product/service
        const newProductService = await createProductService(data);
        setProductsServices([
          ...productsServices,
          { ...newProductService, id: newProductService.id },
        ]);
      }
      setIsDialogOpen(false);
      form.reset();
      setEditProductServiceId(null);
    } catch (err) {
      setError(err.message || "Failed to Create/Update Product/Service");
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditProductService = (productService) => {
    setEditProductServiceId(productService.id);
    form.reset(productService); // Populate form with existing Product/Service data
    setIsDialogOpen(true);
  };

  const openCreateDialog = () => {
    setEditProductServiceId(null);
    form.reset({ name: "", description: "", price: 0, storeId: 1 }); // Reset form with default values
    setIsDialogOpen(true);
  };

  const handleDeleteProductService = async () => {
    if (!deleteProductServiceId) return;
    setIsLoading(true);
    try {
      await deleteProductService(deleteProductServiceId);
      setProductsServices(
        productsServices.filter((p) => p.id !== deleteProductServiceId)
      );
      setIsDeleteDialogOpen(false);
      setDeleteProductServiceId(null);
    } catch (err) {
      setError(err.message || "Failed to delete the Product/Service");
    } finally {
      setIsLoading(false);
    }
  };

  const confirmDeleteProductService = (id) => {
    setDeleteProductServiceId(id);
    setIsDeleteDialogOpen(true);
  };

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-6 flex items-center gap-2">
        <ShoppingBag className="h-8 w-8 text-blue-500" />
        Product/Service Management
      </h1>

      <div className="flex justify-end mb-4">
        <Button
          onClick={openCreateDialog}
          className="bg-blue-500 hover:bg-blue-600 text-white"
        >
          <Plus className="mr-2 h-4 w-4" /> Add Product/Service
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
        <p>Loading Products/Services...</p> // Replace with a more sophisticated loader if desired
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
            {productsServices.map((productService) => (
              <TableRow
                key={productService.id}
                className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                <TableCell>{productService.name}</TableCell>
                <TableCell>{productService.description}</TableCell>
                <TableCell>${productService.price.toFixed(2)}</TableCell>
                <TableCell>{productService.storeId}</TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleEditProductService(productService)}
                      className="hover:bg-gray-100"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="destructive"
                      size="icon"
                      onClick={() =>
                        confirmDeleteProductService(productService.id)
                      }
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
              {editProductServiceId
                ? "Edit Product/Service"
                : "Add Product/Service"}
            </DialogTitle>
            <DialogDescription>
              {editProductServiceId
                ? "Make changes to the Product/Service below. Click save when you finish"
                : "Enter Product/Service details below"}
            </DialogDescription>
          </DialogHeader>
          <Form {...form}>
            <form
              // handleCreateOrUpdateProductService is called when form is submitted with the form data as a prop, despite form data is not explicitly passed in between parentheses
              onSubmit={form.handleSubmit(handleCreateOrUpdateProductService)}
              className="space-y-6"
            >
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Product/Service Name" {...field} />
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
                      <Input
                        placeholder="Product/Service Description"
                        {...field}
                      />
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
                    setEditProductServiceId(null);
                  }}
                  disabled={isLoading}
                  className="mr-2"
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Saving..." : "Save Product/Service"}
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
              Product/Service
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsDeleteDialogOpen(false);
                setDeleteProductServiceId(null);
              }}
              disabled={isLoading}
              className="mr-2"
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteProductService}
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

export default AdminProductServiceManagement;
