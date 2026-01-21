import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "shared-lib";
import { Button } from "shared-lib";
import {
  Users,
  Store,
  Package,
  ShoppingCart,
  ShoppingBag,
  LayoutDashboard,
} from "lucide-react";
/**
 * Issue: ../lib/utils.js is not found in the provided codebase
 * cn likely a utility function used for conditionally joining class names in React components. Often used with libraries like tailwind-merge or classnames to simplify process of applying CSS classes based on certain conditions
 * For example, it might be used to apply a different style to a button when it's disabled
 */
import { cn } from "shared-lib";
import { Link } from "react-router-dom";

const AdminDashboard = () => {
  const dashboardItems = [
    {
      title: "Users",
      description: "Manage users, roles, and permissions",
      icon: Users,
      route: "/admin/users",
    },
    {
      title: "Stores",
      description: "Manage stores, details, and settings",
      icon: Store,
      route: "/admin/stores",
    },
    {
      title: "Products",
      description: "Manage products, categories, and inventory",
      icon: ShoppingBag,
      route: "/admin/products",
    },
    {
      title: "Orders",
      description: "View and manage customer orders",
      icon: ShoppingCart,
      route: "/admin/orders",
    },
    {
      // Issue?: I don't see Route in AdminRoutes
      title: "Shipments",
      description: "Manage order shipments and tracking",
      icon: Package,
      route: "/admin/shipments",
    },
  ];

  return (
    <div className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 rounded shadow p-4">
      <h1 className="text-3xl font-bold mb-6 flex items-center gap-2">
        <LayoutDashboard className="h-8 w-8 text-blue-500" />
        Dashboard
      </h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/** When using React better to use Link from react-router-dom instead of href,
         * because it prevents full page reloads. As rule of thumb, use Link for internal navigation
         * and href for external links, because href will always cause a full page reload
         */}
        {dashboardItems.map((item) => (
          <Link key={item.title} to={item.route}>
            <Card
              className={cn(
                "transition-transform transform hover:scale-105",
                "border-2 border-gray-200 shadow-md hover:shadow-lg",
                "flex flex-col justify-between h-full" // Ensure cards are of equal height
              )}
            >
              <CardHeader>
                <div className="flex items-center gap-4">
                  <item.icon className="h-6 w-6 text-blue-500" />
                  <CardTitle className="text-xl font-semibold">
                    {item.title}
                  </CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">{item.description}</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
      <div className="mt-8">
        <h2 className="text-2xl font-semibold mb-4">Quick Actions</h2>
        <div className="flex flex-wrap gap-4">
          {/** Issue: These buttons are not linked to any routes. They are just placeholders and besides, they're redundant with the cards above. vsCode Copilot notices as best practice to leave only one of them. */}
          <Button variant="outline">
            <Users className="mr-2 h-4 w-4" /> Manage Users
          </Button>
          <Button variant="outline">
            <Store className="mr-2 h-4 w-4" /> Manage Stores
          </Button>
          <Button variant="outline">
            <ShoppingBag className="mr-2 h-4 w-4" /> Manage Products
          </Button>
          <Button variant="outline">
            <ShoppingCart className="mr-2 h-4 w-4" /> View Orders
          </Button>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
