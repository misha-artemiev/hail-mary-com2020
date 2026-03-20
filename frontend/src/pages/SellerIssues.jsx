/**
 * SellerIssues.jsx
 * @author Ed Brown
 */

import React, { useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import Card from "../components/Card";
import Button from "../components/forms/Button";
import FormInput from "../components/forms/FormInput";
import RoleSelect from "../components/forms/RoleSelect";
import { useAuth } from "../context/AuthContext";
import useSellerIssueReports from "../hooks/useSellerIssueReports";

function formatDate(dateString) {
    if (!dateString) {
        return "Unknown";
    }

    const parsed = new Date(dateString);
    if (Number.isNaN(parsed.getTime())) {
        return "Unknown";
    }

    return parsed.toLocaleString();
}

function statusClasses(status) {
    switch (status) {
        case "open":
            return "bg-yellow-100 text-yellow-800";
        case "resolved":
            return "bg-green-100 text-green-800";
        case "closed":
            return "bg-gray-200 text-gray-800";
        default:
            return "bg-blue-100 text-blue-800";
    }
}

function prettyLabel(value) {
    if (!value) {
        return "Unknown";
    }
    return String(value)
        .toLowerCase()
        .replaceAll("_", " ")
        .replace(/\b\w/g, (char) => char.toUpperCase());
}

export default function SellerIssues() {
    const { userRole } = useAuth();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const { issueReports, loading, error } = useSellerIssueReports();

    const initialStatusFilter =
        searchParams.get("status") === "open" ? "open" : "all";

    const [statusFilter, setStatusFilter] = useState(initialStatusFilter);
    const [reservationFilter, setReservationFilter] = useState("");
    const [sourceFilter, setSourceFilter] = useState("all");

    const statusOptions = useMemo(() => {
        const statuses = new Set(issueReports.map((report) => report.status));
        return [
            { value: "all", label: "All statuses" },
            ...Array.from(statuses).map((status) => ({
                value: status,
                label: prettyLabel(status),
            })),
        ];
    }, [issueReports]);

    const sourceOptions = useMemo(() => {
        const sources = new Set(issueReports.map((report) => report.source_type));
        return [
            { value: "all", label: "All sources" },
            ...Array.from(sources).map((source) => ({
                value: source,
                label: prettyLabel(source),
            })),
        ];
    }, [issueReports]);

    const filteredReports = useMemo(() => {
        return issueReports.filter((report) => {
            const statusMatches =
                statusFilter === "all" || report.status === statusFilter;
            const sourceMatches =
                sourceFilter === "all" || report.source_type === sourceFilter;
            const reservationMatches = reservationFilter
                ? String(report.reservation_id).includes(
                      reservationFilter.trim(),
                  )
                : true;
            return statusMatches && sourceMatches && reservationMatches;
        });
    }, [issueReports, reservationFilter, sourceFilter, statusFilter]);

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
        <div className="max-w-6xl mx-auto p-4 md:p-6 space-y-6">
            <Card>
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
                    <h1 className="text-3xl font-bold text-green-700">
                        Seller Issue Reports
                    </h1>
                    <Button onClick={() => navigate("/dashboard")}>Back to Dashboard</Button>
                </div>
                <p className="text-gray-600">
                    These issues are derived from your bundle and reservation data.
                </p>
            </Card>

            <Card>
                <h2 className="text-xl font-semibold text-green-700 mb-4">
                    Filter Reports
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <RoleSelect
                        label="Status"
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        options={statusOptions}
                    />

                    <RoleSelect
                        label="Source"
                        value={sourceFilter}
                        onChange={(e) => setSourceFilter(e.target.value)}
                        options={sourceOptions}
                    />

                    <FormInput
                        label="Reservation ID"
                        name="reservationFilter"
                        value={reservationFilter}
                        onChange={(e) => setReservationFilter(e.target.value)}
                        placeholder="Search by reservation ID"
                    />
                </div>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-4">
                    Reported Issues
                </h2>

                {loading && <p className="text-gray-600">Loading issue reports...</p>}

                {!loading && error && (
                    <div className="text-center font-semibold bg-red-100 text-red-800 p-3 mb-4 rounded">
                        {error}
                    </div>
                )}

                {!loading && !error && filteredReports.length === 0 && (
                    <p className="text-gray-600">No matching issue reports found.</p>
                )}

                {!loading && !error && filteredReports.length > 0 && (
                    <div className="space-y-3">
                        {filteredReports.map((report) => (
                            <div
                                key={report.report_id}
                                className="border border-gray-200 rounded-lg p-4 bg-white"
                            >
                                <div className="flex flex-wrap items-center gap-2 mb-2">
                                    <span className="font-semibold text-gray-800">
                                        Report #{report.report_id}
                                    </span>
                                    <span
                                        className={`text-xs font-semibold px-2 py-1 rounded ${statusClasses(
                                            report.status,
                                        )}`}
                                    >
                                        {prettyLabel(report.status)}
                                    </span>
                                </div>

                                <p className="text-sm text-gray-700 mb-1">
                                    <span className="font-semibold">Source:</span>{" "}
                                    {prettyLabel(report.source_type)}
                                </p>
                                <p className="text-sm text-gray-700 mb-1">
                                    <span className="font-semibold">Bundle:</span>{" "}
                                    {report.bundle_name} (#{report.bundle_id})
                                </p>
                                <p className="text-sm text-gray-700 mb-1">
                                    <span className="font-semibold">Reservation:</span>{" "}
                                    {report.reservation_id ?? "N/A"}
                                </p>
                                <p className="text-sm text-gray-700 mb-1">
                                    <span className="font-semibold">Issue Type:</span>{" "}
                                    {prettyLabel(report.issue_type)}
                                </p>
                                <p className="text-sm text-gray-700 mb-2">
                                    <span className="font-semibold">Reported:</span>{" "}
                                    {formatDate(report.created_at)}
                                </p>

                                <p className="text-sm text-gray-800 whitespace-pre-line">
                                    {report.description}
                                </p>
                            </div>
                        ))}
                    </div>
                )}
            </Card>
        </div>
    );
}