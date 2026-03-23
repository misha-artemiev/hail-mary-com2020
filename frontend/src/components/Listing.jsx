/**
 * Listing.jsx
 * @author Thomas Noakes
 */

import React from "react";

// Resources
import defaultListing from "../assets/default-listing.jpg";
import { useBundleImage } from "../hooks/useBundleImage";

/**
 * A reusable card for displaying a listing as a post.
 *
 * @param {Object} props
 * @param {string} props.title - The title of the listing post.
 * @param {Array<{ label: string, value: string | number }>} props.info
 *          - An array of label-value pairs of additional information.
 * @param {(event: React.MouseEvent<HTMLDivElement>) => void} props.onClick
 *          - Click event handler.
 * @param {React.ReactNode} props.children
 *          - Additional elements to add to the card.
 * @param {number} [props.bundleId]
 *          - Bundle ID for loading image from endpoint.
 *
 * @returns {JSX.Element} a card with a listing and any information.
 */
export default function Listing({ title, info, onClick, children, bundleId }) {
    const { imageUrl } = useBundleImage(bundleId);
    const imageSrc = imageUrl || defaultListing;
    return (
        <div
            className="bg-white border rounded-xl
                        shadow-sm hover:border-md
                        scale-100 hover:scale-102
                        transition cursor-pointer"
            onClick={onClick}
        >
            {/* Item image */}
            <img
                src={imageSrc}
                alt="title"
                className="w-full h-40 object-cover rounded-t-xl"
            />

            {/* TODO: add seller profile picture, if not on profile */}

            <div className="p-4 space-y-3">
                {/* Title */}
                <h2 className="text-lg font-semibold">{title}</h2>

                {/* Information */}
                <div className="space-y-1 text-sm text-gray-700">
                    {info.map(({ label, value }, index) => (
                        <p key={index}>
                            {label && (
                                <span className="font-semibold">{label}: </span>
                            )}
                            {value}
                        </p>
                    ))}
                </div>

                {/* Additional children, if present */}
                {children}
            </div>
        </div>
    );
}
