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
 * @param {(event: React.MouseEvent<HTMLDivElement>) => void} [props.onClick]
 *          - Optional click event handler
 *
 * @returns {JSX.Element} a reservation panel.
 */
export default function Reservation({ id, reserved_at, claimCode, onClick }) {
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

            {/* Date of reservation */}
            <span className="text-sm text-gray-500">
                {new Date(reserved_at).toLocaleDateString("en-GB")}
            </span>
        </div>
    );
}
