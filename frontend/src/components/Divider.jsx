/**
 * Divider.jsx
 * @author Thomas Noakes, Ed Brown
 */

import React from "react";

/**
 * A reusable styled divider with customisable inner HTML (*i.e.* text).
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - Content to be rendered inside the button (*i.e.* text).
 *
 * @returns {JSX.Element} the styled divider with inner text.
 */
export default function Divider({ children }) {
    return (
        // Flex container
        <div className="flex items-center my-6">
            <div className="grow border-t border-gray-300" />

            {/* Text */}
            <span className="px-3 text-gray-500 text-sm">{children}</span>

            <div className="grow border-t border-gray-300" />
        </div>
    );
}
