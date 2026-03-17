/**
 * Leaderboard.jsx
 * @author Thomas Noakes
 */

import React, { useState } from "react";

// Components
import Card from "../components/Card";
import LeaderboardItem from "../components/LeaderboardItem";

// Hooks
import useLeaderboard from "../hooks/useLeaderboard";

/**
 * The leaderboard page of the site.
 * Displays top users by reservations or carbon dioxide saved.
 *
 * @returns {JSX.Element} the leaderboard page
 */
export default function Leaderboard() {
    // State objects: stores the leaderboard data
    const [leaderboardCategory, setLeaderboardCategory] =
        useState("reservations");
    const { leaderboardData, loading, error } =
        useLeaderboard(leaderboardCategory);

    return (
        <div className="max-w-2xl mx-auto p-4 md:p-6">
            <Card>
                <h1 className="text-3xl font-bold text-green-700 mb-6 text-center">
                    Leaderboard
                </h1>

                {/* Type selector */}
                <div className="flex justify-center gap-4 mb-6">
                    <button
                        type="button"
                        onClick={() => setLeaderboardCategory("reservations")}
                        className={`px-4 py-2 rounded-md font-semibold transition-colors ${
                            leaderboardCategory === "reservations"
                                ? "bg-green-600 text-white"
                                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                        }`}
                    >
                        Most Reservations
                    </button>
                    <button
                        type="button"
                        onClick={() => setLeaderboardCategory("carbon_dioxide")}
                        className={`px-4 py-2 rounded-md font-semibold transition-colors ${
                            leaderboardCategory === "carbon_dioxide"
                                ? "bg-green-600 text-white"
                                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                        }`}
                    >
                        Most CO<sub>2</sub> Saved
                    </button>
                </div>

                {/* Loading state */}
                {loading && (
                    <div className="text-center text-gray-500 py-8">
                        Loading leaderboard...
                    </div>
                )}

                {/* Error state */}
                {error && (
                    <div className="text-center font-semibold bg-red-100 text-red-800 p-3 mb-4 rounded">
                        {error}
                    </div>
                )}

                {/* Leaderboard list */}
                {!loading && !error && (
                    <div className="space-y-3">
                        {leaderboardData.length === 0 ? (
                            // No data:
                            <div className="text-center text-gray-500 py-8">
                                No data available yet
                            </div>
                        ) : (
                            // Render all items:
                            leaderboardData.map(
                                ([username, count], position) => (
                                    <LeaderboardItem
                                        key={username}
                                        username={username}
                                        count={count}
                                        position={position}
                                        label={
                                            leaderboardCategory ===
                                            "reservations"
                                                ? "Reservations"
                                                : "CO2 Saved (g)"
                                        }
                                    />
                                ),
                            )
                        )}
                    </div>
                )}
            </Card>
        </div>
    );
}
