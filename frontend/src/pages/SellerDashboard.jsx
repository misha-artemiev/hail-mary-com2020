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
    LineChart,
    Line,
    Legend,
    ReferenceLine,
} from "recharts";

import { useAuth } from "../context/AuthContext";
import useSellerBundles from "../hooks/useSellerBundles";
import useSellerIssueReports from "../hooks/useSellerIssueReports";
import { useSellerAnalytics } from "../hooks/useSellerAnalytics";

import SellerProfileCard from "../components/SellerProfileCard";
import { useSellerBundleReservations } from "../hooks/useSellerBundleReservations";
import { useCollectReservation } from "../hooks/useCollectReservation";

import Card from "../components/Card";
import Modal from "../components/Modal";
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

function AnalyticsSection({ analytics, onRefresh, refreshing }) {
    const [timelineData, setTimelineData] = useState([]);
    const [categoryData, setCategoryData] = useState([]);
    const [timeWindowData, setTimeWindowData] = useState([]);
    const [sellThroughData, setSellThroughData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const loadAnalytics = async () => {
        setLoading(true);
        setError(null);
        try {
            const [
                actualRes,
                forecastRes,
                categoryRes,
                timeWindowRes,
                sellThroughRes,
            ] = await Promise.allSettled([
                analytics.fetchGraph(1),
                analytics.fetchGraph(5),
                analytics.fetchGraph(3),
                analytics.fetchGraph(4),
                analytics.fetchGraph(2),
            ]);

            if (
                actualRes.status === "fulfilled" &&
                forecastRes.status === "fulfilled"
            ) {
                const combined = await analytics.getCombinedTimelineData();
                setTimelineData(combined);
            }

            if (categoryRes.status === "fulfilled") {
                const series = categoryRes.value[1];
                const catSeries = series.find(
                    (s) => s[0].series_name === "categories",
                );
                if (catSeries) {
                    setCategoryData(
                        catSeries[1].map((p) => ({
                            name: p.x,
                            value: Number(p.y),
                        })),
                    );
                }
            }

            if (timeWindowRes.status === "fulfilled") {
                const series = timeWindowRes.value[1];
                const twSeries = series.find(
                    (s) => s[0].series_name === "time_windows",
                );
                if (twSeries) {
                    setTimeWindowData(
                        twSeries[1].map((p) => ({
                            name: p.x,
                            value: Number(p.y),
                        })),
                    );
                }
            }

            if (sellThroughRes.status === "fulfilled") {
                const series = sellThroughRes.value[1];
                const stSeries = series.find(
                    (s) => s[0].series_name === "sell_rate",
                );
                if (stSeries) {
                    setSellThroughData(
                        stSeries[1].map((p) => ({
                            name: p.x,
                            value: Number(p.y),
                        })),
                    );
                }
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadAnalytics();
    }, [analytics]);

    const today = new Date().toISOString().split("T")[0];

    return (
        <Card className="mb-6">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-green-700">Analytics</h2>
                <Button
                    onClick={() => {
                        onRefresh();
                        setTimeout(loadAnalytics, 500);
                    }}
                    disabled={refreshing || loading}
                    className="!w-auto"
                >
                    {refreshing || loading ? "Loading..." : "Refresh Analytics"}
                </Button>
            </div>

            {error && <p className="text-red-500 mb-4">Error: {error}</p>}

            <div className="space-y-8">
                <div>
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                        Sales vs Posted (Past & Forecast)
                    </h3>
                    {timelineData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={timelineData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="date" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <ReferenceLine
                                    x={today}
                                    stroke="#666"
                                    strokeDasharray="5 5"
                                    label={{
                                        value: "Today",
                                        position: "top",
                                    }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="actualSales"
                                    stroke="#22c55e"
                                    strokeWidth={2}
                                    name="Actual Sales"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="actualPosted"
                                    stroke="#22c55e"
                                    strokeWidth={2}
                                    strokeDasharray="5 5"
                                    name="Actual Posted"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="forecastSales"
                                    stroke="#3b82f6"
                                    strokeWidth={2}
                                    strokeDasharray="5 5"
                                    name="Forecast Sales"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="forecastPosted"
                                    stroke="#3b82f6"
                                    strokeWidth={2}
                                    strokeDasharray="10 5"
                                    name="Forecast Posted"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="w-full h-[300px] flex items-center justify-center bg-gray-50 border border-gray-200 rounded">
                            <p className="text-gray-500">
                                No sales data yet. Click &quot;Refresh
                                Analytics&quot; to generate.
                            </p>
                        </div>
                    )}
                </div>

                <div>
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                        Category Distribution
                    </h3>
                    {categoryData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={250}>
                            <BarChart data={categoryData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip />
                                <Bar
                                    dataKey="value"
                                    fill="#8b5cf6"
                                    name="Reservations"
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="w-full h-[250px] flex items-center justify-center bg-gray-50 border border-gray-200 rounded">
                            <p className="text-gray-500">
                                No category data yet. Click &quot;Refresh
                                Analytics&quot; to generate.
                            </p>
                        </div>
                    )}
                </div>

                <div>
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                        Time Window Distribution
                    </h3>
                    {timeWindowData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={250}>
                            <BarChart data={timeWindowData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip />
                                <Bar
                                    dataKey="value"
                                    fill="#f59e0b"
                                    name="Reservations"
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="w-full h-[250px] flex items-center justify-center bg-gray-50 border border-gray-200 rounded">
                            <p className="text-gray-500">
                                No time window data yet. Click &quot;Refresh
                                Analytics&quot; to generate.
                            </p>
                        </div>
                    )}
                </div>

                <div>
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                        Sell Through Rate
                    </h3>
                    {sellThroughData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={250}>
                            <PieChart>
                                <Pie
                                    data={sellThroughData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    paddingAngle={5}
                                    dataKey="value"
                                    label={({ name, value }) =>
                                        `${name}: ${value}%`
                                    }
                                >
                                    <Cell fill="#22c55e" />
                                    <Cell fill="#ef4444" />
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="w-full h-[250px] flex items-center justify-center bg-gray-50 border border-gray-200 rounded">
                            <p className="text-gray-500">
                                No sell through data yet. Click &quot;Refresh
                                Analytics&quot; to generate.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </Card>
    );
}

function BundleRow({ bundle }) {
    const navigate = useNavigate();
    const [showReservations, setShowReservations] = useState(false);
    const { reservations } = useSellerBundleReservations(bundle.bundle_id);

    const reservationCount = reservations.length;

    const getStatus = (reservation) => {
        return reservation.collected_at ? "collected" : "reserved";
    };

    return (
        <>
            <tr
                className="border-b border-gray-200 hover:bg-gray-50 cursor-pointer"
                onClick={() => setShowReservations(!showReservations)}
            >
                <td className="py-3 px-4">
                    <div>
                        <p className="font-medium">{bundle.bundle_name}</p>
                        <p className="text-xs text-gray-500 truncate max-w-[150px]">
                            {bundle.description}
                        </p>
                    </div>
                </td>
                <td className="py-3 px-4">£{bundle.price}</td>
                <td className="py-3 px-4">{bundle.discount_percentage}%</td>
                <td className="py-3 px-4">
                    {(bundle.carbon_dioxide / 1000).toFixed(1)}kg
                </td>
                <td className="py-3 px-4">
                    {reservationCount} / {bundle.total_qty}
                </td>
                <td className="py-3 px-4 text-sm">
                    {new Date(bundle.window_start).toLocaleString()}
                </td>
                <td className="py-3 px-4 text-sm">
                    {new Date(bundle.window_end).toLocaleString()}
                </td>
                <td className="py-3 px-4">
                    <Button
                        onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/bundles/${bundle.bundle_id}`);
                        }}
                    >
                        Open
                    </Button>
                </td>
            </tr>
            {showReservations && (
                <tr key={`${bundle.bundle_id}-reservations`}>
                    <td colSpan={8} className="py-4 px-4 bg-gray-50">
                        <div className="ml-4">
                            <h4 className="text-sm font-semibold text-gray-600 mb-2">
                                Reservations
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
                                            claimCode="-"
                                            status={getStatus(reservation)}
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
    const { userRole, logout } = useAuth();
    const navigate = useNavigate();
    const { bundles, loading } = useSellerBundles();
    const { issueReports, loading: issuesLoading } = useSellerIssueReports();
    const openIssuesCount = issueReports.filter(
        (issue) => issue.status === "open",
    ).length;
    const [showCollectModal, setShowCollectModal] = useState(false);
    const analytics = useSellerAnalytics();
    const [refreshingAnalytics, setRefreshingAnalytics] = useState(false);

    const handleRefreshAnalytics = async () => {
        setRefreshingAnalytics(true);
        try {
            await analytics.refreshAnalytics();
        } catch (err) {
            console.error("Failed to refresh analytics:", err);
        } finally {
            setRefreshingAnalytics(false);
        }
    };

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
                    <div className="flex gap-2">
                        <Button
                            onClick={() => setShowCollectModal(true)}
                            className="!w-auto"
                        >
                            Enter Claim Code
                        </Button>
                        <Button
                            onClick={() => navigate("/bundles/create")}
                            className="!w-auto"
                        >
                            Create Bundle
                        </Button>
                    </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <button
                        type="button"
                        onClick={() =>
                            navigate("/dashboard/issues?status=open")
                        }
                        className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-left hover:bg-amber-100 transition"
                    >
                        <p className="text-sm font-medium text-amber-800">
                            Open Issues
                        </p>
                        <p className="text-3xl font-bold text-amber-900">
                            {issuesLoading ? "..." : openIssuesCount}
                        </p>
                    </button>
                    <button
                        type="button"
                        onClick={() => navigate("/dashboard/issues")}
                        className="rounded-lg border border-gray-200 bg-gray-50 p-4 text-left hover:bg-gray-100 transition"
                    >
                        <p className="text-sm font-medium text-gray-700">
                            Total Derived Issues
                        </p>
                        <p className="text-3xl font-bold text-gray-900">
                            {issuesLoading ? "..." : issueReports.length}
                        </p>
                    </button>
                </div>
            </Card>

            <SellerProfileCard onLogout={logout} />

            <AnalyticsSection
                analytics={analytics}
                onRefresh={handleRefreshAnalytics}
                refreshing={refreshingAnalytics}
            />

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
                                        Discount
                                    </th>
                                    <th className="py-3 px-4 text-green-700 font-semibold">
                                        CO2 Saved
                                    </th>
                                    <th className="py-3 px-4 text-green-700 font-semibold">
                                        Reserved
                                    </th>
                                    <th className="py-3 px-4 text-green-700 font-semibold">
                                        Start
                                    </th>
                                    <th className="py-3 px-4 text-green-700 font-semibold">
                                        End
                                    </th>
                                    <th className="py-3 px-4 text-green-700 font-semibold">
                                        Listing
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
