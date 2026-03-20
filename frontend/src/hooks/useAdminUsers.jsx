/**
 * useAdminUsers.jsx
 * @author Ed Brown
 */

import { useEffect, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Fetches all consumers and sellers visible to admins.
 */
export default function useAdminUsers() {
    const [consumers, setConsumers] = useState([]);
    const [sellers, setSellers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let cancelled = false;

        async function fetchUsers() {
            setLoading(true);
            setError(null);

            const token = localStorage.getItem("authToken");
            if (!token) {
                setLoading(false);
                return;
            }

            try {
                const headers = {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                };

                const [consumersRes, sellersRes] = await Promise.all([
                    fetch(`${API_BASE_URL}/admins/database/consumers`, {
                        method: "GET",
                        headers,
                    }),
                    fetch(`${API_BASE_URL}/admins/database/sellers`, {
                        method: "GET",
                        headers,
                    }),
                ]);

                if (!consumersRes.ok || !sellersRes.ok) {
                    const consumersErr = await consumersRes.json().catch(() => null);
                    const sellersErr = await sellersRes.json().catch(() => null);
                    throw new Error(
                        consumersErr?.detail ||
                            sellersErr?.detail ||
                            "Failed to load users",
                    );
                }

                const [consumerData, sellerData] = await Promise.all([
                    consumersRes.json(),
                    sellersRes.json(),
                ]);

                if (!cancelled) {
                    setConsumers(consumerData || []);
                    setSellers(sellerData || []);
                }
            } catch (err) {
                if (!cancelled) {
                    setError(err?.message || "Failed to load users");
                    setConsumers([]);
                    setSellers([]);
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        }

        fetchUsers();

        return () => {
            cancelled = true;
        };
    }, []);

    return { consumers, sellers, loading, error };
}
