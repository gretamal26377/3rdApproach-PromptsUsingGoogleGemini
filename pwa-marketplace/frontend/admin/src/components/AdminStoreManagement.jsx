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
import { Plus, Edit, Trash2, Store, AlertCircle } from "lucide-react";
import { cn } from "shared-lib";

// Define the schema for store form validation
const storeSchema = z.object({
  name: z.string().min(2, { message: "Name must be at least 2 characters" }),
  description: z
    .string()
    .min(10, { message: "Description must be at least 10 characters" }),
  ownerId: z.coerce
    .number()
    .min(1, { message: "Owner ID must be a positive number" }),
});

// Mock API functions (replace with actual API calls)
const fetchStores = async () => {
  // Simulate fetching stores from a database
  return [
    { id: 1, name: "Store 1", description: "Description 1", ownerId: 1 },
    { id: 2, name: "Store 2", description: "Description 2", ownerId: 2 },
  ];
};

const createStore = async (storeData) => {
  // Simulate creating a store in the database
  console.log("Creating store:", storeData);
  await new Promise((resolve) => setTimeout(resolve, 500)); // Simulate network delay
  return { id: Math.random().toString(36).substr(2, 9), ...storeData }; // Return mock store with ID
};

const updateStore = async (id, storeData) => {
  // Simulate updating a store in the database
  console.log("Updating store", id, "with:", storeData);
  await new Promise((resolve) => setTimeout(resolve, 500));
  return { id, ...storeData }; // Return updated store
};

const deleteStore = async (id) => {
  // Simulate deleting a store from the database
  console.log("Deleting store:", id);
  await new Promise((resolve) => setTimeout(resolve, 500));
  return true; // Indicate success
};

const AdminStoreManagement = () => {
  const [stores, setStores] = useState([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editStoreId, setEditStoreId] = (useState < string) | (null > null);
  const [isLoading, setIsLoading] = useState(false);
  const [deleteStoreId, setDeleteStoreId] = (useState < string) | (null > null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [error, setError] = (useState < string) | (null > null);

  const form = useForm({
    resolver: zodResolver(storeSchema),
    defaultValues: {
      name: "",
      description: "",
      ownerId: 1,
    },
  });

  useEffect(() => {
    const loadStores = async () => {
      setIsLoading(true);
      try {
        const storesData = await fetchStores();
        setStores(
          storesData.map((s) => ({
            ...s,
            id: Math.random().toString(36).substr(2, 9),
          }))
        ); //mock id
      } catch (err) {
        setError(err.message || "Failed to load stores");
      } finally {
        setIsLoading(false);
      }
    };
    loadStores();
  }, []);

  const handleCreateOrUpdateStore = async (data) => {
    setIsLoading(true);
    try {
      if (editStoreId) {
        // Update existing store
        const updatedStore = await updateStore(editStoreId, data);
        setStores(stores.map((s) => (s.id === editStoreId ? updatedStore : s)));
      } else {
        // Create new store
        const newStore = await createStore(data);
        setStores([...stores, { ...newStore, id: newStore.id }]);
      }
      setIsDialogOpen(false);
      form.reset();
      setEditStoreId(null);
    } catch (err) {
      setError(err.message || "Failed to create/update store");
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditStore = (store) => {
    setEditStoreId(store.id);
    form.reset(store);
    setIsDialogOpen(true);
  };

  const openCreateDialog = () => {
    setEditStoreId(null);
    form.reset({ name: "", description: "", ownerId: 1 }); // Reset form with default values
    setIsDialogOpen(true);
  };

  const handleDeleteStore = async () => {
    if (!deleteStoreId) return;
    setIsLoading(true);
    try {
      await deleteStore(deleteStoreId);
      setStores(stores.filter((s) => s.id !== deleteStoreId));
      setIsDeleteDialogOpen(false);
      setDeleteStoreId(null);
    } catch (err) {
      setError(err.message || "Failed to delete the store");
    } finally {
      setIsLoading(false);
    }
  };

  const confirmDeleteStore = (id) => {
    setDeleteStoreId(id);
    setIsDeleteDialogOpen(true);
  };

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-6 flex items-center gap-2">
        <Store className="h-8 w-8 text-blue-500" />
        Store Management
      </h1>

      <div className="flex justify-end mb-4">
        <Button
          onClick={openCreateDialog}
          className="bg-blue-500 hover:bg-blue-600 text-white"
        >
          <Plus className="mr-2 h-4 w-4" /> Add Store
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
        <p>Loading stores...</p> // Replace with a more sophisticated loader if desired
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Owner ID</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {stores.map((store) => (
              <TableRow key={store.id} className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800">
                <TableCell>{store.name}</TableCell>
                <TableCell>{store.description}</TableCell>
                <TableCell>{store.ownerId}</TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleEditStore(store)}
                      className="hover:bg-gray-100"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="destructive"
                      size="icon"
                      onClick={() => confirmDeleteStore(store.id)}
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
              {editStoreId ? "Edit Store" : "Add Store"}
            </DialogTitle>
            <DialogDescription>
              {editStoreId
                ? "Make changes to the store below. Click save when you're done"
                : "Enter store details below"}
            </DialogDescription>
          </DialogHeader>
          <Form {...form}>
            <form
              onSubmit={form.handleSubmit(handleCreateOrUpdateStore)}
              className="space-y-6"
            >
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Store Name" {...field} />
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
                      <Input placeholder="Store Description" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="ownerId"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Owner ID</FormLabel>
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
                    setEditStoreId(null);
                  }}
                  disabled={isLoading}
                  className="mr-2"
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Saving..." : "Save Store"}
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
              store
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsDeleteDialogOpen(false);
                setDeleteStoreId(null);
              }}
              disabled={isLoading}
              className="mr-2"
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteStore}
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

export default AdminStoreManagement;
