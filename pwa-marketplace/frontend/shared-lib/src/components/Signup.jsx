// @ts-nocheck
import React, { useMemo, useState } from "react";
import Button from "./ui/button";
import Input from "./ui/input";
import Label from "./ui/label";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "./ui/card";
import { Alert, AlertDescription, AlertTitle } from "./ui/alert";
import { AlertCircle } from "lucide-react";

const appType = (import.meta.env.VITE_APP_TYPE || "customer").toLowerCase();
const isCustomerApp = appType === "customer";

const initialState = {
  name: "",
  email: "",
  phone: "",
  password: "",
  confirmPassword: "",
  addressLine1: "",
  addressLine2: "",
  city: "",
  state: "",
  postalCode: "",
  organisationId: "",
  storeId: "",
  roleCode: "supervisor",
};

const roleOptions = [
  { value: "admin", label: "Admin" },
  { value: "supervisor", label: "Supervisor" },
  { value: "agent", label: "Agent" },
];

const Signup = ({ onSignup }) => {
  const [formData, setFormData] = useState(initialState);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const pageCopy = useMemo(
    () =>
      isCustomerApp
        ? {
            title: "Sign Up",
            description: "Create your Customer Account",
            cta: "Create Customer",
          }
        : {
            title: "Add User",
            description: "Create a User",
            cta: "Create User",
          },
    []
  );

  const updateField = (field) => (event) => {
    setFormData((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const validate = () => {
    if (formData.password !== formData.confirmPassword) {
      return "Passwords do not match";
    }

    const missingBasics = [
      "name",
      "email",
      "password",
      "confirmPassword",
      "phone",
    ].filter((field) => !formData[field]);

    if (missingBasics.length) {
      return "Please fill in all required fields";
    }

    if (isCustomerApp) {
      const missingAddress = [
        "addressLine1",
        "city",
        "state",
        "postalCode",
      ].filter((field) => !formData[field]);
      if (missingAddress.length) {
        return "Please complete your address";
      }
    }

    return "";
  };

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent default form submission
    setError("");

    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsLoading(true);

    const payload = isCustomerApp
      ? {
          customer_name: formData.name,
          customer_email: formData.email,
          customer_password: formData.password,
          customer_phone: formData.phone,
          address: {
            address_line1: formData.addressLine1,
            address_line2: formData.addressLine2,
            city: formData.city,
            state: formData.state,
            postal_code: formData.postalCode,
          },
        }
      : {
          user_name: formData.name,
          user_email: formData.email,
          user_password: formData.password,
          user_phone: formData.phone,
          user_role_code: formData.roleCode,
          user_store_id: formData.storeId,
          user_organisation_id: formData.organisationId,
        };

    try {
      await onSignup(payload);
    } catch (err) {
      setError("Failed to create Customer. Please try again");
      // Executed after try/catch block, regardless of success or failure
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-3xl mx-auto">
      <CardHeader>
        <CardTitle>{pageCopy.title}</CardTitle>
        <CardDescription>{pageCopy.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Full name</Label>
              <Input
                id="name"
                type="text"
                placeholder="Jane Doe"
                value={formData.name}
                onChange={updateField("name")}
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="jane@example.com"
                value={formData.email}
                onChange={updateField("email")}
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Phone</Label>
              <Input
                id="phone"
                type="tel"
                placeholder="555-123-4567"
                value={formData.phone}
                onChange={updateField("phone")}
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={formData.password}
                onChange={updateField("password")}
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm password</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Re-enter your password"
                value={formData.confirmPassword}
                onChange={updateField("confirmPassword")}
                disabled={isLoading}
              />
            </div>
          </div>

          {isCustomerApp && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-gray-700">Address</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="addressLine1">Address line 1</Label>
                  <Input
                    id="addressLine1"
                    type="text"
                    placeholder="123 Main St"
                    value={formData.addressLine1}
                    onChange={updateField("addressLine1")}
                    disabled={isLoading}
                  />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="addressLine2">
                    Address line 2 (optional)
                  </Label>
                  <Input
                    id="addressLine2"
                    type="text"
                    placeholder="Apartment, suite, etc."
                    value={formData.addressLine2}
                    onChange={updateField("addressLine2")}
                    disabled={isLoading}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="city">City</Label>
                  <Input
                    id="city"
                    type="text"
                    placeholder="City"
                    value={formData.city}
                    onChange={updateField("city")}
                    disabled={isLoading}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="state">State / Province</Label>
                  <Input
                    id="state"
                    type="text"
                    placeholder="State"
                    value={formData.state}
                    onChange={updateField("state")}
                    disabled={isLoading}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="postalCode">Postal code</Label>
                  <Input
                    id="postalCode"
                    type="text"
                    placeholder="12345"
                    value={formData.postalCode}
                    onChange={updateField("postalCode")}
                    disabled={isLoading}
                  />
                </div>
              </div>
            </div>
          )}

          {!isCustomerApp && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-gray-700">
                User details
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="organisation">Organisation ID</Label>
                  <Input
                    id="organisation"
                    type="text"
                    placeholder="e.g. 12"
                    value={formData.organisationId}
                    onChange={updateField("organisationId")}
                    disabled={isLoading}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="store">Store ID</Label>
                  <Input
                    id="store"
                    type="text"
                    placeholder="e.g. 101"
                    value={formData.storeId}
                    onChange={updateField("storeId")}
                    disabled={isLoading}
                  />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="role">Role</Label>
                  <select
                    id="role"
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                    value={formData.roleCode}
                    onChange={updateField("roleCode")}
                    disabled={isLoading}
                  >
                    {roleOptions.map((role) => (
                      <option key={role.value} value={role.value}>
                        {role.label}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    Admin and Supervisor can create users. Agents are
                    Store-Management-only
                  </p>
                </div>
              </div>
            </div>
          )}

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "Working..." : pageCopy.cta}
          </Button>
        </form>

        {error && (
          <Alert variant="destructive" className="mt-4">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default Signup;
