/**
 * ConsumerDashboard.jsx
 * @author Ed Brown
 */

import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useConsumerReservations } from "../hooks/useConsumerHasReserved";

import Card from "../components/Card";
import Button from "../components/forms/Button";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

function formatDateTime(value) {
    if (!value) {
        return "-";
    }

    return new Date(value).toLocaleString("en-GB", {
        weekday: "short",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

function ReservationTable({ title, rows, showCollectedAt }) {
    const navigate = useNavigate();

    return (
        <Card>
            <h2 className="text-2xl font-bold text-green-700 mb-4">{title}</h2>

            {rows.length === 0 ? (
                <p className="text-gray-600">No bundles in this section yet.</p>
            ) : (
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b-2 border-green-700">
                                <th className="py-3 px-4 text-green-700 font-semibold">
                                    Bundle
                                </th>
                                <th className="py-3 px-4 text-green-700 font-semibold">
                                    Claim Code
                                </th>
                                <th className="py-3 px-4 text-green-700 font-semibold">
                                    Reserved At
                                </th>
                                {showCollectedAt && (
                                    <th className="py-3 px-4 text-green-700 font-semibold">
                                        Collected At
                                    </th>
                                )}
                                <th className="py-3 px-4 text-green-700 font-semibold">
                                    Listing
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows.map((reservation) => (
                                <tr
                                    key={reservation.reservation_id}
                                    className="border-b border-gray-200 hover:bg-gray-50"
                                >
                                    <td className="py-3 px-4">
                                        {reservation.bundle_name ||
                                            `Bundle #${reservation.bundle_id}`}
                                    </td>
                                    <td className="py-3 px-4 font-mono font-semibold">
                                        {reservation.claim_code || "-"}
                                    </td>
                                    <td className="py-3 px-4">
                                        {formatDateTime(
                                            reservation.reserved_at,
                                        )}
                                    </td>
                                    {showCollectedAt && (
                                        <td className="py-3 px-4">
                                            {formatDateTime(
                                                reservation.collected_at,
                                            )}
                                        </td>
                                    )}
                                    <td className="py-3 px-4">
                                        <Button
                                            onClick={() =>
                                                navigate(
                                                    `/bundles/${reservation.bundle_id}`,
                                                )
                                            }
                                        >
                                            Open Listing
                                        </Button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </Card>
    );
}

export default function ConsumerDashboard() {
    const navigate = useNavigate();
    const { userRole } = useAuth();
    const { reservations } = useConsumerReservations();

    const [bundleNamesById, setBundleNamesById] = useState({});
    const [bundleLoading, setBundleLoading] = useState(true);

    useEffect(() => {
        async function fetchBundleNames() {
            const token = localStorage.getItem("authToken");
            const uniqueBundleIds = [
                ...new Set(
                    reservations.map((reservation) => reservation.bundle_id),
                ),
            ];

            if (!token || uniqueBundleIds.length === 0) {
                setBundleNamesById({});
                setBundleLoading(false);
                return;
            }

            setBundleLoading(true);

            try {
                const bundleResponses = await Promise.all(
                    uniqueBundleIds.map(async (bundleId) => {
                        const response = await fetch(
                            `${API_BASE_URL}/bundles/${bundleId}`,
                            {
                                headers: {
                                    Authorization: `Bearer ${token}`,
                                },
                            },
                        );

                        if (!response.ok) {
                            return [bundleId, null];
                        }

                        const bundle = await response.json();
                        return [bundleId, bundle.bundle_name || null];
                    }),
                );

                setBundleNamesById(Object.fromEntries(bundleResponses));
            } catch (error) {
                console.error("Unable to load bundle names", error);
                setBundleNamesById({});
            } finally {
                setBundleLoading(false);
            }
        }

        fetchBundleNames();
    }, [reservations]);

    const reservationsWithBundleNames = useMemo(() => {
        return reservations.map((reservation) => ({
            ...reservation,
            bundle_name: bundleNamesById[reservation.bundle_id] || null,
        }));
    }, [reservations, bundleNamesById]);

    const activeReservations = reservationsWithBundleNames.filter(
        (reservation) => reservation.status === "reserved",
    );

    const collectedReservations = reservationsWithBundleNames.filter(
        (reservation) => reservation.status === "collected",
    );

    if (userRole !== "consumer") {
        return (
            <div className="max-w-4xl mx-auto p-4 md:p-6">
                <Card className="flex flex-col items-centre text-center gap-6">
                    <h1 className="text-3xl font-bold text-green-700">
                        Access Error
                    </h1>
                    <p className="text-gray-600 mb-6">
                        This page is only accessible to consumers.
                    </p>
                    <Button onClick={() => navigate("/")}>Go Home</Button>
                </Card>
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto p-4 md:p-6">
            <Card>
                <h1 className="text-3xl font-bold text-green-700 mb-2">
                    Consumer Dashboard
                </h1>
                <p className="text-gray-600">
                    See all of your active reservations and previously collected
                    bundles.
                </p>
            </Card>

            {bundleLoading ? (
                <Card>
                    <p className="text-gray-600">Loading reservations...</p>
                </Card>
            ) : (
                <>
                    <ReservationTable
                        title="My Reserved Bundles"
                        rows={activeReservations}
                        showCollectedAt={false}
                    />
                    <ReservationTable
                        title="Collected Bundles"
                        rows={collectedReservations}
                        showCollectedAt={true}
                    />
                </>
            )}
        </div>
    );
}
