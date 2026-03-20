/**
 * useAdminOpenReservations.jsx
 * @author Ed Brown
 */

import { useEffect, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

function deriveStatus(reservation, bundle) {
    if (reservation.collected_at) {
        return "collected";
    }

    if (!bundle?.window_end) {
        return "reserved";
    }

    const endTime = new Date(bundle.window_end);
    if (Number.isNaN(endTime.getTime())) {
        return "reserved";
    }

    return endTime < new Date() ? "no_show" : "reserved";
}

/**
 * Fetches all reservations visible to admins and returns open (collectable) ones.
 */
export default function useAdminOpenReservations() {
    const [openReservations, setOpenReservations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchOpenReservations() {
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

                const [bundlesResponse, reservationsResponse] = await Promise.all([
                    fetch(`${API_BASE_URL}/admins/database/bundles`, {
                        method: "GET",
                        headers,
                    }),
                    fetch(`${API_BASE_URL}/admins/database/reservations`, {
                        method: "GET",
                        headers,
                    }),
                ]);

                if (!bundlesResponse.ok || !reservationsResponse.ok) {
                    const bundlesError = await bundlesResponse
                        .json()
                        .catch(() => null);
                    const reservationsError = await reservationsResponse
                        .json()
                        .catch(() => null);
                    throw new Error(
                        bundlesError?.detail ||
                            reservationsError?.detail ||
                            "Failed to load reservations",
                    );
                }

                const bundles = await bundlesResponse.json();
                const reservations = await reservationsResponse.json();
                const bundleMap = new Map(
                    bundles.map((bundle) => [bundle.bundle_id, bundle]),
                );

                const open = reservations
                    .map((reservation) => {
                        const bundle = bundleMap.get(reservation.bundle_id);
                        return {
                            ...reservation,
                            bundle_name: bundle?.bundle_name || "Unknown bundle",
                            window_end: bundle?.window_end || null,
                            status: deriveStatus(reservation, bundle),
                        };
                    })
                    .filter((reservation) => reservation.status === "reserved")
                    .sort(
                        (a, b) =>
                            new Date(b.reserved_at).getTime() -
                            new Date(a.reserved_at).getTime(),
                    );

                setOpenReservations(open);
            } catch (err) {
                setError(err?.message || "Failed to load open reservations");
                setOpenReservations([]);
            } finally {
                setLoading(false);
            }
        }

        fetchOpenReservations();
    }, []);

    return { openReservations, loading, error };
}
