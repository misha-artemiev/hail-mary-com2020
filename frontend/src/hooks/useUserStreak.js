import { useEffect, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export function useUserStreak(consumerId) {
    const [streak, setStreak] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!consumerId) {
            return;
        }

        let cancelled = false;

        async function fetchStreak() {
            setLoading(true);

            try {
                const res = await fetch(
                    `${API_BASE_URL}/consumers/${consumerId}/streaks`,
                );

                if (res.ok) {
                    const data = await res.json();
                    if (!cancelled) {
                        setStreak(data);
                    }
                }
            } catch {
                // Keep streak as null
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        }

        fetchStreak();

        return () => {
            cancelled = true;
        };
    }, [consumerId]);

    return { streak, loading };
}
