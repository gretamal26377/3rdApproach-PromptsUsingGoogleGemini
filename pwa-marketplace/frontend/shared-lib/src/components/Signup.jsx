// @ts-nocheck
import React, { useMemo, useState, useEffect } from "react";
import api from "../services/api";
import CountryFlag from "react-country-flag";
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
  cityTown: "",
  stateRegion: "",
  postalCode: "",
  organisationId: "",
  storeId: "",
  roleCode: "supervisor",
};

const Signup = ({ onSignup }) => {
  const [formData, setFormData] = useState(initialState);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  // Dynamic options
  const [roleOptions, setRoleOptions] = useState([]);
  const [countryOptions, setCountryOptions] = useState([]);
  const [stateRegionOptions, setStateRegionOptions] = useState([]);
  const [cityTownOptions, setCityTownOptions] = useState([]);
  const [organisationOptions, setOrganisationOptions] = useState([]);
  const [storeOptions, setStoreOptions] = useState([]);

  // useMemo: Memoize the page copy to avoid unnecessary recalculations
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
    [] // Empty dependency array means this will only be calculated once on initial render
  );

  // Fetch Roles, Countries, Organisations on mount
  useEffect(() => {
    api
      .get("roles")
      .then((data) => setRoleOptions(data))
      .catch(() => setRoleOptions([]));
    api
      .get("countries")
      .then((data) => setCountryOptions(data))
      .catch(() => setCountryOptions([]));
    api
      .get("organisations")
      .then((data) => setOrganisationOptions(data))
      .catch(() => setOrganisationOptions([]));
  }, []);

  // Fetch States/Regions when Country changes
  useEffect(() => {
    if (formData.country) {
      api
        .get(`states-regions?country_id=${formData.country}`)
        .then((data) => setStateRegionOptions(data))
        .catch(() => setStateRegionOptions([]));
      setFormData((prev) => ({ ...prev, stateRegion: "", cityTown: "" }));
      setCityTownOptions([]);
    }
  }, [formData.country]);

  // Fetch Cities/Towns when State/Region changes
  useEffect(() => {
    if (formData.stateRegion) {
      api
        .get(`cities-towns?state_region_id=${formData.stateRegion}`)
        .then((data) => setCityTownOptions(data))
        .catch(() => setCityTownOptions([]));
      setFormData((prev) => ({ ...prev, cityTown: "" }));
    }
  }, [formData.stateRegion]);

  // Fetch Stores when Organisation changes
  useEffect(() => {
    if (formData.organisationId) {
      api
        .get(`stores?organisation_id=${formData.organisationId}`)
        .then((data) => setStoreOptions(data))
        .catch(() => setStoreOptions([]));
      setFormData((prev) => ({ ...prev, storeId: "" }));
    }
  }, [formData.organisationId]);

  // Function to update form field values. It takes the field name as an argument and returns a function
  // that takes an event (from the input change) and updates the corresponding field in formData state
  // with the new value from the input
  const updateField = (field) => (event) => {
    setFormData((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const validate = () => {
    if (formData.password !== formData.confirmPassword) {
      return "Passwords do not match";
    }

    // For each field of the required fields, it checks if the field is empty in formData.
    // If it is empty, it adds the field name to the missingBasics array
    const missingBasics = [
      "name",
      "email",
      "password",
      "confirmPassword",
      "phone",
    ].filter((field) => !formData[field]);

    // If missingBasics array is not empty, it means there are required fields that are not filled in,
    // so it returns an error message asking the user to fill in all required fields
    if (missingBasics.length) {
      return "Please fill in all required fields";
    }

    if (isCustomerApp) {
      const missingAddress = [
        "addressLine1",
        "cityTown",
        "stateRegion",
        "postalCode",
      ].filter((field) => !formData[field]);

      if (missingAddress.length) {
        return "Please complete your address";
      }
    }

    // For admin app, we don't have any additional required fields beyond the basics, so we can skip to the end
    return "";
  };

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent default form submission
    setError("");

    const validationError = validate();
    // If validationError is not an empty string, it means there was a validation error,
    // so we set the error state to the validation error message and return early to prevent further processing
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
            city_town: formData.cityTown,
            state_region: formData.stateRegion,
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
      if (isCustomerApp) {
        setError("Failed to create Customer. Please try again");
      } else {
        setError("Failed to create User. Please try again");
      }
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
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                type="text"
                placeholder="Jane Doe" style={{ fontStyle: 'italic' }}
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
                placeholder="jane@example.com" style={{ fontStyle: 'italic' }}
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
                placeholder="+Country Code Phone Number: +999 999999999" style={{ fontStyle: 'italic' }}
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
                placeholder="Enter your password" style={{ fontStyle: 'italic' }}
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
                placeholder="Re-enter your password" style={{ fontStyle: 'italic' }}
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
                  <Label htmlFor="addressLine1">Address Line 1</Label>
                  <Input
                    id="addressLine1"
                    type="text"
                    placeholder="123 Main St" style={{ fontStyle: 'italic' }}
                    value={formData.addressLine1}
                    onChange={updateField("addressLine1")}
                    disabled={isLoading}
                  />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="addressLine2">
                    Address Line 2 (optional)
                  </Label>
                  <Input
                    id="addressLine2"
                    type="text"
                    placeholder="Apartment, suite, etc." style={{ fontStyle: 'italic' }}
                    value={formData.addressLine2}
                    onChange={updateField("addressLine2")}
                    disabled={isLoading}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="country">Country</Label>
                  <select
                    id="country"
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                    value={formData.country || ""}
                    onChange={updateField("country")}
                    disabled={isLoading}
                  >
                    <option value="" disabled style={{ fontStyle: 'italic' }}>Select Country</option>
                    {countryOptions.map((country) => (
                      <option key={country.value} value={country.value}>
                        {/* Show flag if country.code exists */}
                        {country.code && (
                          <CountryFlag countryCode={country.code} svg style={{ marginRight: 8 }} />
                        )}
                        {country.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="stateRegion">State/Region/Province</Label>
                  <select
                    id="stateRegion"
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                    value={formData.stateRegion || ""}
                    onChange={updateField("stateRegion")}
                    disabled={isLoading || !formData.country}
                  >
                    <option value="" disabled style={{ fontStyle: 'italic' }}>Select State/Region</option>
                    {stateRegionOptions.map((state) => (
                      <option key={state.value} value={state.value}>
                        {state.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="cityTown">City/Town</Label>
                  <select
                    id="cityTown"
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                    value={formData.cityTown || ""}
                    onChange={updateField("cityTown")}
                    disabled={isLoading || !formData.stateRegion}
                  >
                    <option value="" disabled style={{ fontStyle: 'italic' }}>Select City/Town</option>
                    {cityTownOptions.map((city) => (
                      <option key={city.value} value={city.value}>
                        {city.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="postalCode">Postal Code</Label>
                  <Input
                    id="postalCode"
                    type="text"
                    placeholder="12345" style={{ fontStyle: 'italic' }}
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
                User Details
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="organisation">Organisation</Label>
                  <select
                    id="organisation"
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                    value={formData.organisationId || ""}
                    onChange={updateField("organisationId")}
                    disabled={isLoading}
                  >
                    <option value="" disabled style={{ fontStyle: 'italic' }}>Select Organisation</option>
                    {organisationOptions.map((org) => (
                      <option key={org.value} value={org.value}>
                        {org.icon_path && (
                          <img src={org.icon_path} alt="icon" style={{ width: 18, height: 18, display: 'inline', marginRight: 6, verticalAlign: 'middle' }} />
                        )}
                        {org.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="store">Store</Label>
                  <select
                    id="store"
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                    value={formData.storeId || ""}
                    onChange={updateField("storeId")}
                    disabled={isLoading || !formData.organisationId}
                  >
                    <option value="" disabled style={{ fontStyle: 'italic' }}>Select Store</option>
                    {storeOptions.map((store) => (
                      <option key={store.value} value={store.value}>
                        {store.label}
                      </option>
                    ))}
                  </select>
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
                    Store-Management-Only
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
