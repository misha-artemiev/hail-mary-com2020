/**
 * DeveloperProfile.jsx
 * @author Ed Brown
 */

import React, { useState } from "react";

// Hooks
import useSearchBundles from "../hooks/useSearchBundles";

// Components
import Card from "../components/Card";
import Listing from "../components/Listing";
import Tabs from "../components/Tabs";

export default function DeveloperProfile() {
    const [activeTab, setActiveTab] = useState("listings");
    const tabs = [
        { id: "listings", label: "Listings" },
        { id: "reservations", label: "Reservations" },
        { id: "issues", label: "Issues" },
    ];
    
    // Use hooks for data fetching (no direct API calls)
    const { listings, loading } = useSearchBundles();

    /**
     * Render active tab content.
     */
    const renderTabContent = () => {
        switch (activeTab) {
            case "listings":
                return renderListingsTab();
            case "reservations":
                return renderReservationsTab();
            case "issues":
                return renderIssuesTab();
            default:
                return null;
        }
    };

    /**
     * Render listings management tab.
     */
    const renderListingsTab = () => (
        <Card>
            <h2 className="text-2xl font-bold text-green-700 mb-4">
                All Listings
            </h2>

            {loading && <p className="text-gray-600">Loading listings...</p>}

            {!loading && (!listings || listings.length === 0) && (
                <p className="text-gray-600">No listings found.</p>
            )}

            {!loading && listings && listings.length > 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {renderListings(listings)}
                </div>
            )}
        </Card>
    );

    /**
     * Dynamically render listings using the Listing component.
     *
     * @param {Array} listings - The listings to display.
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
                    footer={
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
                    }
                    onClick={() => handleListingClick(listing.bundle_id)}
                />
            );
        });

    /**
     * Handle clicking on a listing.
     */
    const handleListingClick = (listingId) => {
        console.log("Clicked listing:", listingId);
        // TODO: Navigate to listing detail page or show modal
    };

    /**
     * Render reservations management tab.
     */
    const renderReservationsTab = () => (
        <Card>
            <h2 className="text-2xl font-bold text-green-700 mb-4">
                Manage Reservations
            </h2>
            <p className="text-gray-600">
                Reservations will be available once the
                hooks created.
            </p>
            <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">
                    Pending Implementation:
                </h3>
                <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                    <li>Create useReservations hook</li>
                    <li>Fetch all reservations from backend</li>
                    <li>Display reservation details with status</li>
                    <li>Add cancel reservation functionality</li>
                </ul>
            </div>
        </Card>
    );

    /**
     * Render issues dashboard tab.
     */
    const renderIssuesTab = () => (
        <Card>
            <h2 className="text-2xl font-bold text-green-700 mb-4">
                Reported Issues
            </h2>
            <p className="text-gray-600">
                Issue reporting will be available once
                appropriate hooks are created.
            </p>
            <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">
                    Pending Implementation:
                </h3>
                <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                    <li>Create useIssues hook</li>
                    <li>Fetch all reported issues from backend</li>
                    <li>Display issue details with status badges</li>
                    <li>Add issue filtering and sorting</li>
                    <li>Add issue status update functionality</li>
                </ul>
            </div>
        </Card>
    );

    return (
        <div className="max-w-6xl mx-auto p-6">
            {/* Header */}
            <Card>
                <h1 className="text-3xl font-bold text-green-700 mb-2">
                    Admin Dashboard
                </h1>
                <p className="text-gray-600">
                    Manage listings, reservations, and view reported issues.
                </p>
            </Card>

            {/* Tab Navigation */}
            <Card>
                <Tabs
                    tabs={tabs}
                    activeTab={activeTab}
                    onTabChange={setActiveTab}
                />
            </Card>

            {/* Tab Content */}
            {renderTabContent()}
        </div>
    );
}