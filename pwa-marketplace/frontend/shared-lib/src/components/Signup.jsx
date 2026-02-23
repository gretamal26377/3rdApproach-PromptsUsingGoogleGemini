// @ts-nocheck
import React, { useMemo, useState, useEffect } from "react";
import api from "../services/api";
import CountryFlag from "react-country-flag";
import {
  Form,
  FormLabel,
  FormField,
  FormItem,
  FormControl,
  FormMessage,
} from "./ui/form";
import Input from "./ui/input";
import Checkbox from "./ui/checkbox";
import Dropdown from "./ui/dropdown";
import Button from "./ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "./ui/card";
import { Alert, AlertDescription, AlertTitle } from "./ui/alert";
import { AlertCircle } from "lucide-react";

const APP_TYPE = (import.meta.env.VITE_APP_TYPE || "customer").toLowerCase();
const isCustomerApp = APP_TYPE === "customer";

const emptyAddress = {
  addressLine1: "",
  addressLine2: "",
  countryId: "",
  cityTownId: "",
  stateRegionId: "",
  google_maps_url: "",
  postalCode: "",
};

const initialState = {
  name: "",
  email: "",
  password: "",
  confirmPassword: "",
  phone: "",
  addresses: [{ ...emptyAddress }], // At least one address required
  organisationId: "",
  roleCode: "supervisor",
  // For admin app, we will allow multi-store selection, so we store selected store IDs in an array
  selectedStoreIds: [],
};

