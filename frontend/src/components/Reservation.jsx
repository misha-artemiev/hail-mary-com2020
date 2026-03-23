/**
 * Reservation.jsx
 * @author Thomas Noakes
 */

import React from "react";

/**
 * A reusable panel for displaying a reservation for a bundle.
 *
 * @param {Object} props
 * @param {number} props.id - The ID of the reservation.
 * @param {Date} props.reserved_at - The date the reservation was made.
 * @param {string} props.claimCode - The code to claim with.
 * @param {string} props.status - The status of the reservation.
 * @param {(event: React.MouseEvent<HTMLDivElement>) => void} [props.onClick]
 *          - Optional click event handler
 * @param {() => void} [props.onReport] - Optional report action.
 *
 * @returns {JSX.Element} a reservation panel.
 */
export default function Reservation({
    id,
    reserved_at,
    claimCode,
    status,
    onClick,
    onReport,
}) {
    const statusColors = {
        reserved: "bg-yellow-100 text-yellow-800",
        collected: "bg-green-100 text-green-800",
        no_show: "bg-red-100 text-red-800",
    };

    return (
        <div
            onClick={onClick}
            className="flex justify-between items-center p-3
                     bg-gray-100 rounded-lg
                     cursor-pointer
                     hover:scale-101 transition"
        >
            <div>
                {/* Reservation ID */}
                <p className="font-medium">
                    Reservation{" "}
                    <span className="font-mono font-bold">#{id}</span>
                </p>

                <p className="text-sm text-gray-500">
                    Claim Code:{" "}
                    <span className="font-mono font-bold">{claimCode}</span>
                </p>
            </div>

            <div className="flex items-center gap-3">
                {onReport && (
                    <button
                        type="button"
                        onClick={(e) => {
                            e.stopPropagation();
                            onReport();
                        }}
                        className="px-2 py-1 rounded text-xs font-semibold bg-red-100 text-red-700 hover:bg-red-200 transition"
                    >
                        Report
                    </button>
                )}
                <span
                    className={`px-2 py-1 rounded text-xs font-medium ${statusColors[status] || ""}`}
                >
                    {status}
                </span>
                {/* Date of reservation */}
                <span className="text-sm text-gray-500">
                    {new Date(reserved_at).toLocaleDateString("en-GB")}
                </span>
            </div>
        </div>
    );
}
