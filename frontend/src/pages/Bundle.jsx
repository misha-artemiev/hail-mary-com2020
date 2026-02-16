/**
 * Bundle.jsx
 * Page displaying information about a specific bundle
 */

import React from "react";
import { useParams } from "react-router-dom";

// Hooks
import useBundle from "../hooks/useBundle";

// Components
import Card from "../components/Card";
import InfoLine from "../components/InfoLine";

// Resources
import defaultListing from "../assets/default-listing.jpg";

/**
 * The bundle page.
 * The requested bundle is taken from the URL (*i.e.* `/bundles/<bundle_id`)
 * If logged in:
 *  - Consumers can reserve bundles
 *  - Sellers can view reservations
 *
 * @returns the specific bundle page.
 */
export default function Bundle() {
    const { id } = useParams();

    const { bundle, loading, error } = useBundle(id);

    if (loading) {
        return (
            <div className="max-w-4xl mx-auto p-6">
                <Card>Loading bundle...</Card>
            </div>
        );
    }

    // Display any error when finding the bundle
    if (error) {
        return (
            // TODO: better error page
            <div className="max-w-4xl mx-auto p-6">
                <Card>Bundle not found!</Card>
            </div>
        );
    }

    // Display an error if the bundle doesn't exist/can't be found
    if (!bundle) {
        return (
            // TODO: better error page
            <div className="max-w-4xl mx-auto p-6">
                <Card>Bundle not found!</Card>
            </div>
        );
    }

    // Calculate discount percentage
    const originalPrice = Number(bundle.price);
    const discountedPrice =
        originalPrice * (1 - bundle.discount_percentage / 100);

    //
    const windowStart = new Date(bundle.window_start);
    const windowEnd = new Date(bundle.window_end);

    /**
     * Convert a date object to a formatted string.
     *
     * @param {Date} date - The date to format.
     *
     * @returns the formatted date string.
     */
    const formatDateTime = (date) => {
        return date.toLocaleString("en-GB", {
            weekday: "short",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    return (
        <div className="max-w-4xl mx-auto p-6">
            <Card className="overflow-hidden">
                <div className="flex flex-col md:flex-row gap-6">
                    {/* Image */}
                    <div className="relative w-full h-64 md:h-80">
                        <img
                            src={defaultListing} // TODO: fetch image
                            alt={bundle.bundle_name}
                            className="w-full h-full object-cover"
                        />
                    </div>
                </div>

                <div className="p-6 text-center">
                    {/* Title */}
                    <h1 className="text-2xl md:text-4xl font-bold text-green-700">
                        {bundle.bundle_name}
                    </h1>

                    {/* Description */}
                    <p className="mt-3 text-gray-600 max-w-xl mx-auto">
                        {bundle.description}
                    </p>

                    {/* Information */}
                    <div className="mt-5 flex items-center justify-center gap-3 flex-wrap">
                        {/* Original price */}
                        <span className="text-gray-400 line-through text-lg">
                            £{originalPrice.toFixed(2)}
                        </span>

                        {/* New price */}
                        <span className="text-3xl font-bold text-green-600">
                            £{discountedPrice.toFixed(2)}
                        </span>

                        {/* Discount tag */}
                        <span className="bg-red-500 text-white text-sm px-3 py-1 rounded-full hover:">
                            {bundle.discount_percentage}% OFF
                        </span>
                    </div>
                </div>
            </Card>

            <Card>
                {/* Subtitle */}
                <h2 className="text-xl font-bold text-green-700 mb-4">
                    Pickup Details
                </h2>

                {/* TODO: get seller information */}
                <InfoLine label="Restaurant" value="" />

                <InfoLine
                    label="Pickup Window"
                    value={`${formatDateTime(windowStart)} - ${formatDateTime(windowEnd)}`}
                />
            </Card>
        </div>
    );
}