const Signup = ({ onSignup }) => {
  const [formData, setFormData] = useState(initialState);
  // Multi-Store selection is now part of formData
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  // Dynamic options
  const [roleOptions, setRoleOptions] = useState([]);
  const [countryOptions, setCountryOptions] = useState([]);
  const [stateRegionOptions, setStateRegionOptions] = useState([]);
  const [cityTownOptions, setCityTownOptions] = useState([]);
  const [organisationOptions, setOrganisationOptions] = useState([]);
  const [storeOptions, setStoreOptions] = useState([]);
  // Track which address is being edited (for multi-address UI)
  const [activeAddressIdx, setActiveAddressIdx] = useState(0);

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

  // Fetch States/Regions when Country changes (for active address)
  useEffect(() => {
    const addr = formData.addresses[activeAddressIdx] || {};
    if (addr.countryId) {
      api
        .get(`states-regions?country_id=${addr.countryId}`)
        .then((data) => setStateRegionOptions(data))
        .catch(() => setStateRegionOptions([]));
      updateAddressField("stateRegionId", "");
      updateAddressField("cityTownId", "");
      setCityTownOptions([]);
    }
    // eslint-disable-next-line
  }, [formData.addresses[activeAddressIdx]?.countryId]);

  // Fetch Cities/Towns when State/Region changes (for active address)
  useEffect(() => {
    const addr = formData.addresses[activeAddressIdx] || {};
    if (addr.stateRegionId) {
      api
        .get(`cities-towns?state_region_id=${addr.stateRegionId}`)
        .then((data) => setCityTownOptions(data))
        .catch(() => setCityTownOptions([]));
      updateAddressField("cityTownId", "");
    }
    // eslint-disable-next-line
  }, [formData.addresses[activeAddressIdx]?.stateRegionId]);

  // Fetch Stores when Organisation changes
  useEffect(() => {
    if (formData.organisationId) {
      api
        .get(`stores?organisation_id=${formData.organisationId}`)
        .then((data) => setStoreOptions(data))
        .catch(() => setStoreOptions([]));
      setFormData((prev) => ({ ...prev, selectedStoreIds: [] }));
    }
  }, [formData.organisationId]);

  // Function to update form field values. It takes the field name as an argument and returns a function
  // that takes an event (from the input change) and updates the corresponding field in formData state
  // with the new value from the input
  const updateField = (field) => (event) => {
    setFormData((prev) => ({ ...prev, [field]: event.target.value }));
  };

  // Update a field in the active address
  const updateAddressField = (field, valueOrEvent) => {
    setFormData((prev) => {
      const addresses = [...prev.addresses];
      // Determine the value based on whether valueOrEvent is an event object or a direct value
      const value =
        valueOrEvent && valueOrEvent.target
          ? valueOrEvent.target.value
          : valueOrEvent;
      addresses[activeAddressIdx] = {
        ...addresses[activeAddressIdx],
        [field]: value,
      };
      return { ...prev, addresses };
    });
  };

  // Add a new empty address
  const addAddress = () => {
    setFormData((prev) => ({
      ...prev,
      addresses: [...prev.addresses, { ...emptyAddress }],
    }));
    setActiveAddressIdx(formData.addresses.length); // focus new address
  };

  // Remove an address (cannot remove if only one left)
  const removeAddress = (idx) => {
    setFormData((prev) => {
      if (prev.addresses.length === 1) return prev;
      const addresses = prev.addresses.filter((_, i) => i !== idx);
      return { ...prev, addresses };
    });
    setActiveAddressIdx(0);
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
      // Validate all addresses, but require at least one complete
      const hasValidAddress = formData.addresses.some(
        (addr) =>
          addr.addressLine1 &&
          addr.countryId &&
          addr.stateRegionId &&
          addr.cityTownId &&
          addr.google_maps_url
      );
      if (!hasValidAddress) {
        return "Please complete at least one Address";
      }
    }

    // For admin app, we don't have any additional required fields beyond the basics, so we can skip to the end
    return "";
  };

  const handleStoreCheckboxChange = (storeId) => {
    setFormData((prev) => {
      const prevIds = prev.selectedStoreIds || [];
      let newIds;
      if (prevIds.includes(storeId)) {
        // if prevIds already includes the storeId, it means the user is unchecking the box,
        // so we create a new array that filters out that storeId
        newIds = prevIds.filter((id) => id !== storeId);
      } else {
        newIds = [...prevIds, storeId];
      }
      return { ...prev, selectedStoreIds: newIds };
    });
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
          addresses: formData.addresses.map((addr) => ({
            address_line1: addr.addressLine1,
            address_line2: addr.addressLine2,
            country_id: addr.countryId,
            state_region_id: addr.stateRegionId,
            city_town_id: addr.cityTownId,
            google_maps_url: addr.google_maps_url,
            postal_code: addr.postalCode,
          })),
        }
      : {
          user_name: formData.name,
          user_email: formData.email,
          user_password: formData.password,
          user_phone: formData.phone,
          user_organisation_id: formData.organisationId,
          user_role_code: formData.roleCode,
          user_store_ids: formData.selectedStoreIds,
        };

    // Store the first Address as default in localStorage for Customer
    if (isCustomerApp && formData.addresses.length > 0) {
      localStorage.setItem(
        "defaultDeliveryAddress",
        JSON.stringify(formData.addresses[0])
      );
    }

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
        <Form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField>
              <FormLabel htmlFor="name">Full Name</FormLabel>
              <FormControl>
                <Input
                  id="name"
                  type="text"
                  placeholder="Jane Doe"
                  value={formData.name}
                  onChange={updateField("name")}
                  disabled={isLoading}
                />
              </FormControl>
            </FormField>
            <FormField>
              <FormLabel htmlFor="email">Email</FormLabel>
              <FormControl>
                <Input
                  id="email"
                  type="email"
                  placeholder="jane@example.com"
                  value={formData.email}
                  onChange={updateField("email")}
                  disabled={isLoading}
                />
              </FormControl>
            </FormField>
            <FormField>
              <FormLabel htmlFor="phone">Phone</FormLabel>
              <FormControl>
                <Input
                  id="phone"
                  type="tel"
                  placeholder="+Country Code Phone Number: +999 999999999"
                  value={formData.phone}
                  onChange={updateField("phone")}
                  disabled={isLoading}
                />
              </FormControl>
            </FormField>
            <FormField>
              <FormLabel htmlFor="password">Password</FormLabel>
              <FormControl>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={updateField("password")}
                  disabled={isLoading}
                />
              </FormControl>
            </FormField>
            <FormField>
              <FormLabel htmlFor="confirmPassword">Confirm password</FormLabel>
              <FormControl>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="Re-enter your password"
                  value={formData.confirmPassword}
                  onChange={updateField("confirmPassword")}
                  disabled={isLoading}
                />
              </FormControl>
            </FormField>
          </div>

          {isCustomerApp && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-gray-700">Addresses</h3>
              <div className="flex gap-2 mb-2">
                {formData.addresses.map((addr, idx) => (
                  <Button
                    key={idx}
                    type="button"
                    variant={activeAddressIdx === idx ? "secondary" : "outline"}
                    size="sm"
                    className={`text-xs ${
                      activeAddressIdx === idx ? "border-blue-500" : ""
                    }`}
                    onClick={() => setActiveAddressIdx(idx)}
                    disabled={isLoading}
                  >
                    {`Address ${idx + 1}`}
                    {idx === 0 && " (Default)"}
                  </Button>
                ))}
                <Button
                  type="button"
                  variant="success"
                  size="sm"
                  className="text-xs ml-2"
                  onClick={addAddress}
                  disabled={isLoading}
                >
                  + Add Address
                </Button>
                {formData.addresses.length > 1 && (
                  <Button
                    type="button"
                    variant="destructive"
                    size="sm"
                    className="text-xs ml-2"
                    onClick={() => removeAddress(activeAddressIdx)}
                    disabled={isLoading}
                  >
                    Remove
                  </Button>
                )}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField>
                  <FormLabel htmlFor="addressLine1">Address Line 1</FormLabel>
                  <FormControl>
                    <Input
                      id="addressLine1"
                      type="text"
                      placeholder="123 Main St"
                      value={
                        formData.addresses[activeAddressIdx]?.addressLine1 || ""
                      }
                      onChange={(e) => updateAddressField("addressLine1", e)}
                      disabled={isLoading}
                    />
                  </FormControl>
                </FormField>
                <FormField>
                  <FormLabel htmlFor="addressLine2">
                    Address Line 2 (optional)
                  </FormLabel>
                  <FormControl>
                    <Input
                      id="addressLine2"
                      type="text"
                      placeholder="Apartment, suite, etc."
                      value={
                        formData.addresses[activeAddressIdx]?.addressLine2 || ""
                      }
                      onChange={(e) => updateAddressField("addressLine2", e)}
                      disabled={isLoading}
                    />
                  </FormControl>
                </FormField>
                <FormField>
                  <FormLabel htmlFor="countryId">Country</FormLabel>
                  <FormControl>
                    <Dropdown
                      id="countryId"
                      value={
                        formData.addresses[activeAddressIdx]?.countryId || ""
                      }
                      onChange={(e) => updateAddressField("countryId", e)}
                      disabled={isLoading}
                    >
                      <option value="" disabled>
                        Select Country
                      </option>
                      {countryOptions.map((country) => (
                        <option key={country.value} value={country.value}>
                          {country.code && (
                            <CountryFlag
                              countryCode={country.code}
                              svg
                              style={{ marginRight: 8 }}
                            />
                          )}
                          {country.label}
                        </option>
                      ))}
                    </Dropdown>
                  </FormControl>
                </FormField>
                <FormField>
                  <FormLabel htmlFor="stateRegionId">
                    State/Region/Province
                  </FormLabel>
                  <FormControl>
                    <Dropdown
                      id="stateRegionId"
                      value={
                        formData.addresses[activeAddressIdx]?.stateRegionId ||
                        ""
                      }
                      onChange={(e) => updateAddressField("stateRegionId", e)}
                      disabled={
                        isLoading ||
                        !formData.addresses[activeAddressIdx]?.countryId
                      }
                    >
                      <option value="" disabled>
                        Select State/Region
                      </option>
                      {stateRegionOptions.map((state) => (
                        <option key={state.value} value={state.value}>
                          {state.label}
                        </option>
                      ))}
                    </Dropdown>
                  </FormControl>
                </FormField>
                <FormField>
                  <FormLabel htmlFor="cityTownId">City/Town</FormLabel>
                  <FormControl>
                    <Dropdown
                      id="cityTownId"
                      value={
                        formData.addresses[activeAddressIdx]?.cityTownId || ""
                      }
                      onChange={(e) => updateAddressField("cityTownId", e)}
                      disabled={
                        isLoading ||
                        !formData.addresses[activeAddressIdx]?.stateRegionId
                      }
                    >
                      <option value="" disabled>
                        Select City/Town
                      </option>
                      {cityTownOptions.map((city) => (
                        <option key={city.value} value={city.value}>
                          {city.label}
                        </option>
                      ))}
                    </Dropdown>
                  </FormControl>
                </FormField>
                <FormField>
                  <FormLabel htmlFor="google_maps_url">
                    Google Maps URL
                  </FormLabel>
                  <FormControl>
                    <Input
                      id="google_maps_url"
                      type="url"
                      placeholder="Paste Google Maps URL here"
                      value={
                        formData.addresses[activeAddressIdx]?.google_maps_url ||
                        ""
                      }
                      onChange={(e) => updateAddressField("google_maps_url", e)}
                      disabled={isLoading}
                    />
                  </FormControl>
                </FormField>
                <FormField>
                  <FormLabel htmlFor="postalCode">Postal Code</FormLabel>
                  <FormControl>
                    <Input
                      id="postalCode"
                      type="text"
                      placeholder="12345"
                      value={
                        formData.addresses[activeAddressIdx]?.postalCode || ""
                      }
                      onChange={(e) => updateAddressField("postalCode", e)}
                      disabled={isLoading}
                    />
                  </FormControl>
                </FormField>
              </div>
            </div>
          )}

          {!isCustomerApp && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-gray-700">
                User Details
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField>
                  <FormLabel htmlFor="organisation">Organisation</FormLabel>
                  <FormControl>
                    <Dropdown
                      id="organisation"
                      value={formData.organisationId || ""}
                      onChange={updateField("organisationId")}
                      disabled={isLoading}
                    >
                      <option value="" disabled>
                        Select Organisation
                      </option>
                      {organisationOptions.map((org) => (
                        <option key={org.value} value={org.value}>
                          {org.icon_path && (
                            <img
                              src={org.icon_path}
                              alt="icon"
                              style={{
                                width: 18,
                                height: 18,
                                display: "inline",
                                marginRight: 6,
                                verticalAlign: "middle",
                              }}
                            />
                          )}
                          {org.label}
                        </option>
                      ))}
                    </Dropdown>
                  </FormControl>
                </FormField>
                <FormField>
                  <FormLabel>Store(s)</FormLabel>
                  <FormControl>
                    <Dropdown
                      id="storeDropdown"
                      value=""
                      onChange={() => {}}
                      disabled={isLoading || !formData.organisationId}
                      className="relative"
                    >
                      <option value="" disabled>
                        {formData.selectedStoreIds.length === 0
                          ? "Select Store(s)"
                          : `${formData.selectedStoreIds.length} Store(s) Selected`}
                      </option>
                    </Dropdown>
                    {/* Custom Dropdown menu for Store selection */}
                    <div
                      className="absolute z-10 mt-2 w-full bg-white dark:bg-gray-900 border rounded-md shadow-lg"
                      style={{ display: "block" }}
                    >
                      {storeOptions.length === 0 && (
                        <span className="text-gray-400 italic text-sm px-3 py-2 block">
                          No Stores available
                        </span>
                      )}
                      {storeOptions.map((store) => (
                        <label
                          key={store.value}
                          className="flex items-center gap-2 cursor-pointer px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800"
                        >
                          <Checkbox
                            checked={formData.selectedStoreIds.includes(
                              store.value
                            )}
                            onChange={() =>
                              handleStoreCheckboxChange(store.value)
                            }
                            disabled={isLoading || !formData.organisationId}
                          />
                          <span>{store.label}</span>
                        </label>
                      ))}
                    </div>
                  </FormControl>
                  <p className="text-xs text-gray-500 mt-1 italic">
                    Select one or more Stores where the User will have access
                  </p>
                </FormField>
                <FormField className="md:col-span-2">
                  <FormLabel htmlFor="role">Role</FormLabel>
                  <FormControl>
                    <Dropdown
                      id="role"
                      value={formData.roleCode}
                      onChange={updateField("roleCode")}
                      disabled={isLoading}
                    >
                      {roleOptions.map((role) => (
                        <option key={role.value} value={role.value}>
                          {role.label}
                        </option>
                      ))}
                    </Dropdown>
                  </FormControl>
                </FormField>
              </div>
            </div>
          )}

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "Working..." : pageCopy.cta}
          </Button>
        </Form>

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
