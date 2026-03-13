/**
 * SellerDashboard.jsx
 * @author Thomas Noakes
 */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

import useSellerBundles from "../hooks/useSellerBundles";
import { useSellerBundleReservations } from "../hooks/useSellerBundleReservations";

import Card from "../components/Card";
import Button from "../components/forms/Button";
import Reservation from "../components/Reservation";

function BundleRow({ bundle }) {
    const [showReservations, setShowReservations] = useState(false);
    const { sellerReservations } = useSellerBundleReservations(
        bundle.bundle_id,
    );

    return (
        <>
            <tr
                className="border-b border-gray-200 hover:bg-gray-50 cursor-pointer"
                onClick={() => setShowReservations(!showReservations)}
            >
                <td className="py-3 px-4">{bundle.bundle_name}</td>
                <td className="py-3 px-4">£{bundle.price}</td>
                <td className="py-3 px-4">{bundle.total_qty}</td>
                <td className="py-3 px-4">{bundle.discount_percentage}%</td>
                <td className="py-3 px-4">
                    {new Date(bundle.window_start).toLocaleString()}
                </td>
                <td className="py-3 px-4">
                    {new Date(bundle.window_end).toLocaleString()}
                </td>
            </tr>
            {showReservations && (
                <tr key={`${bundle.bundle_id}-reservations`}>
                    <td colSpan={6} className="py-4 px-4 bg-gray-50">
                        <div className="ml-4">
                            <h4 className="text-sm font-semibold text-gray-600 mb-2">
                                Reservations ({sellerReservations.length})
                            </h4>
                            {sellerReservations.length === 0 ? (
                                <p className="text-gray-500 text-sm">
                                    No reservations yet.
                                </p>
                            ) : (
                                <div className="space-y-2">
                                    {sellerReservations.map((reservation) => (
                                        <Reservation
                                            key={reservation.reservation_id}
                                            id={reservation.reservation_id}
                                            reserved_at={
                                                reservation.reserved_at
                                            }
                                            claimCode={reservation.claim_code}
                                        />
                                    ))}
                                </div>
                            )}
                        </div>
                    </td>
                </tr>
            )}
        </>
    );
}

export default function SellerDashboard() {
    const { userRole } = useAuth();
    const navigate = useNavigate();
    const { bundles, loading } = useSellerBundles();

    if (userRole !== "seller") {
        return (
            <div className="max-w-4xl mx-auto p-4 md:p-6">
                <Card className="flex flex-col items-centre text-center gap-6">
                    <h1 className="text-3xl font-bold text-green-700">
                        Access Error
                    </h1>
                    <p className="text-gray-600 mb-6">
                        This page is only accessible to sellers.
                    </p>
                    <Button onClick={() => navigate("/")}>Go Home</Button>
                </Card>
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto p-4 md:p-6">
            <Card>
                <div className="flex items-center justify-between mb-6">
                    <h1 className="text-3xl font-bold text-green-700">
                        Seller Dashboard
                    </h1>
                    <Button onClick={() => navigate("/bundles/create")}>
                        Create Bundle
                    </Button>
                </div>

                <div className="mb-6">
                    <Button onClick={() => navigate("/collect")}>
                        Enter Claim Code
                    </Button>
                </div>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-4">
                    My Bundles
                </h2>

                {loading && <p className="text-gray-600">Loading bundles...</p>}

                {!loading && bundles && bundles.length === 0 && (
                    <p className="text-gray-600">No bundles found.</p>
                )}

                {!loading && bundles && bundles.length > 0 && (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="border-b-2 border-green-700">
                                    <th className="py-3 px-4 text-green-700 font-semibold">
                                        Name
                                    </th>
                                    <th className="py-3 px-4 text-green-700 font-semibold">
                                        Price
                                    </th>
                                    <th className="py-3 px-4 text-green-700 font-semibold">
                                        Total Qty
                                    </th>
                                    <th className="py-3 px-4 text-green-700 font-semibold">
                                        Discount
                                    </th>
                                    <th className="py-3 px-4 text-green-700 font-semibold">
                                        Window Start
                                    </th>
                                    <th className="py-3 px-4 text-green-700 font-semibold">
                                        Window End
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {bundles.map((bundle) => (
                                    <BundleRow
                                        key={bundle.bundle_id}
                                        bundle={bundle}
                                    />
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </Card>
        </div>
    );
}
