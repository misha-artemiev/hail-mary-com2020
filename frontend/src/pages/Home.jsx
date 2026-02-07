/**
 * Home.jsx
 * @author Ed Brown
 */

import React, { useState } from "react";

/**
 * The main home page of the site, a feed of available bundles.
 *
 * @returns {JSX.Element} the home page
 */
export default function Home() {

    const [filters, setFilters] = useState({
        restaurant: "",
        category: "",
        allergen: "",
        maxPrice: "",
        maxDistance: ""
    })

    const handleChange = (e) => {
        const { name, value  } = e.target;
        setFilters((prev) => ({ ...prev, [name]: value }));
    };

    const handleSearch = () => {
        console.log("Filters used:", filters);
        // TODO: FETCH BUNDLES WITH FILTERS FROM BACKEND HERE
    }

    return (
        <div className="max-w-6xl mx-auto p-6">
            <h1 className="text-3xl font-bold text-green-700 mb-6">Rescue Marketplace</h1>

            <div className="bg-white shadow-md rounded-lg p-6 mb-8">
                <h2 className="text-xl font-semibold text-gray-700 mb-4">Filters</h2>
                {/* Restaurant Filter */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <input
                        type="text"
                        name="restaurant"
                        placeholder="Restaurant Name"
                        value={filters.restaurant}
                        onChange={handleChange}
                        className="border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"/>
                    {/* Category Filter */}
                    <select
                        name="category"
                        value={filters.category}
                        onChange={handleChange}
                        className="border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500">
                        <option value="">All categories</option>
                        <option value="bakery">Bakery</option>
                        <option value="grocery">Supermarket</option>
                        <option value="restaurant">Restaurant</option>
                        {/*MORE CATEGORIES CAN BE ADDED HERE*/}
                    </select>
                    {/* Allergen Filter */}
                    <select
                        name="allergen"
                        value={filters.allergen}
                        onChange={handleChange}
                        className="border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500">
                        <option value="">No allergen filter</option>
                        <option value="nuts">Nuts</option>
                        <option value="dairy">Dairy</option>
                        <option value="gluten">Gluten</option>
                        <option value="shellfish">Shellfish</option>
                        {/*MORE ALLERGENS CAN BE ADDED HERE*/}
                    </select>
                    {/* Max Price Filter */}
                    <input
                        type="number"
                        name="maxPrice"
                        placeholder="Max Price (£)"
                        value={filters.maxPrice}
                        onChange={handleChange}
                        className="border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"/>
                    {/* Max Distance Filter */}
                    <input
                        type="number"
                        name="maxDistance"
                        placeholder="Max Distance (km)"
                        value={filters.maxDistance}
                        onChange={handleChange}
                        className="border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"/>
                </div>

                <button
                    onClick={handleSearch}
                    className="mt-6 bg-green-600 text-white px-6 py-3 rounded-md font-semibold
                                hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500">
                    Search Bundles </button>
                </div>

                <div className="bg-white shadow-md rounded-lg p-6">
                    <p className="text-gray-600">No bundles yet</p>
                    <p className="text-gray-500 text-sm mt-2">RESULTS WILL BE DISPLAYED HERE AFTER BACKEND CONNECTION</p>
            </div>
        </div>
    );
}
