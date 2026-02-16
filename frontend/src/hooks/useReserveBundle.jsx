/**
 * useReserveBundle.jsx
 * @author Thomas Noakes
 */

import { useState } from "react";

// Set the default base API route
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Custom React hook for reserving a bundle.
 * Uses the token stored in the user's local storage.
 *
 * @param {Number} bundleId - The ID of the bundle to reserve.
 * @returns {{ reserving: boolean, reservationSuccess: boolean, handleReserve: () => Promise<void> }}
 *          object of if the bundle has been/is being reserved, and a promise function to reserve it
 */
export function useReserveBundle(bundleId) {
    // State object: stores reservation status
    const [reserving, setReserving] = useState(false);
    const [reservationSuccess, setReservationSuccess] = useState(false);

    /**
     * Make the reservation.
     * Gets the user's auth token.
     */
    async function handleReserve() {
        setReserving(true);
        setReservationSuccess(false);

        // Get the user's auth token from local storage
        const token = localStorage.getItem("authToken");
        if (!token) {
            return;
        }

        try {
            // Send the request
            const response = await fetch(
                `${API_BASE_URL}/bundles/${bundleId}/reservations`,
                {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                },
            );

            // Catch bad HTTP codes
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail);
            }

            setReservationSuccess(true);
        } catch (err) {
            console.error(err.message);
        } finally {
            setReserving(false);
        }
    }

    // Exit with reservation status information and a handler function
    return {
        reserving,
        reservationSuccess,
        handleReserve,
    };
}
