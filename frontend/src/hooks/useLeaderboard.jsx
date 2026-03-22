/**
 * useLeaderboard.jsx
 * @author Thomas Noakes
 */

import { useState, useEffect } from "react";

// Set the default base API route
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Custom React hook for getting leaderboard data.
 *
 * @param {string} category - The category of data to score by
 * @param {number} [limit=10] - The number of results to return
 *
 * @returns {{ leaderboardData: Array<[]>, loading: boolean, error: string|null } | null}
 *          the leaderboard data and error/loading information
 *
 * ---
 * @example
 * const { leaderboardData, loading, error } = useLeaderboard("reservations", 10);
 * if (loading) return <Spinner />;
 * if (!bundle) return <NotFound />;
 * return <Leaderboard data={leaderboardData} />;
 */
export default function useLeaderboard(category, limit = 10) {
    // State object: stores the leaderboard results
    const [leaderboardData, setLeaderboardData] = useState([]);

    // State object: stores loading and error states
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Fetch leaderboard data
    useEffect(() => {
        // Catch if no category supplied
        if (!category) return;

        async function fetchLeaderboard() {
            setLoading(true);
            setError(null);

            try {
                // Send the request
                const response = await fetch(
                    // e.g. /leaderboard/leaderboard/reservations?limit=10
                    `${API_BASE_URL}/leaderboard/leaderboard/${category}?limit=${limit}`,
                );

                // Catch bad HTTP codes
                if (!response.ok) {
                    throw new Error("Failed to fetch leaderboard");
                }
                const data = await response.json();

                setLeaderboardData(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        }

        fetchLeaderboard();
    }, [category, limit]);

    // Exit with data, loading/error status
    return { leaderboardData, loading, error };
}
