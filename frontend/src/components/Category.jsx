/**
 * Category.jsx
 * @author Thomas Noakes
 */

import React from "react";

/**
 * A styled 'pill' for displaying categories. With optional click event.
 *
 * @param {Object} props
 * @param {(event: React.MouseEvent<HTMLSpanElement>) => void} props.onClick
 *          - Click event handler.
 * @param {React.ReactNode} props.children - The content of the pill (*i.e.* text).
 *
 * @returns {JSX.Element} a styled category pill.
 */
export default function Category({ onClick, children }) {
    return (
        <span
            className="px-3 py-1 rounded-full
                       text-sm font-medium text-green-700
                       bg-green-100 hover:bg-green-200
                       transition"
            onClick={onClick}
        >
            {children}
        </span>
    );
}
