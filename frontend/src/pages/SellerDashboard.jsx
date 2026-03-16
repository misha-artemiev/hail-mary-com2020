/**
 * SellerDashboard.jsx
 * @author Thomas Noakes
 */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

import useSellerBundles from "../hooks/useSellerBundles";
import { useSellerBundleReservations } from "../hooks/useSellerBundleReservations";
import { useCollectReservation } from "../hooks/useCollectReservation";

import Card from "../components/Card";
import Button from "../components/forms/Button";
import FormInput from "../components/forms/FormInput";
import SubmitButton from "../components/forms/SubmitButton";
import Reservation from "../components/Reservation";

function CollectModal({ bundles, onClose }) {
    const [selectedBundleId, setSelectedBundleId] = useState("");
    const [claimCode, setClaimCode] = useState("");
    const { collecting, collectSuccess, handleCollect, reset } =
        useCollectReservation(selectedBundleId || null);

    const handleSubmit = (e) => {
        e.preventDefault();
        handleCollect(claimCode);
    };

    const handleClose = () => {
        setSelectedBundleId("");
        setClaimCode("");
        reset();
        onClose();
    };

    if (collectSuccess) {
        return (
            <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-50">
                <Card className="w-full max-w-md">
                    <div className="text-center py-6">
                        <p className="text-green-600 font-semibold text-lg">
                            Bundle successfully collected!
                        </p>
                        <Button onClick={handleClose} className="mt-4">
                            Close
                        </Button>
                    </div>
                </Card>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-50">
            <Card className="w-full max-w-md">
                <h2 className="text-xl font-bold text-green-700 mb-4">
                    Collect Bundle
                </h2>
                <p className="text-gray-600 mb-4">
                    Enter the claim code from the customer to mark this bundle
                    as collected.
                </p>
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Select Bundle
                        </label>
                        <select
                            value={selectedBundleId}
                            onChange={(e) =>
                                setSelectedBundleId(e.target.value)
                            }
                            className="w-full p-2 border border-gray-300 rounded"
                            required
                        >
                            <option value="">Select a bundle...</option>
                            {bundles.map((bundle) => (
                                <option
                                    key={bundle.bundle_id}
                                    value={bundle.bundle_id}
                                >
                                    {bundle.bundle_name}
                                </option>
                            ))}
                        </select>
                    </div>
                    <FormInput
                        label="Claim Code"
                        name="claimCode"
                        value={claimCode}
                        onChange={(e) => setClaimCode(e.target.value)}
                        placeholder="Enter the claim code"
                        required
                    />
                    <div className="flex gap-2 mt-4">
                        <SubmitButton
                            disabled={collecting || !selectedBundleId}
                        >
                            {collecting
                                ? "Collecting..."
                                : "Confirm Collection"}
                        </SubmitButton>
                        <Button type="button" onClick={handleClose}>
                            Cancel
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
}

function BundleRow({ bundle }) {
    const [showReservations, setShowReservations] = useState(false);
    const { reservations } = useSellerBundleReservations(bundle.bundle_id);

    const reservedCount = reservations.filter(
        (r) => r.status === "reserved",
    ).length;

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
                    {reservedCount} / {bundle.total_qty}
                </td>
                <td className="py-3 px-4">
                    {new Date(bundle.window_start).toLocaleString()}
                </td>
                <td className="py-3 px-4">
                    {new Date(bundle.window_end).toLocaleString()}
                </td>
            </tr>
            {showReservations && (
                <tr key={`${bundle.bundle_id}-reservations`}>
                    <td colSpan={7} className="py-4 px-4 bg-gray-50">
                        <div className="ml-4">
                            <h4 className="text-sm font-semibold text-gray-600 mb-2">
                                Reservations ({reservations.length})
                            </h4>
                            {reservations.length === 0 ? (
                                <p className="text-gray-500 text-sm">
                                    No reservations yet.
                                </p>
                            ) : (
                                <div className="space-y-2">
                                    {reservations.map((reservation) => (
                                        <Reservation
                                            key={reservation.reservation_id}
                                            id={reservation.reservation_id}
                                            reserved_at={
                                                reservation.reserved_at
                                            }
                                            claimCode={reservation.claim_code}
                                            status={reservation.status}
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
    const [showCollectModal, setShowCollectModal] = useState(false);

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
                    <Button onClick={() => setShowCollectModal(true)}>
                        Enter Claim Code
                    </Button>
                </div>
            </Card>

            {showCollectModal && (
                <CollectModal
                    bundles={bundles}
                    onClose={() => setShowCollectModal(false)}
                />
            )}

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
                                        Reservations
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
