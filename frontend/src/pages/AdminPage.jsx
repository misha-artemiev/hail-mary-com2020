/**
 * DeveloperProfile.jsx
 * @author Ed Brown
 */

import React, { useState } from "react";

// Hooks
import useAllergens from "../hooks/useAllergens";
import useAdminIssueReports from "../hooks/useAdminIssueReports";
import useAdminOpenReservations from "../hooks/useAdminOpenReservations";
import useAdminUsers from "../hooks/useAdminUsers";
import useCategories from "../hooks/useCategories";
import useSearchBundles from "../hooks/useSearchBundles";

// Components
import Card from "../components/Card";
import Category from "../components/Category";
import Listing from "../components/Listing";
import Tabs from "../components/Tabs";
import Button from "../components/forms/Button";
import DropdownSelect from "../components/forms/DropdownSelect";
import FormInput from "../components/forms/FormInput";
import RoleSelect from "../components/forms/RoleSelect";

function prettyLabel(value) {
    if (!value) {
        return "Unknown";
    }

    return String(value)
        .toLowerCase()
        .replaceAll("_", " ")
        .replace(/\b\w/g, (char) => char.toUpperCase());
}

function statusClasses(status) {
    switch (status) {
        case "open":
            return "bg-yellow-100 text-yellow-800";
        case "in_progress":
            return "bg-blue-100 text-blue-800";
        case "closed":
            return "bg-gray-200 text-gray-800";
        default:
            return "bg-green-100 text-green-800";
    }
}

