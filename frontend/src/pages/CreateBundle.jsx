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

// Config
import { CREATE_BUNDLE_FORM_FIELDS } from "../config/createBundleFormFields";

/**
 * The bundle creation page of the site.
 * Allows sellers to create new bundles.
 * Not accessible to consumers (errors).
 *
 * @returns {JSX.Element} the bundle creation page
 */
export default function CreateBundle() {
    const navigate = useNavigate();
    const { userRole } = useAuth();

    // Use hooks to retrieve categories, allergens
    const { categoryOptions, loading: categoriesLoading } = useCategories();
    const { allergenOptions, loading: allergensLoading } = useAllergens();

    const { creating, createBundle } = useCreateBundle();

    // State object: stores form data
    const [form, setFormData] = useState({
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
            <div className="max-w-4xl mx-auto p-4 md:p-6">
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

        const result = await createBundle(form);
        navigate(`/bundles/${result.bundle_id}`);
    };

    /**
     * Dynamically renders given information fields.
     *
     * @param {Object} fields
     * @returns {JSX.Element} a set of FormInput elements.
     */
    const renderFields = (fields) =>
        fields.map((field) => (
            <FormInput
                key={field.name}
                label={field.label}
                name={field.name}
                type={field.type}
                min={field.min}
                max={field.max}
                step={field.step}
                value={form[field.name]}
                onChange={handleChange}
                required={field.required}
                placeholder={field.placeholder}
            />
        ));

    return (
        <div className="max-w-2xl mx-auto p-4 md:p-6">
            <Card>
                {/* Heading */}
                <h1 className="text-2xl font-bold text-green-700 mb-6">
                    Create New Bundle
                </h1>

                {/* Login form */}
                <form onSubmit={handleSubmit} className="space-y-4">
                    {renderFields(CREATE_BUNDLE_FORM_FIELDS.top)}

                    {/* Larger description container */}
                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">
                            Description
                        </label>
                        <textarea
                            name="description"
                            value={form.description}
                            onChange={handleChange}
                            required
                            rows={3}
                            placeholder="Describe what's in this bundle..."
                            className="w-full rounded-md px-3 py-2 border
                                       focus:ring-2 focus:ring-green-500
                                       focus:outline-none"
                        />
                    </div>

                    {/* 2-wide grid container */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {renderFields(CREATE_BUNDLE_FORM_FIELDS.grid)}
                    </div>

                    <Divider />

                    {/* Categories option dropdown */}
                    {!categoriesLoading && (
                        <DropdownSelect
                            options={categoryOptions}
                            value={form.categories}
                            name="category"
                            onChange={handleCategoriesChange}
                        />
                    )}

                    {/* Allergens option dropdown */}
                    {!allergensLoading && (
                        <DropdownSelect
                            options={allergenOptions}
                            value={form.allergens}
                            name="allergen"
                            onChange={handleAllergensChange}
                        />
                    )}

                    {/* Submit button */}
                    <SubmitButton disabled={creating}>
                        {creating ? "Creating Bundle..." : "Create Bundle"}
                    </SubmitButton>
                </form>
            </Card>
        </div>
    );
}
