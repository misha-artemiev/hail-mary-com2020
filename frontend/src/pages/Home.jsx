/**
 * Home.jsx
 * @author Ed Brown
 */

import React, { useState } from "react";

// Components
import Card from "../components/Card";
import FormInput from "../components/forms/FormInput";
import Button from "../components/forms/Button";
import Category from "../components/Category";
import DropdownSelect from "../components/forms/DropdownSelect";

/**
 * The main home page of the site, a feed of available bundles.
 *
 * @returns {JSX.Element} the home page
 */
export default function Home() {
    // State object: holds all fields for the form
    const [filters, setFilters] = useState({
        restaurant: "",
        category: "",
        allergens: [],
        maxPrice: "",
        maxDistance: "",
    });

    /**
     * Handles changes to the filters.
     */
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFilters((prev) => ({ ...prev, [name]: value }));
    };

    const handleCategoryClick = (category) => {
        console.log(filters);
        setFilters((prev) => ({
            ...prev,
            category: prev.category === category ? "" : category, // Can toggle on/off
        }));
    };

    const handleAllergensChange = (nextAllergens) => {
        setFilters((prev) => ({
            ...prev,
            allergens: nextAllergens,
        }));
    };

    /**
     * Handles submitting a search.
     */
    const handleSearch = () => {
        console.log(filters);
        // TODO: fetch filters
    };

    /**
     * Dynamically renders given categories.
     *
     * @param {Object} categories - The categories to display.
     * @returns {JSX.Element} a set of Category elements
     */
    const renderCategories = (categories) =>
        categories.map((category) => (
            <Category
                key={category.value}
                selected={filters.category === category.value}
                onClick={() => handleCategoryClick(category.value)}
            >
                {category.label}
            </Category>
        ));

    const CATEGORIES = [
        {
            value: "bakery",
            label: "Bakery",
        },
        {
            value: "grocery",
            label: "Grocery",
        },
        {
            value: "restaurant",
            label: "Restaurant",
        },
    ];

    const ALLERGENS = [
        {
            value: "nuts",
            label: "Nuts",
        },
        {
            value: "dairy",
            label: "Dairy",
        },
        {
            value: "gluten",
            label: "Gluten",
        },
        {
            value: "shellfish",
            label: "Shellfish",
        },
    ];

    return (
        <div className="max-w-8xl mx-auto p-6">
            <Card>
                <h2 className="text-xl font-semibold text-gray-700 mb-4">
                    Filters
                </h2>

                {/* Restaurant filter */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <FormInput
                        placeholder="Restaurant Name"
                        name="restaurant"
                        type="text"
                        value={filters.restaurant}
                        onChange={handleChange}
                    />

                    {/* Allergen filter */}
                    <select
                        name="allergen"
                        value={filters.allergen}
                        onChange={handleChange}
                        className="border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                    >
                        <option value="">No allergen filter</option>
                        <option value="nuts">Nuts</option>
                        <option value="dairy">Dairy</option>
                        <option value="gluten">Gluten</option>
                        <option value="shellfish">Shellfish</option>
                    </select>

                    <DropdownSelect
                        value={filters.allergens}
                        onChange={handleAllergensChange}
                        options={ALLERGENS}
                    />

                    {/* Max price filter */}
                    <FormInput
                        placeholder="Max Price (£)"
                        name="maxPrice"
                        type="number"
                        value={filters.maxPrice}
                        onChange={handleChange}
                    />

                    {/* Max distance filter */}
                    <FormInput
                        placeholder="Max Distance (km)"
                        name="maxDistance"
                        type="number"
                        value={filters.maxDistance}
                        onChange={handleChange}
                    />
                </div>

                {/* Categories div */}
                <div className="mt-4 flex flex-wrap gap-2">
                    {renderCategories(CATEGORIES)}
                </div>

                <Button onClick={handleSearch} className="w-md mt-4">
                    Search Bundles
                </Button>
            </Card>

            <Card>
                <p className="text-gray-600">No bundles yet</p>
            </Card>
        </div>
    );
}
