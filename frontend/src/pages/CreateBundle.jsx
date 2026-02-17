/**
 * CreateBundle.jsx
 * @author Thomas Noakes
 */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

// Authentication
import { useAuth } from "../context/AuthContext";

// Hooks
import useCategories from "../hooks/useCategories";
import useAllergens from "../hooks/useAllergens";
import useCreateBundle from "../hooks/useCreateBundle";

// Components
import Card from "../components/Card";
import Button from "../components/forms/Button";
import FormInput from "../components/forms/FormInput";
import DropdownSelect from "../components/forms/DropdownSelect";
import SubmitButton from "../components/forms/SubmitButton";
import Divider from "../components/Divider";

export default function CreateBundle() {
    const navigate = useNavigate();
    const { userRole } = useAuth();

    // Use hooks to retrieve categories, allergens
    const { categoryOptions, loading: categoriesLoading } = useCategories();
    const { allergenOptions, loading: allergensLoading } = useAllergens();

    const { creating, createBundle } = useCreateBundle();

    // State object: stores form data
    const [formData, setFormData] = useState({
        bundle_name: "",
        description: "",
        price: "",
        total_qty: 1,
        discount_percentage: "",
        window_start: "",
        window_end: "",
        categories: [],
        allergens: [],
    });

    // Not accessible if the user is a consumer
    if (userRole !== "seller") {
        return (
            <div className="max-w-4xl mx-auto p-6">
                <Card className="flex flex-col items-centre text-center gap-6">
                    {/* Header */}
                    <h1 className="text-3xl font-bold text-green-700">
                        Access Error
                    </h1>

                    <p className="text-gray-600 mb-6">
                        This page is only accessible to sellers.
                    </p>
                    <Button onClick={() => navigate("/")}>Go Home</Button>
                </Card>
            </div>
        );
    }

    /**
     * Handles changes to the form.
     */
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    /**
     * Handles changes to the categories dropdown.
     */
    const handleCategoriesChange = (selected) => {
        setFormData((prev) => ({ ...prev, categories: selected }));
    };

    /**
     * Handles changes to the allergens dropdown.
     */
    const handleAllergensChange = (selected) => {
        setFormData((prev) => ({ ...prev, allergens: selected }));
    };

    /**
     * Handles submitting the form.
     * Uses the `createBundle` custom hook.
     * Redirects to the new bundle page.
     */
    const handleSubmit = async (e) => {
        e.preventDefault();

        const result = await createBundle(formData);
        navigate(`/bundles/${result.bundle_id}`);
    };

    return (
        <div className="max-w-2xl mx-auto p-6">
            <Card>
                {/* Heading */}
                <h1 className="text-2xl font-bold text-green-700 mb-6">
                    Create New Bundle
                </h1>

                {/* Login form */}
                <form onSubmit={handleSubmit} className="space-y-4">
                    <FormInput
                        label="Bundle Name"
                        name="bundle_name"
                        value={formData.bundle_name}
                        onChange={handleChange}
                        required
                        placeholder="e.g., Evening Surprise Bag"
                    />

                    {/* Larger description container */}
                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">
                            Description
                        </label>
                        <textarea
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            required
                            rows={3}
                            placeholder="Describe what's in this bundle..."
                            className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500 focus:outline-none"
                        />
                    </div>

                    {/* Quantity */}
                    <FormInput
                        label="Total Quantity"
                        type="number"
                        min="1"
                        step="1"
                        name="total_qty"
                        value={formData.total_qty}
                        onChange={handleChange}
                        required
                    />

                    {/* 2-wide grid container */}
                    <div className="grid grid-cols-2 gap-4">
                        {/* Original price */}
                        <FormInput
                            label="Original Price (£)"
                            name="price"
                            type="number"
                            min="0"
                            step="0.5"
                            value={formData.price}
                            onChange={handleChange}
                            required
                            placeholder="10.00"
                        />

                        {/* Discount percentage */}
                        <FormInput
                            label="Discount (%)"
                            name="discount_percentage"
                            type="number"
                            min="0"
                            max="100"
                            value={formData.discount_percentage}
                            onChange={handleChange}
                            required
                            placeholder="50"
                        />

                        {/* Available from */}
                        <FormInput
                            label="Pickup Window Start"
                            name="window_start"
                            type="datetime-local"
                            value={formData.window_start}
                            onChange={handleChange}
                            required
                        />

                        {/* Available until */}
                        <FormInput
                            label="Pickup Window End"
                            name="window_end"
                            type="datetime-local"
                            value={formData.window_end}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <Divider />

                    {/* Categories option dropdown */}
                    {!categoriesLoading && (
                        <DropdownSelect
                            options={categoryOptions}
                            value={formData.categories}
                            name="category"
                            onChange={handleCategoriesChange}
                        />
                    )}

                    {!allergensLoading && (
                        <DropdownSelect
                            options={allergenOptions}
                            value={formData.allergens}
                            name="allergen"
                            onChange={handleAllergensChange}
                        />
                    )}

                    <SubmitButton disabled={creating}>
                        {creating ? "Creating Bundle..." : "Create Bundle"}
                    </SubmitButton>
                </form>
            </Card>
        </div>
    );
}
