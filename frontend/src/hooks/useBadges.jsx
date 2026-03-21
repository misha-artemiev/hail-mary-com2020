import { useState, useEffect } from "react";
import { getAuthToken } from "../services/authService";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export default function useBadges() {
    const [badges, setBadges] = useState([]);
    const [consumerBadges, setConsumerBadges] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchBadges = async () => {
        const token = getAuthToken();
        if (!token) {
            setError("Not authenticated");
            setLoading(false);
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const [badgesRes, consumerBadgesRes] = await Promise.all([
                fetch(`${API_BASE_URL}/badges/`, {
                    headers: { Authorization: `Bearer ${token}` },
                }),
                fetch(`${API_BASE_URL}/consumers/me/badges`, {
                    headers: { Authorization: `Bearer ${token}` },
                }),
            ]);

            if (badgesRes.ok && consumerBadgesRes.ok) {
                const allBadges = await badgesRes.json();
                const acquired = await consumerBadgesRes.json();
                setBadges(allBadges);
                setConsumerBadges(acquired);
            } else {
                setError(`Failed to load badges`);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchBadges();
    }, []);

    const getConsumerBadgeLevel = (badgeId) => {
        const acquired = consumerBadges.find((b) => b.badge_id === badgeId);
        return acquired?.level || 0;
    };

    return {
        badges,
        consumerBadges,
        loading,
        error,
        refetch: fetchBadges,
        getConsumerBadgeLevel,
    };
}
