import { useEffect, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export function useUserImpact(consumerId) {
    const [impact, setImpact] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!consumerId) {
            return;
        }

        let cancelled = false;

        async function fetchImpact() {
            setLoading(true);

            try {
                const res = await fetch(
                    `${API_BASE_URL}/consumers/${consumerId}/impact`,
                );

                if (res.ok) {
                    const data = await res.json();
                    if (!cancelled) {
                        setImpact(data);
                    }
                }
            } catch {
                // Keep impact as null
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        }

        fetchImpact();

        return () => {
            cancelled = true;
        };
    }, [consumerId]);

    return { impact, loading };
}
