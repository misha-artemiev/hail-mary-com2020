/**
 * useSellerIssueReports.jsx
 * @author Ed Brown
 */

import { useEffect, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

function toDate(value) {
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? null : parsed;
}

/**
 * Builds seller-facing issue items from existing bundle and reservation data.
 *
 * This avoids backend changes by deriving issues from:
 * - seller bundles: /sellers/me/bundles
 * - bundle reservations: /sellers/me/bundles/{bundle_id}/reservations
 */
export default function useSellerIssueReports() {
    const [issueReports, setIssueReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchIssues() {
            setLoading(true);
            setError(null);

            const token = localStorage.getItem("authToken");
            if (!token) {
                setLoading(false);
                return;
            }

            try {
                const bundlesResponse = await fetch(
                    `${API_BASE_URL}/sellers/me/bundles`,
                    {
                        method: "GET",
                        headers: {
                            Authorization: `Bearer ${token}`,
                            "Content-Type": "application/json",
                        },
                    },
                );

                if (!bundlesResponse.ok) {
                    const details = await bundlesResponse
                        .json()
                        .catch(() => null);
                    throw new Error(
                        details?.detail || "Failed to fetch bundles",
                    );
                }

                const bundles = await bundlesResponse.json();
                const now = new Date();
                const derivedIssues = [];

                for (const bundle of bundles) {
                    const reservationsResponse = await fetch(
                        `${API_BASE_URL}/sellers/me/bundles/${bundle.bundle_id}/reservations`,
                        {
                            method: "GET",
                            headers: {
                                Authorization: `Bearer ${token}`,
                                "Content-Type": "application/json",
                            },
                        },
                    );

                    if (!reservationsResponse.ok) {
                        continue;
                    }

                    const reservations = await reservationsResponse.json();
                    const windowEnd = toDate(bundle.window_end);
                    const bundleExpired = windowEnd ? windowEnd < now : false;

                    const uncollectedExpiredReservations = reservations.filter(
                        (reservation) => {
                            const collectedAt = toDate(
                                reservation.collected_at,
                            );
                            return bundleExpired && !collectedAt;
                        },
                    );

                    for (const reservation of uncollectedExpiredReservations) {
                        derivedIssues.push({
                            report_id: `reservation-${reservation.reservation_id}`,
                            source_type: "reservation",
                            reservation_id: reservation.reservation_id,
                            bundle_id: bundle.bundle_id,
                            bundle_name: bundle.bundle_name,
                            issue_type: "UNCOLLECTED_RESERVATION",
                            status: "open",
                            created_at:
                                bundle.window_end || reservation.reserved_at,
                            description:
                                "Pickup window ended but this reservation has not been collected.",
                        });
                    }

                    if (bundleExpired) {
                        const unsoldQuantity = Math.max(
                            (bundle.total_qty || 0) - reservations.length,
                            0,
                        );

                        if (unsoldQuantity > 0) {
                            derivedIssues.push({
                                report_id: `bundle-${bundle.bundle_id}`,
                                source_type: "bundle",
                                reservation_id: null,
                                bundle_id: bundle.bundle_id,
                                bundle_name: bundle.bundle_name,
                                issue_type: "UNSOLD_BUNDLE_STOCK",
                                status: "open",
                                created_at: bundle.window_end,
                                description: `${unsoldQuantity} of ${bundle.total_qty} items were not reserved before the pickup window closed.`,
                            });
                        }
                    }
                }

                derivedIssues.sort((a, b) => {
                    const first = toDate(a.created_at)?.getTime() || 0;
                    const second = toDate(b.created_at)?.getTime() || 0;
                    return second - first;
                });

                setIssueReports(derivedIssues);
            } catch (err) {
                setError(err?.message || "Unable to load seller issues");
                setIssueReports([]);
            } finally {
                setLoading(false);
            }
        }

        fetchIssues();
    }, []);

    return { issueReports, loading, error };
}
