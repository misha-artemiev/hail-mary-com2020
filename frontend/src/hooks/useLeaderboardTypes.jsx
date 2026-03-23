/**
 * useLeaderboardTypes.jsx
 */

import { useState, useEffect } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export const CATEGORY_LABELS = {
    reservations: "Most Reservations",
    carbon_dioxide: "Most CO\u2082 Saved",
    money_saved: "Most Money Saved",
    total_spent: "Most Spent",
    weekly_streak: "Longest Streak",
};

export default function useLeaderboardTypes() {
    const [types, setTypes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchTypes() {
            try {
                const response = await fetch(
                    `${API_BASE_URL}/leaderboard/`,
                );
                if (!response.ok) {
                    throw new Error("Failed to fetch leaderboard types");
                }
                const data = await response.json();
                setTypes(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        }

        fetchTypes();
    }, []);

    return { types, loading, error };
}
