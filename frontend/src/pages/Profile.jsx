/**
 * Profile.jsx
 * @author Thomas Noakes
 */

import React from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

// Components
import Card from "../components/Card";
import InfoLine from "../components/InfoLine";

// Hooks
import useConsumerProfile from "../hooks/useConsumerProfile";
import { useUserImage } from "../hooks/useUserImage";

// Resources
import defaultProfile from "../assets/default-user.jpg";

export default function Profile() {
    const { logout } = useAuth();
    const navigate = useNavigate();
    const { profile, loading, error } = useConsumerProfile();
    const { imageUrl } = useUserImage();

    const handleLogout = () => {
        logout();
        navigate("/");
    };

    const handleEdit = () => {
        navigate("/editprofile");
    };

    if (loading) {
        return (
            <div className="max-w-3xl mx-auto p-4 md:p-6">
                <Card>
                    <p className="text-gray-500 text-center py-4">
                        Loading profile...
                    </p>
                </Card>
            </div>
        );
    }

    if (error || !profile) {
        return (
            <div className="max-w-3xl mx-auto p-4 md:p-6">
                <Card>
                    <p className="text-red-500 text-center py-4">
                        {error ?? "Profile not found"}
                    </p>
                </Card>
            </div>
        );
    }

    const displayName =
        profile.fname && profile.lname
            ? `${profile.fname} ${profile.lname} (${profile.username})`
            : profile.username || "User";

    return (
        <div className="max-w-3xl mx-auto p-4 md:p-6">
            {/* Profile container */}
            <Card>
                <div className="flex items-center justify-between mb-6">
                    {/* Header */}
                    <h1 className="text-3xl font-bold text-green-700">
                        Profile
                    </h1>

                    <div className="flex gap-2">
                        {/* Logout button */}
                        <button
                            onClick={handleLogout}
                            className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-400"
                        >
                            Log out
                        </button>

                        {/* Edit profile button */}
                        <button
                            onClick={handleEdit}
                            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                        >
                            Edit Profile
                        </button>
                    </div>
                </div>

                {/* Profile picture */}
                <img
                    src={imageUrl || defaultProfile}
                    alt="Profile"
                    className="w-32 h-32 rounded-full mb-4 mx-auto object-cover border-2 border-green-600"
                    onError={(e) => {
                        e.target.src = defaultProfile;
                    }}
                />

                {/* User info */}
                <InfoLine label="Display name" value={displayName} />
                <InfoLine label="Email" value={profile.email} />
                <InfoLine label="Current rescue streak" value="0 weeks" />
                <InfoLine label="Bundles rescued" value="0" />
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
