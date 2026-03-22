/**
 * User.jsx
 * @author Thomas Noakes
 */

import React from "react";
import { useParams } from "react-router-dom";

// Hooks
import { useUser } from "../hooks/useUser";
import { useUserListings } from "../hooks/useUserListings";
import { useUserProfileImage } from "../hooks/useUserProfileImage";

// Components
import Card from "../components/Card";
import Tooltip from "../components/Tooltip";
import InfoLine from "../components/InfoLine";
import Divider from "../components/Divider";
import Listing from "../components/Listing";
import Category from "../components/Category";

// Resources
import defaultProfile from "../assets/default-user.jpg";

/**
 * The user page of the site.
 * The requested user is taken from the URL (*i.e* `/user/<username>`)
 * The displayed information varies if role is seller or consumer.
 *
 * @returns the specific user page.
 */
export default function User() {
    // Get the selected user from the URL
    const { username } = useParams();

    // Use custom hooks
    const { user, loading } = useUser(username);
    const listings = useUserListings(username);
    const { imageUrl: profileImage, loading: imageLoading } = useUserProfileImage(username);

    // Display a temporary loading indicator
    if (loading || imageLoading) {
        return (
            <div className="max-w-4xl mx-auto p-4 md:p-6">
                <Card>Loading user...</Card>
            </div>
        );
    }

    // Display an error if the user can't be found
    if (!user) {
        return (
            // TODO: better error page
            <div className="max-w-4xl mx-auto p-4 md:p-6">
                <Card>User {username} not found!</Card>
            </div>
        );
    }

    const isSeller = user.role === "seller";

    /**
     * Dynamically renders given listings.
     *
     * @param {Object} listings - The listings to display.
     * @returns {JSX.Element} a set of Listing elements
     */
    const renderListings = (listings) =>
        listings.map((listing) => (
            <Listing
                key={listing.title}
                title={listing.title}
                info={listing.info}
            />
        ));

    /**
     * Dynamically renders given categories.
     *
     * @param {Object} categories - The categories to display.
     * @returns {JSX.Element} a set of Category elements
     */
    const renderCategories = (categories) =>
        categories.map((category) => (
            <Category key={category}>{category}</Category>
        ));

    return (
        <div className="max-w-4xl mx-auto p-4 md:p-6">
            {/* User info container */}
            <Card>
                <div className="text-center mb-6">
                    {/* Profile picture */}
                    <img
                        src={profileImage || defaultProfile}
                        alt="Profile"
                        className="w-48 h-48 rounded-full mb-4 mx-auto"
                    />

                    {/* Header */}
                    <h1 className="flex items-center justify-center gap-2 mt-4 text-4xl font-bold text-green-700">
                        {username}
                        {isSeller && (
                            <Tooltip text="Verified Seller">
                                <span className="text-2xl">🏪</span>
                            </Tooltip>
                        )}
                    </h1>

                    {/* Bio */}
                    {user.bio !== "" && (
                        <p className="mt-4 text-gray-700">{user.bio}</p>
                    )}

                    {/* Categories */}
                    {isSeller && user.categories.length > 0 && (
                        <div className="mt-4 flex flex-wrap justify-center gap-2">
                            {renderCategories(user.categories)}
                        </div>
                    )}
                </div>

                {/* Seller-specific */}
                {isSeller && (
                    <>
                        <Divider>About us</Divider>

                        {/* User info */}
                        <InfoLine
                            label="Active since"
                            value={user.activeSince}
                        />
                        <InfoLine label="Located in" value={user.location} />
                        <InfoLine
                            label="Opening hours"
                            value={user.openingHours}
                        />
                    </>
                )}

                {!isSeller && (
                    <>
                        {/* User info */}
                        <InfoLine
                            label="Active since"
                            value={user.activeSince}
                        />
                        <InfoLine label="Rescue streak" value={user.streak} />

                        {/* Personal impact summary */}
                        <h2 className="mt-4 text-xl font-bold text-green-700">
                            Impact
                        </h2>
                        <InfoLine label="Meals saved" value={user.mealsSaved} />
                        <InfoLine label="CO2e prevented" value={user.co2e} />
                    </>
                )}
            </Card>

            {/* Listings container */}
            {isSeller && (
                <Card>
                    {/* Header */}
                    <h2 className="text-2xl font-bold mb-4 text-green-700">
                        Listings
                    </h2>

                    {/* Active listings */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {renderListings(listings)}
                    </div>
                </Card>
            )}

            {/* Reservations container */}
            {!isSeller && (
                <Card>
                    {/* Header */}
                    <h2 className="text-2xl font-bold mb-4 text-green-700">
                        Reservations
                    </h2>

                    {/* Active reservations */}
                    {/* TODO: get active reservations */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {renderListings(listings)}
                    </div>
                </Card>
            )}

            {/* Badges container */}
            <Card>
                {/* Header */}
                <h2 className="text-2xl font-bold mb-4 text-green-700">
                    Badges
                </h2>

                {/* TODO: get badges properly */}
                <p>No badges yet...!</p>
            </Card>
        </div>
    );
}
