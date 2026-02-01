/**
 * User.jsx
 * @author Thomas Noakes
 */

import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

// Components
import Card from "../components/Card";
import Tooltip from "../components/Tooltip";
import InfoLine from "../components/InfoLine";
import Divider from "../components/Divider";
import Listing from "../components/Listing";

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

    // State object: stores the user information
    const [user, setUser] = useState(null);
    const [listings, setListings] = useState(null);
    const [loading, setLoading] = useState(true);

    // Fetch user information
    useEffect(() => {
        // TODO: get user information properly
        async function fetchUser() {
            // const res = await fetch(`/api/user/&{username}`);
            // const data = await res.json();
            // setUser(data);

            // TODO: REMOVE
            setUser({
                username: username,
                bio: "Selling quality items with fast delivery and trusted service.",
                activeSince: "1st Jan, 2026",
                location: "Exeter, England",
                openingHours: "9am-5pm daily",
                role: "seller",
                categories: ["Fast Food", "Tacos", "Mexican", "Spicy"],
            });

            setLoading(false);
        }

        fetchUser();
    }, [username]);

    // Fetch user listings
    useEffect(() => {
        // TODO: get user listings properly
        async function fetchListings() {
            // const res = await fetch(`/api/listings?user=&{username}`);
            // const data = await res.json();
            // setListings(data);

            // TODO: remove
            setListings([
                {
                    title: "Item 1",
                    image: "",
                    info: [
                        { label: "Pickup", value: "13:00-15:00" },
                        { label: "", value: "3 left" },
                    ],
                },
                {
                    title: "Item 2",
                    image: "",
                    info: [
                        { label: "Pickup", value: "09:00-10:00" },
                        { label: "", value: "Collection only" },
                    ],
                },
                {
                    title: "Item 3",
                    image: "",
                    info: [{ label: "Pickup", value: "13:00-15:00" }],
                },
            ]);
        }

        fetchListings();
    }, [username]);

    if (loading) {
        return (
            <div className="max-w-4xl mx-auto p-6">
                <Card>Loading user...</Card>
            </div>
        );
    }

    if (!user) {
        return (
            // TODO: better error page
            <div className="max-w-4xl mx-auto p-6">
                <Card>User {username} not found!</Card>
            </div>
        );
    }

    const isSeller = user.role === "seller";

    const renderListings = (listings) =>
        listings.map((listing) => (
            <Listing
                key={listing.title}
                title={listing.title}
                info={listing.info}
            />
        ));

    return (
        <div className="max-w-4xl mx-auto p-6">
            {/* User info container */}
            <Card>
                <div className="text-center mb-6">
                    {/* Profile picture */}
                    <img
                        // TODO: get user profile properly
                        src={defaultProfile}
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
                            {user.categories.map((category) => (
                                <span
                                    key={category}
                                    className="px-3 py-1 rounded-full
                                               text-sm font-medium text-green-700
                                               bg-green-100 hover:bg-green-200
                                               transition"
                                >
                                    {category}
                                </span>
                            ))}
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
            </Card>

            {/* Listings container */}
            <Card>
                {/* Header */}
                <h2 className="text-2xl font-bold mb-4 text-green-700">
                    Listings
                </h2>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {renderListings(listings)}
                </div>
            </Card>

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
