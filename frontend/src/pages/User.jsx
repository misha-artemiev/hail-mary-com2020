/**
 * User.jsx
 * @author Thomas Noakes
 */

import React from "react";
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

    // TODO: get user role properly
    const seller = true;

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
                        {seller && (
                            <Tooltip text="Verified Seller">
                                <span className="text-2xl">🏪</span>
                            </Tooltip>
                        )}
                    </h1>

                    {/* Bio */}
                    <p className="mt-4 text-gray-700">
                        Selling quality items with fast delivery and trusted
                        service.
                    </p>
                </div>

                {/* Seller-specific */}
                {seller && (
                    <>
                        <Divider>About us</Divider>

                        {/* User info */}
                        <InfoLine label="Active since" value="1st Jan, 2026" />
                        <InfoLine label="Located in" value="Exeter, England" />
                        <InfoLine label="Opening hours" value="9am-5pm daily" />
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
                    {/* TODO: get user's listings properly */}
                    <Listing
                        title="Item 1"
                        info={[{ label: "Pickup", value: "13:00-15:00" }]}
                        footer={<span className="text-green-600">3 left</span>}
                    />
                    <Listing
                        title="Item 2"
                        info={[{ label: "Pickup", value: "09:00-10:00" }]}
                        footer={
                            <span className="text-red-600">
                                Collection only
                            </span>
                        }
                    />
                    <Listing
                        title="Item 3"
                        info={[{ label: "Pickup", value: "13:00-13:30" }]}
                    />
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
