/**
 * Profile.jsx
 * @author Thomas Noakes
 */

import React from "react";

// Components
import Card from "../components/Card";

// Resources
import defaultProfile from "../assets/default-user.jpg";

/**
 * Displays a labelled information field.
 *
 * @param {Object} props
 * @param {string} props.label - The label to describe the value
 * @param {string | number} props.label - The value to display
 *
 * @returns {JSX.Element} a paragraph element containing the label and value
 */
function Info({ label, value }) {
    return (
        <p className="text-gray-700 mb-2">
            <span className="font-semibold">{label}:</span> {value}
        </p>
    );
}

export default function Profile() {
    /**
     * Handles clicking the edit button.
     */
    const handleEdit = () => {
        // TODO: add edit profile
        alert("Clicked");
    };

    return (
        <div className="max-w-3xl mx-auto p-6">
            {/* Profile container */}
            <Card>
                <div className="flex items-center justify-between mb-6">
                    {/* Header */}
                    <h1 className="text-3xl font-bold text-green-700">
                        Profile
                    </h1>

                    {/* Edit profile button */}
                    <button
                        onClick={handleEdit}
                        className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                    >
                        Edit Profile
                    </button>
                </div>

                {/* Profile picture */}
                <img
                    // TODO: get user profile properly
                    src={defaultProfile}
                    alt="Profile"
                    className="w-32 h-32 rounded-full mb-4 mx-auto"
                />

                {/* User info */}
                <Info label="Display name" value="User0001" />
                <Info label="Current rescue streak" value="0 weeks" />
                <Info label="Bundles rescued" value="0" />
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
