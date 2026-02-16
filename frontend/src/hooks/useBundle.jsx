/**
 * useBundle.jsx
 * @author Thomas Noakes
 */

import { useState, useEffect } from "react";

// Set the default base API route
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export default function useBundle(bundleId) {
    // State object: stores the bundle information
    const [bundle, setBundle] = useState(null);
    const [loading, setLoading] = useState(true);

    // Fetch bundle information
    useEffect(() => {
        // Catch if no bundle ID supplied
        if (!bundleId) return;

        async function fetchBundle() {
            setLoading(true);

            try {
                const response = await fetch(
                    `${API_BASE_URL}/bundles/${bundleId}`,
                );

                if (!response.ok) {
                    if (response.status === 404) {
                        throw new Error("Bundle not found");
                    }
                    throw new Error("Failed to fetch bundle");
                }

                const data = await response.json();
                setBundle(data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        }

        fetchBundle();
    }, [bundleId]);

    // Exit with bundle information and loading status
    return { bundle, loading };
}