export default function DeveloperProfile() {
    const [activeTab, setActiveTab] = useState("listings");
    const [filtersOpen, setFiltersOpen] = useState(false);
    const [reservationBundleFilter, setReservationBundleFilter] = useState("");
    const [reservationConsumerFilter, setReservationConsumerFilter] =
        useState("");
    const [reservationClaimCodeFilter, setReservationClaimCodeFilter] =
        useState("");
    const [issueSourceFilter, setIssueSourceFilter] = useState("all");
    const [issueStatusFilter, setIssueStatusFilter] = useState("all");
    const [issueSearch, setIssueSearch] = useState("");
    const [userUsernameFilter, setUserUsernameFilter] = useState("");
    const [userEmailFilter, setUserEmailFilter] = useState("");
    const [userRoleFilter, setUserRoleFilter] = useState("all");
    const [filters, setFilters] = useState({
        restaurant: "",
        category: "",
        allergens: [],
        maxPrice: "",
        maxDistance: "",
    });

    const tabs = [
        { id: "listings", label: "Listings" },
        { id: "reservations", label: "Reservations" },
        { id: "issues", label: "Issues" },
        { id: "users", label: "Users" },
    ];
    
    // Use hooks for data fetching (no direct API calls)
    const { listings, loading, search } = useSearchBundles();
    const {
        issueReports,
        loading: issuesLoading,
        error: issuesError,
    } = useAdminIssueReports();
    const {
        openReservations,
        loading: openReservationsLoading,
        error: openReservationsError,
    } = useAdminOpenReservations();
    const {
        consumers,
        sellers,
        loading: usersLoading,
        error: usersError,
    } = useAdminUsers();
    const { allergenOptions } = useAllergens();
    const { categoryOptions } = useCategories();

    const filteredOpenReservations = openReservations.filter((reservation) => {
        const bundleMatches = reservationBundleFilter.trim()
            ? String(reservation.bundle_name || "")
                  .toLowerCase()
                  .includes(reservationBundleFilter.trim().toLowerCase())
            : true;

        const consumerMatches = reservationConsumerFilter.trim()
            ? String(reservation.consumer_id || "").includes(
                  reservationConsumerFilter.trim(),
              )
            : true;

        const claimCodeMatches = reservationClaimCodeFilter.trim()
            ? String(reservation.claim_code || "")
                  .toLowerCase()
                  .includes(reservationClaimCodeFilter.trim().toLowerCase())
            : true;

        return bundleMatches && consumerMatches && claimCodeMatches;
    });

    const filteredIssueReports = issueReports.filter((report) => {
        const sourceMatches =
            issueSourceFilter === "all" || report.source_type === issueSourceFilter;
        const statusMatches =
            issueStatusFilter === "all" || report.status === issueStatusFilter;

        if (!issueSearch.trim()) {
            return sourceMatches && statusMatches;
        }

        const searchValue = issueSearch.trim().toLowerCase();
        const haystack = [
            String(report.report_id),
            String(report.reservation_id || ""),
            String(report.user_id || ""),
            String(report.issue_type || ""),
            String(report.source_type || ""),
            String(report.status || ""),
            String(report.description || ""),
        ]
            .join(" ")
            .toLowerCase();

        return sourceMatches && statusMatches && haystack.includes(searchValue);
    });

    const allUsers = [
        ...consumers.map((consumer) => ({
            ...consumer,
            role: "consumer",
            display_name: `${consumer.fname} ${consumer.lname}`.trim(),
            verification_status: null,
        })),
        ...sellers.map((seller) => ({
            ...seller,
            role: "seller",
            display_name: seller.seller_name,
            verification_status: seller.verified_by ? "verified" : "unverified",
        })),
    ].sort((a, b) => {
        const first = new Date(a.created_at).getTime();
        const second = new Date(b.created_at).getTime();
        return second - first;
    });

    const filteredUsers = allUsers.filter((user) => {
        const usernameMatches = userUsernameFilter.trim()
            ? String(user.username || "")
                  .toLowerCase()
                  .includes(userUsernameFilter.trim().toLowerCase())
            : true;

        const emailMatches = userEmailFilter.trim()
            ? String(user.email || "")
                  .toLowerCase()
                  .includes(userEmailFilter.trim().toLowerCase())
            : true;

        const roleMatches =
            userRoleFilter === "all" || user.role === userRoleFilter;

        return usernameMatches && emailMatches && roleMatches;
    });

    const issueSourceOptions = [
        { value: "all", label: "All sources" },
        { value: "admin", label: "Admin" },
        { value: "seller", label: "Seller" },
    ];

    const issueStatusOptions = [
        { value: "all", label: "All statuses" },
        { value: "open", label: "Open" },
        { value: "in_progress", label: "In Progress" },
        { value: "closed", label: "Closed" },
    ];

    const userRoleOptions = [
        { value: "all", label: "All roles" },
        { value: "consumer", label: "Consumer" },
        { value: "seller", label: "Seller" },
    ];

    /**
     * Handles changes to text and number filters.
     */
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFilters((prev) => ({ ...prev, [name]: value }));
    };

    /**
     * Handles toggling a category on/off.
     */
    const handleCategoryClick = (category) => {
        setFilters((prev) => ({
            ...prev,
            category: prev.category === category ? "" : category,
        }));
    };

    /**
     * Handles allergen multi-select changes.
     */
    const handleAllergensChange = (nextAllergens) => {
        setFilters((prev) => ({
            ...prev,
            allergens: nextAllergens,
        }));
    };

    /**
     * Run filtered bundle search, matching homepage behavior.
     */
    const handleSearch = () => {
        search(filters);
    };

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
            case "users":
                return renderUsersTab();
            default:
                return null;
        }
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
                Open Reservations
            </h2>
            <p className="text-gray-600 mb-4">
                All currently open reservations across the platform.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                <FormInput
                    placeholder="Filter by bundle name"
                    name="reservationBundleFilter"
                    type="text"
                    value={reservationBundleFilter}
                    onChange={(e) => setReservationBundleFilter(e.target.value)}
                />
                <FormInput
                    placeholder="Filter by consumer ID"
                    name="reservationConsumerFilter"
                    type="text"
                    value={reservationConsumerFilter}
                    onChange={(e) => setReservationConsumerFilter(e.target.value)}
                />
                <FormInput
                    placeholder="Filter by claim code"
                    name="reservationClaimCodeFilter"
                    type="text"
                    value={reservationClaimCodeFilter}
                    onChange={(e) =>
                        setReservationClaimCodeFilter(e.target.value)
                    }
                />
            </div>

            {openReservationsLoading && (
                <p className="text-gray-600">Loading open reservations...</p>
            )}

            {!openReservationsLoading && openReservationsError && (
                <div className="text-center font-semibold bg-red-100 text-red-800 p-3 mb-4 rounded">
                    {openReservationsError}
                </div>
            )}

            {!openReservationsLoading &&
                !openReservationsError &&
                filteredOpenReservations.length === 0 && (
                    <p className="text-gray-600">No open reservations found.</p>
                )}

            {!openReservationsLoading &&
                !openReservationsError &&
                filteredOpenReservations.length > 0 && (
                <div className="space-y-4">
                    {filteredOpenReservations.map((reservation) => (
                        <div
                            key={reservation.reservation_id}
                            className="p-4 rounded-lg border border-gray-200 bg-gray-50"
                        >
                            <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                                <h3 className="text-lg font-semibold text-gray-800">
                                    {reservation.bundle_name}
                                </h3>
                                <span className="text-xs font-semibold px-2 py-1 rounded bg-yellow-100 text-yellow-800">
                                    Open
                                </span>
                            </div>
                            <p className="text-sm text-gray-700">
                                Reservation ID: {reservation.reservation_id}
                            </p>
                            <p className="text-sm text-gray-700">
                                Bundle ID: {reservation.bundle_id}
                            </p>
                            <p className="text-sm text-gray-700">
                                Consumer ID: {reservation.consumer_id}
                            </p>
                            <p className="text-sm text-gray-700">
                                Claim Code: {reservation.claim_code}
                            </p>
                            <p className="text-sm text-gray-700">
                                Reserved At:{" "}
                                {new Date(reservation.reserved_at).toLocaleString()}
                            </p>
                            {reservation.window_end && (
                                <p className="text-sm text-gray-700">
                                    Pickup Window Ends:{" "}
                                    {new Date(
                                        reservation.window_end,
                                    ).toLocaleString()}
                                </p>
                            )}
                        </div>
                    ))}
                </div>
            )}
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

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                <RoleSelect
                    label="Source"
                    value={issueSourceFilter}
                    onChange={(e) => setIssueSourceFilter(e.target.value)}
                    options={issueSourceOptions}
                />
                <RoleSelect
                    label="Status"
                    value={issueStatusFilter}
                    onChange={(e) => setIssueStatusFilter(e.target.value)}
                    options={issueStatusOptions}
                />
                <FormInput
                    label="Search"
                    placeholder="Search issues"
                    name="issueSearch"
                    type="text"
                    value={issueSearch}
                    onChange={(e) => setIssueSearch(e.target.value)}
                />
            </div>

            {issuesLoading && (
                <p className="text-gray-600">Loading issue reports...</p>
            )}

            {!issuesLoading && issuesError && (
                <div className="text-center font-semibold bg-red-100 text-red-800 p-3 mb-4 rounded">
                    {issuesError}
                </div>
            )}

            {!issuesLoading && !issuesError && filteredIssueReports.length === 0 && (
                <p className="text-gray-600">No issue reports found.</p>
            )}

            {!issuesLoading && !issuesError && filteredIssueReports.length > 0 && (
                <div className="space-y-3">
                    {filteredIssueReports.map((report) => (
                        <div
                            key={`${report.source_type}-${report.report_id}`}
                            className="border border-gray-200 rounded-lg p-4 bg-white"
                        >
                            <div className="flex flex-wrap items-center gap-2 mb-2">
                                <span className="font-semibold text-gray-800">
                                    Report #{report.report_id}
                                </span>
                                <span
                                    className={`text-xs font-semibold px-2 py-1 rounded ${statusClasses(
                                        report.status,
                                    )}`}
                                >
                                    {prettyLabel(report.status)}
                                </span>
                            </div>

                            <p className="text-sm text-gray-700 mb-1">
                                <span className="font-semibold">Source:</span>{" "}
                                {prettyLabel(report.source_type)}
                            </p>
                            <p className="text-sm text-gray-700 mb-1">
                                <span className="font-semibold">Issue Type:</span>{" "}
                                {prettyLabel(report.issue_type)}
                            </p>
                            {report.reservation_id && (
                                <p className="text-sm text-gray-700 mb-1">
                                    <span className="font-semibold">
                                        Reservation:
                                    </span>{" "}
                                    {report.reservation_id}
                                </p>
                            )}
                            {report.user_id && (
                                <p className="text-sm text-gray-700 mb-1">
                                    <span className="font-semibold">User ID:</span>{" "}
                                    {report.user_id}
                                </p>
                            )}
                            <p className="text-sm text-gray-700 mb-2">
                                <span className="font-semibold">Reported:</span>{" "}
                                {new Date(report.created_at).toLocaleString()}
                            </p>

                            <p className="text-sm text-gray-800 whitespace-pre-line">
                                {report.description}
                            </p>
                        </div>
                    ))}
                </div>
            )}
        </Card>
    );

    /**
     * Render users dashboard tab.
     */
    const renderUsersTab = () => (
        <Card>
            <h2 className="text-2xl font-bold text-green-700 mb-4">Users</h2>
            <p className="text-gray-600 mb-4">
                All registered consumers and sellers on the platform.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                <FormInput
                    label="Username"
                    placeholder="Search username"
                    name="userUsernameFilter"
                    type="text"
                    value={userUsernameFilter}
                    onChange={(e) => setUserUsernameFilter(e.target.value)}
                />
                <FormInput
                    label="Email"
                    placeholder="Search email"
                    name="userEmailFilter"
                    type="text"
                    value={userEmailFilter}
                    onChange={(e) => setUserEmailFilter(e.target.value)}
                />
                <RoleSelect
                    label="Role"
                    value={userRoleFilter}
                    onChange={(e) => setUserRoleFilter(e.target.value)}
                    options={userRoleOptions}
                />
            </div>

            {usersLoading && <p className="text-gray-600">Loading users...</p>}

            {!usersLoading && usersError && (
                <div className="text-center font-semibold bg-red-100 text-red-800 p-3 mb-4 rounded">
                    {usersError}
                </div>
            )}

            {!usersLoading && !usersError && filteredUsers.length === 0 && (
                <p className="text-gray-600">No users found.</p>
            )}

            {!usersLoading && !usersError && filteredUsers.length > 0 && (
                <div className="space-y-3">
                    {filteredUsers.map((user) => (
                        <div
                            key={`${user.role}-${user.user_id}`}
                            className="border border-gray-200 rounded-lg p-4 bg-white"
                        >
                            <div className="flex flex-wrap items-center gap-2 mb-2">
                                <span className="font-semibold text-gray-800">
                                    {user.display_name || user.username}
                                </span>
                                <span className="text-xs font-semibold px-2 py-1 rounded bg-gray-100 text-gray-700">
                                    {prettyLabel(user.role)}
                                </span>
                                {user.role === "seller" && (
                                    <span
                                        className={`text-xs font-semibold px-2 py-1 rounded ${
                                            user.verification_status === "verified"
                                                ? "bg-green-100 text-green-800"
                                                : "bg-yellow-100 text-yellow-800"
                                        }`}
                                    >
                                        {prettyLabel(user.verification_status)}
                                    </span>
                                )}
                            </div>

                            <p className="text-sm text-gray-700 mb-1">
                                <span className="font-semibold">User ID:</span>{" "}
                                {user.user_id}
                            </p>
                            <p className="text-sm text-gray-700 mb-1">
                                <span className="font-semibold">Username:</span>{" "}
                                {user.username}
                            </p>
                            <p className="text-sm text-gray-700 mb-1">
                                <span className="font-semibold">Email:</span>{" "}
                                {user.email}
                            </p>
                            <p className="text-sm text-gray-700 mb-1">
                                <span className="font-semibold">Created:</span>{" "}
                                {new Date(user.created_at).toLocaleString()}
                            </p>
                            <p className="text-sm text-gray-700">
                                <span className="font-semibold">Last Login:</span>{" "}
                                {new Date(user.last_login).toLocaleString()}
                            </p>
                        </div>
                    ))}
                </div>
            )}
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

            {activeTab === "listings" && (
                <Card>
                    <button
                        className="w-full flex items-center justify-between text-left"
                        onClick={() => setFiltersOpen(!filtersOpen)}
                    >
                        <h2 className="text-xl font-semibold text-gray-700">
                            Filters
                        </h2>
                        <svg
                            className={`w-5 h-5 text-gray-500
                                    transition-transform duration-250 ${
                                        filtersOpen ? "rotate-180" : ""
                                    }`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M19 9l-7 7-7-7"
                            />
                        </svg>
                    </button>

                    <div
                        className={`overflow-hidden transition-all duration-250 ${
                            filtersOpen
                                ? "max-h-125 opacity-100 mt-4"
                                : "max-h-0 opacity-0"
                        }`}
                    >
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <FormInput
                                placeholder="Restaurant Name"
                                name="restaurant"
                                type="text"
                                value={filters.restaurant}
                                onChange={handleChange}
                            />

                            <FormInput
                                placeholder="Max Price (£)"
                                name="maxPrice"
                                type="number"
                                min="0"
                                step="0.5"
                                value={filters.maxPrice}
                                onChange={handleChange}
                            />

                            <FormInput
                                placeholder="Max Distance (km)"
                                name="maxDistance"
                                type="number"
                                min="0"
                                step="1"
                                value={filters.maxDistance}
                                onChange={handleChange}
                            />

                            <DropdownSelect
                                value={filters.allergens}
                                name="allergen"
                                onChange={handleAllergensChange}
                                options={allergenOptions}
                            />
                        </div>

                        <div className="mt-4 flex flex-wrap gap-2">
                            {renderCategories(categoryOptions)}
                        </div>

                        <Button
                            onClick={handleSearch}
                            className="w-full md:w-auto mt-4"
                        >
                            Search Bundles
                        </Button>
                    </div>
                </Card>
            )}

            {/* Tab Content */}
            {renderTabContent()}
        </div>
    );
}