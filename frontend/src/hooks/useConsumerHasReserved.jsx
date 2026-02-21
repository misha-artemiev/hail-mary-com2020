/**
 * useConsumerReservations.jsx
 * @author Thomas Noakes
 */

import { useState, useEffect } from "react";

// Set the default base API route
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Custom React hook for checking if a user has reserved a bundle.
 * Uses the token stored in the user's local storage.
 *
 * @param {Number} bundleId - The ID of the bundle to reserve.
 * @returns {{ hasReservedBundle: (bundleId: Number) => boolean }}
 *          a function to check if the bundle ID has been reserved.
 */
export function useConsumerReservations() {
    // State object: a list of all the reservations by the user
    const [reservations, setReservations] = useState([]);

    /**
     * Check the reservations.
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
                    `${API_BASE_URL}/consumers/me/reservations`,
                    {
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

                const data = await response.json();
                setReservations(data);
            } catch (err) {
                console.error(err.message);
            }
        }

        fetchReservations();
    }, []);

    /**
     * Checks if the user has reserved the given bundle.
     *
     * @param {Number} bundleId - The ID of the bundle to check.
     *
     * @returns {boolean} if the user has reserved that bundle.
     */
    const hasReservedBundle = (bundleId) => {
        return reservations.some((res) => res.bundle_id === bundleId);
    };

    /**
     * Gets the reservation for a specific bundle.
     *
     * @param {Number} bundleId - The ID of the bundle.
     *
     * @returns {Object|undefined} the reservation for that bundle.
     */
    const getReservationForBundle = (bundleId) => {
        return reservations.find((res) => res.bundle_id === bundleId);
    };

    // Exit with the confirmation function and reservations
    return { hasReservedBundle, getReservationForBundle, reservations };
}
