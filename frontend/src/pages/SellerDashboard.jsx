/**
 * SellerDashboard.jsx
 * @author Thomas Noakes
 */

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
} from "recharts";

import { useAuth } from "../context/AuthContext";

import useSellerBundles from "../hooks/useSellerBundles";
import { useSellerBundleReservations } from "../hooks/useSellerBundleReservations";
import { useCollectReservation } from "../hooks/useCollectReservation";

import Card from "../components/Card";
import Modal from "../components/Modal";
import Button from "../components/forms/Button";
import FormInput from "../components/forms/FormInput";
import SubmitButton from "../components/forms/SubmitButton";
import Reservation from "../components/Reservation";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

function useAllSellerReservations(bundles) {
    const [allReservations, setAllReservations] = useState([]);

    useEffect(() => {
        async function fetchAllReservations() {
            if (!bundles || bundles.length === 0) {
                return;
            }

            const token = localStorage.getItem("authToken");
            if (!token) {
                return;
            }

            const allRes = [];
            try {
                for (const bundle of bundles) {
                    const response = await fetch(
                        `${API_BASE_URL}/sellers/me/bundles/${bundle.bundle_id}/reservations`,
                        {
                            headers: {
                                Authorization: `Bearer ${token}`,
                            },
                        },
                    );
                    if (response.ok) {
                        const data = await response.json();
                        allRes.push(
                            ...data.map((r) => ({
                                ...r,
                                bundle_name: bundle.bundle_name,
                            })),
                        );
                    }
                }
                setAllReservations(allRes);
            } catch (err) {
                console.error(err.message);
            }
        }

        fetchAllReservations();
    }, [bundles]);

    return allReservations;
}

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
            <Modal isOpen={true} onClose={handleClose}>
                <div className="text-center py-6">
                    <p className="text-green-600 font-semibold text-lg">
                        Bundle successfully collected!
                    </p>
                    <Button onClick={handleClose} className="mt-4">
                        Close
                    </Button>
                </div>
            </Modal>
        );
    }

    return (
        <Modal isOpen={true} onClose={handleClose} title="Collect Bundle">
            <p className="text-gray-600 mb-4">
                Enter the claim code from the customer to mark this bundle as
                collected.
            </p>
            <form onSubmit={handleSubmit}>
                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Select Bundle
                    </label>
                    <select
                        value={selectedBundleId}
                        onChange={(e) => setSelectedBundleId(e.target.value)}
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
                    <SubmitButton disabled={collecting || !selectedBundleId}>
                        {collecting ? "Collecting..." : "Confirm Collection"}
                    </SubmitButton>
                    <Button type="button" onClick={handleClose}>
                        Cancel
                    </Button>
                </div>
            </form>
        </Modal>
    );
}

const COLORS = ["#22c55e", "#eab308", "#ef4444"];

function StatsSection({ bundles, reservations }) {
    const statsByBundle = bundles.map((bundle) => {
        const bundleRes = reservations.filter(
            (r) => r.bundle_name === bundle.bundle_name,
        );
        const total = bundleRes.length;
        const collected = bundleRes.filter(
            (r) => r.status === "collected",
        ).length;
        const reserved = bundleRes.filter(
            (r) => r.status === "reserved",
        ).length;
        const noShow = bundleRes.filter((r) => r.status === "no_show").length;
        return {
            name: bundle.bundle_name.slice(0, 15),
            total,
            collected,
            reserved,
            noShow,
        };
    });

    const statusData = [
        {
            name: "Collected",
            value: reservations.filter((r) => r.status === "collected").length,
        },
        {
            name: "Reserved",
            value: reservations.filter((r) => r.status === "reserved").length,
        },
        {
            name: "No Show",
            value: reservations.filter((r) => r.status === "no_show").length,
        },
    ];

    return (
        <Card className="mb-6">
            <h2 className="text-2xl font-bold text-green-700 mb-4">
                Statistics
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                        Reservations by Bundle
                    </h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={statsByBundle}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis allowDecimals={false} />
                            <Tooltip />
                            <Bar
                                dataKey="collected"
                                stackId="a"
                                fill="#22c55e"
                                name="Collected"
                            />
                            <Bar
                                dataKey="reserved"
                                stackId="a"
                                fill="#eab308"
                                name="Reserved"
                            />
                            <Bar
                                dataKey="noShow"
                                stackId="a"
                                fill="#ef4444"
                                name="No Show"
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
                <div>
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                        Reservation Status
                    </h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                            <Pie
                                data={statusData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="value"
                                label={({ name, value }) => `${name}: ${value}`}
                            >
                                {statusData.map((_, index) => (
                                    <Cell
                                        key={`cell-${index}`}
                                        fill={COLORS[index % COLORS.length]}
                                    />
                                ))}
                            </Pie>
                            <Tooltip />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </Card>
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
    const allReservations = useAllSellerReservations(bundles);

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

            {!loading && bundles && bundles.length > 0 && (
                <StatsSection
                    bundles={bundles}
                    reservations={allReservations}
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
