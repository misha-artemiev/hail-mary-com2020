/**
 * useCollectReservation.jsx
 * @author Thomas Noakes
 */

import { useState } from "react";

// Set the default base API route
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * A custom React hook for collecting a reservation using a claim code.
 *
 * @param {number} bundleId - The ID of the bundle to claim for collection.
 *
 * @returns {{ collecting: boolean, collectSuccess: boolean, handleCollect: () => Promise<void>, reset: () => void }}
 */
export function useCollectReservation(bundleId) {
    // State object: the status of the collection
    const [collecting, setCollecting] = useState(false);
    const [collectSuccess, setCollectSuccess] = useState(false);

    /**
     * Send the request to claim the collection.
     *
     * @param {string} claimCode - The claim code of the bundle.
     */
    async function handleCollect(claimCode) {
        setCollecting(true);
        setCollectSuccess(false);

        // Get the user's auth token from local storage
        const token = localStorage.getItem("authToken");
        if (!token) {
            setCollecting(false);
            return;
        }

        try {
            // Send the request
            const response = await fetch(
                // e.g. /sellers/me/bundles/reservations/collect?claim_code=AB_XY
                `${API_BASE_URL}/sellers/me/bundles/${bundleId}/reservations/collect?claim_code=${encodeURIComponent(claimCode)}`,
                {
                    method: "PATCH",
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                },
            );

            // Catch bad HTTP codes
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail);
            }

            setCollectSuccess(true);
        } catch (err) {
            console.error(err.message);
        } finally {
            setCollecting(false);
        }
    }

    // Exit with status and functions to hook into collection/reset
    return {
        collecting,
        collectSuccess,
        handleCollect,
        reset: () => {
            setCollectSuccess(false);
        },
    };
}
