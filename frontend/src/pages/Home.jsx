/**
 * Home.jsx
 * @author Ed Brown
 */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

// Hooks
import useAllergens from "../hooks/useAllergens";
import useCategories from "../hooks/useCategories";
import useSearchBundles from "../hooks/useSearchBundles";

// Components
import Card from "../components/Card";
import FormInput from "../components/forms/FormInput";
import Button from "../components/forms/Button";
import Category from "../components/Category";
import DropdownSelect from "../components/forms/DropdownSelect";
import Listing from "../components/Listing";

/**
 * The main home page of the site, a feed of available bundles.
 *
 * @returns {JSX.Element} the home page
 */
export default function Home() {
    const navigate = useNavigate();

    // State object: holds all fields for the form
    const [filters, setFilters] = useState({
        restaurant: "",
        category: "",
        allergens: [],
        maxPrice: "",
        maxDistance: "",
    });

    // Use custom hooks
    const { listings, loading, search } = useSearchBundles();
    const { allergenOptions } = useAllergens();
    const { categoryOptions } = useCategories();

    /**
     * Handles changes to the filters.
     */
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFilters((prev) => ({ ...prev, [name]: value }));
    };

    /**
     * Handles toggling a category on/off.
     *
     * @param {string} category - The category to toggle.
     */
    const handleCategoryClick = (category) => {
        console.log(filters);
        setFilters((prev) => ({
            ...prev,
            category: prev.category === category ? "" : category, // Can toggle on/off
        }));
    };

    /**
     * Handles adding new allergens to the filter list.
     *
     * @param {Array<string>} nextAllergens - The selected allergens.
     */
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
        search(filters);
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

    /**
     * Dynamically renders given listings.
     *
     * @param {Object} listings - The listings to display.
     * @returns {JSX.Element} a set of Listing elements
     */
    const renderListings = (listings) =>
        listings.map((listing) => {
            const originalPrice = listing.price;
            const discountedPrice =
                originalPrice * (1 - listing.discount_percentage / 100);
            const windowStart = new Date(listing.window_start);
            const windowEnd = new Date(listing.window_end);
            const startDateTime = windowStart.toLocaleString("en-GB", {
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
            });
            const endDateTime = windowEnd.toLocaleString("en-GB", {
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
            });

            return (
                <Listing
                    key={listing.bundle_id}
                    title={listing.bundle_name}
                    info={[
                        {
                            label: "Description",
                            value: listing.bundle_description,
                        },
                        { label: "Restaurant", value: listing.sellers_name },
                        {
                            label: "Pickup Window",
                            value: `${startDateTime} - ${endDateTime}`,
                        },
                    ]}
                    onClick={() => navigate(`/bundles/${listing.bundle_id}`)}
                >
                    <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-gray-500 line-through">
                            £{originalPrice.toFixed(2)}
                        </span>
                        <span className="text-lg font-bold text-green-600">
                            £{discountedPrice.toFixed(2)}
                        </span>
                        <span className="bg-red-500 text-white text-xs px-2 py-1 rounded">
                            {listing.discount_percentage}% OFF
                        </span>
                        <span className="text-gray-600 text-m ml-auto">
                            {listing.dist.toFixed(1)} km
                        </span>
                    </div>
                </Listing>
            );
        });

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

                    {/* Max price filter */}
                    <FormInput
                        placeholder="Max Price (£)"
                        name="maxPrice"
                        type="number"
                        min="0"
                        step="0.5"
                        value={filters.maxPrice}
                        onChange={handleChange}
                    />

                    {/* Max distance filter */}
                    <FormInput
                        placeholder="Max Distance (km)"
                        name="maxDistance"
                        type="number"
                        min="0"
                        step="1"
                        value={filters.maxDistance}
                        onChange={handleChange}
                    />

                    {/* Allergen filter */}
                    <DropdownSelect
                        value={filters.allergens}
                        name="allergen"
                        onChange={handleAllergensChange}
                        options={allergenOptions}
                    />
                </div>

                {/* Categories div */}
                <div className="mt-4 flex flex-wrap gap-2">
                    {renderCategories(categoryOptions)}
                </div>

                <Button onClick={handleSearch} className="w-md mt-4">
                    Search Bundles
                </Button>
            </Card>

            <Card>
                {/* Display a temporary loading indicator */}
                {loading && (
                    <p className="text-gray-600">Loading listings...</p>
                )}

                {/* Display if there are no listings */}
                {!listings ||
                    (listings.length === 0 && (
                        <p className="text-gray-600">No listings yet!</p>
                    ))}

                {listings && (
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        {renderListings(listings)}
                    </div>
                )}
            </Card>
        </div>
    );
}
