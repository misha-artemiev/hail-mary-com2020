/**
 * Bundle.jsx
 * @author Thomas Noakes
 */

import React from "react";
import { useParams, useNavigate } from "react-router-dom";

// Hooks
import useBundle from "../hooks/useBundle";
import { useAuth } from "../context/AuthContext";
import { useReserveBundle } from "../hooks/useReserveBundle";
import { useConsumerReservations } from "../hooks/useConsumerHasReserved";
import { useSellerBundleReservations } from "../hooks/useSellerBundleReservations";

// Components
import Card from "../components/Card";
import InfoLine from "../components/InfoLine";
import Button from "../components/forms/Button";
import Reservation from "../components/Reservation";

// Resources
import defaultListing from "../assets/default-listing.jpg";

/**
 * The bundle page.
 * The requested bundle is taken from the URL (*i.e.* `/bundles/<bundle_id`)
 * If logged in:
 *  - Consumers can reserve bundles
 *  - Sellers can view reservations
 *
 * @returns the specific bundle page.
 */
export default function Bundle() {
    const navigate = useNavigate();
    const { id } = useParams();

    // Get if the user has already reserved
    const { hasReservedBundle, getReservationForBundle } =
        useConsumerReservations();

    // Get the role of the logged in user
    const { userRole } = useAuth();

    // Get bundle information
    const { bundle, loading, error } = useBundle(id);

    // Get reservation information
    const { reserving, reservationSuccess, handleReserve } =
        useReserveBundle(id);

    // Get seller reservations
    const { sellerReservations } = useSellerBundleReservations(parseInt(id));

    if (loading) {
        return (
            <div className="max-w-4xl mx-auto p-4 md:p-6">
                <Card>Loading bundle...</Card>
            </div>
        );
    }

    // Display any error when finding the bundle
    if (error) {
        return (
            // TODO: better error page
            <div className="max-w-4xl mx-auto p-4 md:p-6">
                <Card>Bundle not found!</Card>
            </div>
        );
    }

    // Display an error if the bundle doesn't exist/can't be found
    if (!bundle) {
        return (
            // TODO: better error page
            <div className="max-w-4xl mx-auto p-4 md:p-6">
                <Card>Bundle not found!</Card>
            </div>
        );
    }

    // Calculate discount percentage
    const originalPrice = Number(bundle.price);
    const discountedPrice =
        originalPrice * (1 - bundle.discount_percentage / 100);

    // Dates and times bundle is available
    const windowStart = new Date(bundle.window_start);
    const windowEnd = new Date(bundle.window_end);

    /**
     * Convert a date object to a formatted string.
     *
     * @param {Date} date - The date to format.
     *
     * @returns the formatted date string.
     */
    const formatDateTime = (date) => {
        return date.toLocaleString("en-GB", {
            weekday: "short",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    /**
     * Dynamically renders given reservations.
     *
     * @param {Object} reservations - The categories to display.
     * @returns {JSX.Element} a set of reservation elements
     */
    const renderReservations = (reservations) =>
        reservations.map((reservation) => (
            <Reservation
                key={reservation.reservation_id}
                id={reservation.reservation_id}
                reserved_at={reservation.reserved_at}
                claimCode={reservation.claim_code}
                onReport={() =>
                    navigate(
                        `/report-error?issueType=reservation&reservation_id=${reservation.reservation_id}&bundle_id=${id}`,
                    )
                }
            />
        ));

    return (
        <div className="max-w-4xl mx-auto p-4 md:p-6">
            <Card className="overflow-hidden">
                <div className="flex flex-col md:flex-row gap-6">
                    {/* Image */}
                    <div className="relative w-full h-64 md:h-80">
                        <img
                            src={defaultListing} // TODO: fetch image
                            alt={bundle.bundle_name}
                            className="w-full h-full object-cover"
                        />
                    </div>
                </div>

                <div className="p-6 text-center">
                    {/* Title */}
                    <h1 className="text-2xl md:text-4xl font-bold text-green-700">
                        {bundle.bundle_name}
                    </h1>

                    {/* Description */}
                    <p className="mt-3 text-gray-600 max-w-xl mx-auto">
                        {bundle.description}
                    </p>

                    {/* Information */}
                    <div className="mt-5 flex items-center justify-center gap-3 flex-wrap">
                        {/* Original price */}
                        <span className="text-gray-400 line-through text-lg">
                            £{originalPrice.toFixed(2)}
                        </span>

                        {/* New price */}
                        <span className="text-3xl font-bold text-green-600">
                            £{discountedPrice.toFixed(2)}
                        </span>

                        {/* Discount tag */}
                        <span className="bg-red-500 text-white text-sm px-3 py-1 rounded-full hover:">
                            {bundle.discount_percentage}% OFF
                        </span>
                    </div>
                </div>
            </Card>

            <Card>
                {/* Subtitle */}
                <h2 className="text-xl font-bold text-green-700 mb-4">
                    Pickup Details
                </h2>

                {/* TODO: get seller information */}
                <InfoLine label="Restaurant" value="" />

                <InfoLine
                    label="Pickup Window"
                    value={`${formatDateTime(windowStart)} - ${formatDateTime(windowEnd)}`}
                />

                {(userRole === "consumer" || userRole === "seller") && (
                    <div className="mt-4">
                        <Button
                            onClick={() =>
                                navigate(
                                    `/report-error?issueType=bundle&bundle_id=${id}`,
                                )
                            }
                        >
                            Report This Bundle
                        </Button>
                    </div>
                )}
            </Card>

            {/* Consumer reservation section */}
            {userRole === "consumer" && (
                <Card>
                    {/* Subtitle */}
                    <h2 className="text-xl font-bold text-green-700 mb-4">
                        Reserve This Bundle
                    </h2>

                    <p className="text-gray-600 mb-4">
                        Reserve this bundle now to secure your pickup.
                        You&apos;ll receive a claim code to use when you collect
                        it.
                    </p>

                    {/* Depends on reservation status */}
                    {reservationSuccess ? (
                        // Reservation was a success:
                        <div className="text-center py-4">
                            <p className="text-green-600 font-semibold text-lg">
                                Reservation successful!
                            </p>
                        </div>
                    ) : hasReservedBundle(parseInt(id)) ? (
                        // Reservation was previously made:
                        (() => {
                            // Get reservation status
                            const reservation = getReservationForBundle(
                                parseInt(id),
                            );
                            const isCollected =
                                reservation?.status === "collected";

                            return (
                                <div className="text-center py-4">
                                    {isCollected ? (
                                        // If it has been collected
                                        <div
                                            className="w-full px-4 py-3 rounded-md
                                                       font-semibold text-lg text-blue-600 bg-blue-50
                                                       border border-blue-600"
                                        >
                                            Collected!
                                        </div>
                                    ) : (
                                        // If not collected, but active reservation
                                        <p className="font-semibold text-lg text-green-600">
                                            Reservation{" "}
                                            <span className="font-mono font-bold">
                                                #{reservation.reservation_id}
                                            </span>{" "}
                                            active
                                        </p>
                                    )}

                                    {/* Display the collection code */}
                                    {!isCollected &&
                                        reservation?.claim_code && (
                                            <p className="text-gray-600 mt-2">
                                                Your collection code:{" "}
                                                <span className="font-mono font-bold text-lg">
                                                    {reservation.claim_code}
                                                </span>
                                            </p>
                                        )}

                                    {!isCollected && reservation?.reservation_id && (
                                        <div className="mt-4">
                                            <Button
                                                onClick={() =>
                                                    navigate(
                                                        `/report-error?issueType=reservation&reservation_id=${reservation.reservation_id}&bundle_id=${id}`,
                                                    )
                                                }
                                            >
                                                Report This Reservation
                                            </Button>
                                        </div>
                                    )}
                                </div>
                            );
                        })()
                    ) : (
                        // Otherwise, able to make new reservation:
                        <Button onClick={handleReserve} disabled={reserving}>
                            {reserving ? "Reserving..." : "Reserve Bundle"}
                        </Button>
                    )}
                </Card>
            )}

            {/* Seller reservations section */}
            {userRole === "seller" && (
                <Card>
                    <div className="flex items-center justify-between mb-6">
                        {/* Subtitle */}
                        <h2 className="text-xl font-bold text-green-700 mb-4">
                            Active Reservations
                        </h2>

                        {/* Collect bundle link */}
                        <div className="">
                            <Button
                                onClick={() =>
                                    navigate(`/bundles/${id}/collect`)
                                }
                            >
                                Complete Collection
                            </Button>
                        </div>
                    </div>

                    {/* Depends on reservation status */}
                    {sellerReservations.length === 0 ? (
                        // No reservations
                        <p className="text-gray-600">
                            No active reservations for this bundle.
                        </p>
                    ) : (
                        <div className="space-y-3">
                            {renderReservations(sellerReservations)}
                        </div>
                    )}
                </Card>
            )}
        </div>
    );
}
