/**
 * Leaderboard.jsx
 * @author Thomas Noakes
 */

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

// Components
import Card from "../components/Card";
import LeaderboardItem from "../components/LeaderboardItem";

// Hooks
import useLeaderboard from "../hooks/useLeaderboard";
import useLeaderboardTypes, { CATEGORY_LABELS } from "../hooks/useLeaderboardTypes";

// Services
import { getUsername } from "../services/authService";

/**
 * The leaderboard page of the site.
 * Displays top users by reservations or carbon dioxide saved.
 *
 * @returns {JSX.Element} the leaderboard page
 */
export default function Leaderboard() {
    const navigate = useNavigate();

    const { types: leaderboardTypes, loading: typesLoading, error: typesError } =
        useLeaderboardTypes();

    // Get current user's username
    const [currentUsername, setCurrentUsername] = useState(null);
    useEffect(() => {
        setCurrentUsername(getUsername());
    }, []);

    // State objects: stores the leaderboard data
    const [leaderboardCategory, setLeaderboardCategory] =
        useState("reservations");
    const [leaderboardLimit, setLeaderboardLimit] = useState(10);
    const { leaderboardData, loading, error } = useLeaderboard(
        leaderboardCategory,
        leaderboardLimit,
    );

    /**
     * Adjust the score of each item to account for duplicate (tied) scores.
     *
     * *e.g.* scores of {14, 14, 12, 10} would have positions {1, 1, 3, 4}
     *
     * @param {Array<[]>} data - The data in the whole leaderboard
     * @param {Number} currentIndex - The index to change
     *
     * @returns {Number} the actual adjusted position
     */
    const getRank = (data, currentIndex) => {
        const currentScore = data[currentIndex][1];
        let higherCount = 0;

        // Increase for each other score higher than this
        for (let i = 0; i < currentIndex; i++) {
            if (data[i][1] > currentScore) {
                higherCount++;
            }
        }
        return higherCount;
    };

    return (
        <div className="max-w-2xl mx-auto p-4 md:p-6">
            <Card>
                <h1 className="text-3xl font-bold text-green-700 mb-6 text-center">
                    Leaderboard
                </h1>

                {/* Type selector */}
                <div className="flex flex-col sm:flex-row justify-center items-center gap-4 mb-6">
                    <div className="flex flex-wrap justify-center gap-2">
                        {typesLoading ? (
                            <span className="text-gray-500">Loading categories...</span>
                        ) : typesError ? (
                            <span className="text-red-500">{typesError}</span>
                        ) : (
                            leaderboardTypes.map((type) => (
                                <button
                                    key={type}
                                    type="button"
                                    onClick={() => setLeaderboardCategory(type)}
                                    className={`px-4 py-2 rounded-md font-semibold transition-colors ${
                                        leaderboardCategory === type
                                            ? "bg-green-600 text-white"
                                            : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                                    }`}
                                >
                                    {CATEGORY_LABELS[type] || type}
                                </button>
                            ))
                        )}
                    </div>

                    {/* Limit selection */}
                    <div className="relative">
                        <select
                            value={leaderboardLimit}
                            onChange={(e) => setLeaderboardLimit(Number(e.target.value))}
                            className="appearance-none bg-white border border-gray-300 rounded-md px-4 py-2 pr-8 font-semibold text-gray-700 cursor-pointer hover:border-green-500 focus:outline-none focus:ring-2 focus:ring-green-500"
                        >
                            <option value={10}>Top 10</option>
                            <option value={25}>Top 25</option>
                            <option value={50}>Top 50</option>
                            <option value={100}>Top 100</option>
                        </select>
                        <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </div>
                    </div>
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
                                        position={getRank(
                                            leaderboardData,
                                            position,
                                        )}
                                        category={leaderboardCategory}
                                        isCurrentUser={
                                            username === currentUsername
                                        }
                                        onClick={() =>
                                            navigate(`/user/${username}`)
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
