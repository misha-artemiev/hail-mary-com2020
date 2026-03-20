/**
 * useSellerBundles.jsx
 * @author Thomas Noakes
 */

import { useState, useEffect } from "react";

import { getAuthToken } from "../services/authService";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Custom React hook for fetching seller's bundles.
 *
 * @returns {{ bundles: Array<Object>|null, loading: boolean }}
 *          the bundle information and loading status.
 *
 * ---
 * @example
 * const { bundles, loading, error } = useSellerBundles();
 *
 * if (loading) return <Spinner />;
 * if (error) return <Error message={error} />;
 * return <BundleTable bundles={bundles} />;
 */
export default function useSellerBundles() {
    const [bundles, setBundles] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchBundles() {
            setLoading(true);

            try {
                const token = getAuthToken();
                const response = await fetch(
                    `${API_BASE_URL}/sellers/me/bundles`,
                    {
                        method: "GET",
                        headers: {
                            Authorization: `Bearer ${token}`,
                            "Content-Type": "application/json",
                        },
                    },
                );

                if (!response.ok) {
                    throw new Error("Failed to fetch bundles");
                }

                const data = await response.json();
                setBundles(data);
            } finally {
                setLoading(false);
            }
        }

        fetchBundles();
    }, []);

    return { bundles, loading };
}
