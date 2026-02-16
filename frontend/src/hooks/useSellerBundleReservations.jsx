/**
 * useSellerBundleReservations.jsx
 * @author Thomas Noakes
 */

import { useState, useEffect } from "react";

// Set the default base API route
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Custom React hook for fetching reservations for a seller's bundle.
 *
 * @param {Number} bundleId - The ID of the bundle to fetch reservations for.
 *
 * @returns {{ reservations: Array<Object> }} a list of active reservations for the bundle.
 */
export function useSellerBundleReservations(bundleId) {
    // State object: a list of all the reservations for the bundle
    const [reservations, setReservations] = useState([]);

    /**
     * Get all reservations.
     * Uses the user's auth token.
     */
    useEffect(() => {
        async function fetchReservations() {
            // Get the user's auth token from local storage
            const token = localStorage.getItem("authToken");
            if (!token) {
                return;
            }

            try {
                // Send the request
                const response = await fetch(
                    `${API_BASE_URL}/sellers/me/bundles/${bundleId}/reservations`,
                    {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    },
                );

                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.detail);
                }

                const data = await response.json();
                setReservations(data);
            } catch (err) {
                console.error(err.message);
            }
        }

        fetchReservations();
    }, [bundleId]);

    // Filter by reservations that are reserved
    const sellerReservations = reservations.filter(
        (res) => res.status === "reserved",
    );

    // Exit with a list of active reservations
    return { sellerReservations };
}
