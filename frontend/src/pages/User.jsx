/**
 * User.jsx
 * @author Thomas Noakes
 */

import React from "react";
import { useParams, useNavigate } from "react-router-dom";

import { useUser } from "../hooks/useUser";
import { useUserListings } from "../hooks/useUserListings";
import { useUserProfileImage } from "../hooks/useUserProfileImage";
import { useUserStreak } from "../hooks/useUserStreak";
import { useUserImpact } from "../hooks/useUserImpact";
import { useUserBadges } from "../hooks/useUserBadges";

import Card from "../components/Card";
import Tooltip from "../components/Tooltip";
import InfoLine from "../components/InfoLine";
import Divider from "../components/Divider";

import defaultProfile from "../assets/default-user.jpg";

const BADGE_IMAGES = import.meta.glob("../assets/badges/*_*.jpeg", {
    eager: true,
    import: "default",
});

const getBadgeImage = (badgeId, level = 1) => {
    const key = Object.keys(BADGE_IMAGES).find(
        (path) => path.includes(`_${badgeId}.${level}.jpeg`) || path.includes(`_${badgeId}.jpeg`),
    );
    return key ? BADGE_IMAGES[key] : null;
};

export default function User() {
    const { username } = useParams();
    const navigate = useNavigate();

    const { user, loading, error } = useUser(username);
    const { imageUrl: profileImage } = useUserProfileImage(username);
    const { listings, loading: listingsLoading } = useUserListings(
        username,
        user?.role,
        user?.user_id,
    );
    const { streak } = useUserStreak(user?.user_id);
    const { impact } = useUserImpact(user?.user_id);
    const { badges, loading: badgesLoading } = useUserBadges(user?.user_id);

    if (loading) {
        return (
            <div className="max-w-4xl mx-auto p-4 md:p-6">
                <Card>
                    <p className="text-gray-500 text-center py-4">
                        Loading user...
                    </p>
                </Card>
            </div>
        );
    }

    if (error || !user) {
        return (
            <div className="max-w-4xl mx-auto p-4 md:p-6">
                <Card>
                    <p className="text-red-500 text-center py-4">
                        {error ?? `User ${username} not found`}
                    </p>
                </Card>
            </div>
        );
    }

    const isSeller = user.role === "seller";

    const formatDate = (dateStr) => {
        if (!dateStr) return "N/A";
        const date = new Date(dateStr);
        return date.toLocaleDateString("en-GB", {
            day: "numeric",
            month: "short",
            year: "numeric",
        });
    };

    const formatLocation = () => {
        if (!isSeller) return null;
        const parts = [
            user.address_line1,
            user.address_line2,
            user.city,
            user.post_code,
            user.country,
        ].filter(Boolean);
        return parts.length > 0 ? parts.join(", ") : null;
    };

    const isVerified = isSeller && user.verified_by !== null;

    return (
        <div className="max-w-4xl mx-auto p-4 md:p-6">
            <Card>
                <div className="text-center mb-6">
                    <img
                        src={profileImage || defaultProfile}
                        alt="Profile"
                        className="w-48 h-48 rounded-full mb-4 mx-auto object-cover border-2 border-green-600"
                        onError={(e) => {
                            e.target.src = defaultProfile;
                        }}
                    />

                    <h1 className="flex items-center justify-center gap-2 mt-4 text-4xl font-bold text-green-700">
                        {isSeller
                            ? user.seller_name
                            : `${user.fname} ${user.lname}`}
                        {isVerified && (
                            <Tooltip text="Verified Seller">
                                <span className="text-2xl">🏪</span>
                            </Tooltip>
                        )}
                    </h1>

                    <p className="text-gray-500 mt-1">@{user.username}</p>
                </div>

                {isSeller && (
                    <>
                        <Divider>About us</Divider>

                        <InfoLine
                            label="Active since"
                            value={formatDate(user.created_at)}
                        />
                        {formatLocation() && (
                            <InfoLine
                                label="Located in"
                                value={formatLocation()}
                            />
                        )}
                    </>
                )}

                {!isSeller && (
                    <>
                        <InfoLine
                            label="Active since"
                            value={formatDate(user.created_at)}
                        />
                        {streak !== null && (
                            <InfoLine
                                label="Rescue streak"
                                value={`${streak} weeks`}
                            />
                        )}

                        <Divider>Impact</Divider>

                        <InfoLine
                            label="Meals saved"
                            value={impact?.meals_saved ?? 0}
                        />
                        <InfoLine
                            label="CO2e prevented"
                            value={`${((impact?.co2e_saved ?? 0) / 1000).toFixed(2)}kg`}
                        />
                    </>
                )}
            </Card>

            {isSeller && (
                <Card>
                    <h2 className="text-2xl font-bold mb-4 text-green-700">
                        Listings
                    </h2>

                    {listingsLoading ? (
                        <p className="text-gray-500">Loading listings...</p>
                    ) : listings && listings.length > 0 ? (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {listings.map((bundle) => {
                                const windowStart = new Date(
                                    bundle.window_start,
                                );
                                const windowEnd = new Date(bundle.window_end);
                                const pickupTime = `${windowStart.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })} - ${windowEnd.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })}`;

                                return (
                                    <div
                                        key={bundle.bundle_id}
                                        className="bg-white border rounded-xl shadow-sm hover:border-green-500 cursor-pointer transition p-4"
                                        onClick={() =>
                                            navigate(
                                                `/bundles/${bundle.bundle_id}`,
                                            )
                                        }
                                    >
                                        <h3 className="text-lg font-semibold">
                                            {bundle.bundle_name}
                                        </h3>
                                        <p className="text-sm text-gray-700 mt-1">
                                            Pickup: {pickupTime}
                                        </p>
                                        <p className="text-sm text-gray-500">
                                            {bundle.remaining_count ??
                                                bundle.total_qty}{" "}
                                            left
                                        </p>
                                    </div>
                                );
                            })}
                        </div>
                    ) : (
                        <p className="text-gray-500">No listings yet.</p>
                    )}
                </Card>
            )}

            {!isSeller && (
                <Card>
                    <h2 className="text-2xl font-bold mb-4 text-green-700">
                        Reservations
                    </h2>

                    {listingsLoading ? (
                        <p className="text-gray-500">Loading reservations...</p>
                    ) : listings && listings.length > 0 ? (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {listings.map((reservation) => {
                                const bundle = reservation.bundle ?? {};
                                return (
                                    <div
                                        key={reservation.reservation_id}
                                        className="bg-white border rounded-xl shadow-sm hover:border-green-500 cursor-pointer transition p-4"
                                        onClick={() =>
                                            navigate(
                                                `/bundles/${bundle.bundle_id ?? reservation.bundle_id}`,
                                            )
                                        }
                                    >
                                        <h3 className="text-lg font-semibold">
                                            {bundle.bundle_name ?? "Bundle"}
                                        </h3>
                                        <p className="text-sm text-gray-700 mt-1">
                                            Status:{" "}
                                            {reservation.status ?? "Unknown"}
                                        </p>
                                    </div>
                                );
                            })}
                        </div>
                    ) : (
                        <p className="text-gray-500">No reservations yet.</p>
                    )}
                </Card>
            )}

            {!isSeller && (
                <Card>
                    <h2 className="text-2xl font-bold mb-4 text-green-700">
                        Badges
                    </h2>

                    {badgesLoading ? (
                        <p className="text-gray-500">Loading badges...</p>
                    ) : (
                        <div className="flex flex-wrap gap-4 justify-center">
                            {badges.map((badge) => {
                                const isAcquired = badge.level > 0;
                                const badgeImage = getBadgeImage(
                                    badge.badge_id,
                                    isAcquired ? badge.level : 1,
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
                                                Lv.{badge.level}
                                            </span>
                                        )}
                                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-white text-gray-800 text-xs rounded-md border-2 border-green-600 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
                                            {badge.description}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </Card>
            )}

            {isSeller && (
                <Card>
                    <h2 className="text-2xl font-bold mb-4 text-green-700">
                        Badges
                    </h2>
                    <p className="text-gray-500">Sellers do not have badges.</p>
                </Card>
            )}
        </div>
    );
}
