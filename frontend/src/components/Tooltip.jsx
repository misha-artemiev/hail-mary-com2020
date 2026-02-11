/**
 * Tooltip.jsx
 * @author Thomas Noakes
 */

import React from "react";

/**
 * Shows a tooltip when hovered.
 *
 * @param {Object} props
 * @param {string} props.text - the text inside the tooltip.
 * @param {React.ReactNode} props.children
 *          - the elements to display the tooltip on (*i.e* an icon).
 *
 * @returns {JSX.Element} the icon with a tooltip on hover.
 */
export default function Tooltip({ text, children }) {
    return (
        <span className="relative group cursor-default">
            {/* Icon */}
            <span className="inline-block group-hover:scale-105 transition">
                {children}
            </span>

            {/* Tooltip */}
            <span
                className="absolute left-1/2 top-full -translate-x-1/2
                           px-3 py-1.5 mt-2 z-10
                           rounded-md bg-gray-900
                           text-sm text-white whitespace-nowrap
                           opacity-0 group-hover:opacity-100
                           scale-95 group-hover:scale-100
                           transition pointer-events-none"
            >
                {text}
            </span>
        </span>
    );
}
