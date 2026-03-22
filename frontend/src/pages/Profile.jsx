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
import useBadges from "../hooks/useBadges";

// Resources
import defaultProfile from "../assets/default-user.jpg";

const BADGE_IMAGES = import.meta.glob("../assets/badges/*_*.jpeg", {
    eager: true,
    import: "default",
});

const getBadgeImage = (badgeId, level = 1) => {
    const key = Object.keys(BADGE_IMAGES).find((path) =>
        path.includes(`_${badgeId}.${level}.jpeg`),
    );
    return key ? BADGE_IMAGES[key] : null;
};

export default function Profile() {
    const { logout } = useAuth();
    const navigate = useNavigate();
    const {
        profile,
        loading: profileLoading,
        error: profileError,
    } = useConsumerProfile();
    const { imageUrl } = useUserImage();
    const {
        badges,
        loading: badgesLoading,
        error: badgesError,
        getConsumerBadgeLevel,
    } = useBadges();

    const handleLogout = () => {
        logout();
        navigate("/");
    };

    const handleEdit = () => {
        navigate("/editprofile");
    };

    if (profileLoading || badgesLoading) {
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

    if (profileError || !profile) {
        return (
            <div className="max-w-3xl mx-auto p-4 md:p-6">
                <Card>
                    <p className="text-red-500 text-center py-4">
                        {profileError ?? "Profile not found"}
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

                {badgesError && (
                    <p className="text-red-500 text-center py-4">
                        {badgesError}
                    </p>
                )}

                <div className="flex flex-wrap gap-4 justify-center">
                    {badges.map((badge) => {
                        const acquiredLevel = getConsumerBadgeLevel(
                            badge.badge_id,
                        );
                        const isAcquired = acquiredLevel > 0;
                        const badgeImage = getBadgeImage(
                            badge.badge_id,
                            isAcquired ? acquiredLevel : 1,
                        );
                        return (
                            <div
                                key={badge.badge_id}
                                className="flex flex-col items-center max-w-24 group relative"
                            >
                                {badgeImage ? (
                                    <img
                                        src={badgeImage}
                                        alt={badge.name}
                                        className={`w-16 h-16 object-contain ${isAcquired ? "" : "grayscale opacity-50"}`}
                                    />
                                ) : (
                                    <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center">
                                        <span className="text-gray-400 text-xs">
                                            {badge.name.charAt(0)}
                                        </span>
                                    </div>
                                )}
                                <span className="text-xs font-medium text-gray-700 mt-1 text-center">
                                    {badge.name}
                                </span>
                                {isAcquired && (
                                    <span className="text-xs text-green-600 font-medium">
                                        Lv.{acquiredLevel}
                                    </span>
                                )}
                                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-white text-gray-800 text-xs rounded-md border-2 border-green-600 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
                                    {badge.description}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </Card>
        </div>
    );
}
