/**
 * useCreateBundle.jsx
 * @author Thomas Noakes
 */

import { useState } from "react";

// Set the default base API route
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * A custom React hook to create a new bundle.
 *
 * @returns {{ creating: boolean, createBundle: () => Promise<void> }}
 */
export default function useCreateBundle() {
    // State object: stores status of creating bundle
    const [creating, setCreating] = useState(false);

    /**
     * Create a new bundle with the given data.
     *
     * @param {Object} bundleData - The data of the bundle
     * @returns {Promise<void>}
     */
    async function createBundle(bundleData) {
        setCreating(true);

        // Get the user's auth token from local storage
        const token = localStorage.getItem("authToken");
        if (!token) {
            return;
        }

        try {
            // Send the request
            const response = await fetch(`${API_BASE_URL}/sellers/me/bundles`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                // Convert the data to a JSON string
                body: JSON.stringify({
                    bundle_name: bundleData.bundle_name,
                    description: bundleData.description,
                    price: parseFloat(bundleData.price),
                    total_qty: bundleData.total_qty,
                    weight: parseFloat(bundleData.weight) * 1000, // Convert kg to g
                    discount_percentage: parseInt(
                        bundleData.discount_percentage,
                    ),
                    window_start: bundleData.window_start,
                    window_end: bundleData.window_end,
                    categories: bundleData.categories,
                    allergens: bundleData.allergens,
                }),
            });

            // Catch bad HTTP codes
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message);
            }

            const data = await response.json();
            return data;
        } catch (err) {
            console.error(err.message);
        } finally {
            setCreating(false);
        }
    }

    // Exit with the status of creating the bundle, and the hook to make the bundle
    return {
        creating,
        createBundle,
    };
}
