import { useEffect, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export function useUserBadges(consumerId) {
    const [badges, setBadges] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!consumerId) {
            return;
        }

        let cancelled = false;

        async function fetchBadges() {
            setLoading(true);

            try {
                const [badgesRes, consumerBadgesRes] = await Promise.all([
                    fetch(`${API_BASE_URL}/badges/`),
                    fetch(`${API_BASE_URL}/consumers/${consumerId}/badges`),
                ]);

                if (badgesRes.ok && consumerBadgesRes.ok) {
                    const allBadges = await badgesRes.json();
                    const acquired = await consumerBadgesRes.json();

                    const acquiredMap = new Map(
                        acquired.map((b) => [b.badge_id, b]),
                    );

                    const combinedBadges = allBadges.map((badge) => ({
                        ...badge,
                        level: acquiredMap.get(badge.badge_id)?.level ?? 0,
                        acquired_at:
                            acquiredMap.get(badge.badge_id)?.acquired_at ?? null,
                    }));

                    if (!cancelled) {
                        setBadges(combinedBadges);
                    }
                }
            } catch {
                // Keep badges as empty
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        }

        fetchBadges();

        return () => {
            cancelled = true;
        };
    }, [consumerId]);

    return { badges, loading };
}
