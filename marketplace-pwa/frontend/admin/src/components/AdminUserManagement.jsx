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
import { Plus, Edit, Trash2, User, AlertCircle } from "lucide-react";
import { cn } from "shared-lib";
import { Checkbox } from "shared-lib";

// Define the schema for user form validation
const userSchema = z.object({
  username: z
    .string()
    .min(2, { message: "Username must be at least 2 characters." }),
  email: z.string().email({ message: "Invalid email address." }),
  isAdmin: z.boolean(),
});

// Mock API functions (replace with actual API calls)
const fetchUsers = async () => {
  // Simulate fetching users from a database
  return [
    { id: "1", username: "user1", email: "user1@example.com", isAdmin: false },
    { id: "2", username: "admin1", email: "admin1@example.com", isAdmin: true },
  ];
};

const createUser = async (userData) => {
  // Simulate creating a user in the database
  console.log("Creating user:", userData);
  await new Promise((resolve) => setTimeout(resolve, 500)); // Simulate network delay
  return { id: Math.random().toString(36).substr(2, 9), ...userData }; // Return mock user with ID
};

const updateUser = async (id, userData) => {
  // Simulate updating a user in the database
  console.log("Updating user", id, "with:", userData);
  await new Promise((resolve) => setTimeout(resolve, 500));
  return { id, ...userData }; // Return updated user
};

const deleteUser = async (id) => {
  // Simulate deleting a user from the database
  console.log("Deleting user:", id);
  await new Promise((resolve) => setTimeout(resolve, 500));
  return true; // Indicate success
};

const AdminUserManagement = () => {
  const [users, setUsers] = useState([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editUserId, setEditUserId] = (useState < string) | (null > null);
  const [isLoading, setIsLoading] = useState(false);
  const [deleteUserId, setDeleteUserId] = (useState < string) | (null > null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [error, setError] = (useState < string) | (null > null);

  const form = useForm({
    resolver: zodResolver(userSchema),
    defaultValues: {
      username: "",
      email: "",
      isAdmin: false,
    },
  });

  useEffect(() => {
    const loadUsers = async () => {
      setIsLoading(true);
      try {
        const usersData = await fetchUsers();
        setUsers(usersData);
      } catch (err) {
        setError(err.message || "Failed to load users");
      } finally {
        setIsLoading(false);
      }
    };
    loadUsers();
  }, []);

  const handleCreateOrUpdateUser = async (data) => {
    setIsLoading(true);
    try {
      if (editUserId) {
        // Update existing user
        const updatedUser = await updateUser(editUserId, data);
        setUsers(
          users.map((user) => (user.id === editUserId ? updatedUser : user))
        );
      } else {
        // Create new user
        const newUser = await createUser(data);
        setUsers([...users, newUser]);
      }
      setIsDialogOpen(false);
      form.reset();
      setEditUserId(null);
    } catch (err) {
      setError(err.message || "Failed to create/update user");
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditUser = (user) => {
    setEditUserId(user.id);
    form.reset(user);
    setIsDialogOpen(true);
  };

  const openCreateDialog = () => {
    setEditUserId(null);
    form.reset({ username: "", email: "", isAdmin: false }); // Reset form with default values
    setIsDialogOpen(true);
  };

  const handleDeleteUser = async () => {
    if (!deleteUserId) return;
    setIsLoading(true);
    try {
      await deleteUser(deleteUserId);
      setUsers(users.filter((user) => user.id !== deleteUserId));
      setIsDeleteDialogOpen(false);
      setDeleteUserId(null);
    } catch (err) {
      setError(err.message || "Failed to delete the user");
    } finally {
      setIsLoading(false);
    }
  };

  const confirmDeleteUser = (id) => {
    setDeleteUserId(id);
    setIsDeleteDialogOpen(true);
  };

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-6 flex items-center gap-2">
        <User className="h-8 w-8 text-blue-500" />
        User Management
      </h1>

      <div className="flex justify-end mb-4">
        <Button
          onClick={openCreateDialog}
          className="bg-blue-500 hover:bg-blue-600 text-white"
        >
          <Plus className="mr-2 h-4 w-4" /> Add User
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
        <p>Loading users...</p> // Replace with a more sophisticated loader if desired
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Username</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Admin</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id} className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800">
                <TableCell>{user.username}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>{user.isAdmin ? "Yes" : "No"}</TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleEditUser(user)}
                      className="hover:bg-gray-100"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="destructive"
                      size="icon"
                      onClick={() => confirmDeleteUser(user.id)}
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
            <DialogTitle>{editUserId ? "Edit User" : "Add User"}</DialogTitle>
            <DialogDescription>
              {editUserId
                ? "Make changes to the user below. Click save when you're done"
                : "Enter user details below"}
            </DialogDescription>
          </DialogHeader>
          <Form {...form}>
            <form
              // handleCreateOrUpdateUser receives form data as prop
              onSubmit={form.handleSubmit(handleCreateOrUpdateUser)}
              className="space-y-6"
            >
              <FormField
                control={form.control}
                name="username"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Username</FormLabel>
                    <FormControl>
                      <Input placeholder="Username" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input placeholder="Email" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="isAdmin"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between space-y-0">
                    <FormLabel>Admin</FormLabel>
                    <FormControl>
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          checked={field.value}
                          onCheckedChange={field.onChange}
                          className="border-gray-300"
                        />
                      </div>
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
                    setEditUserId(null);
                  }}
                  disabled={isLoading}
                  className="mr-2"
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Saving..." : "Save User"}
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
              user
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsDeleteDialogOpen(false);
                setDeleteUserId(null);
              }}
              disabled={isLoading}
              className="mr-2"
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteUser}
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

export default AdminUserManagement;
