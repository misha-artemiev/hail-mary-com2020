/**
 * Home.jsx
 * @author Ed Brown
 */

import React, { useState } from "react";

// Components
import Card from "../components/Card";
import FormInput from "../components/forms/FormInput";

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
        allergen: "",
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

    /**
     * Handles submitting a search.
     */
    const handleSearch = () => {
        // TODO: fetch filters
    };

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

                    {/* Category filter */}
                    <select
                        name="category"
                        value={filters.category}
                        onChange={handleChange}
                        className="border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                    >
                        <option value="">All categories</option>
                        <option value="bakery">Bakery</option>
                        <option value="grocery">Supermarket</option>
                        <option value="restaurant">Restaurant</option>
                    </select>

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

                <button
                    onClick={handleSearch}
                    className="mt-6 bg-green-600 text-white px-6 py-3 rounded-md font-semibold
                                hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                    Search Bundles
                </button>
            </Card>

            <Card>
                <p className="text-gray-600">No bundles yet</p>
            </Card>
        </div>
    );
}
