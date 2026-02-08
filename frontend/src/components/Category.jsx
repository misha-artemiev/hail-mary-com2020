/**
 * Category.jsx
 * @author Thomas Noakes
 */

import React from "react";

/**
 * A styled 'pill' for displaying categories. With optional click event.
 *
 * @param {Object} props
 * @param {boolean} [props.selected=false] - Whether the category is selected.
 * @param {(event: React.MouseEvent<HTMLSpanElement>) => void} props.onClick
 *          - Click event handler.
 * @param {React.ReactNode} props.children - The content of the pill (*i.e.* text).
 *
 * @returns {JSX.Element} a styled category pill.
 */
export default function Category({ selected = false, onClick, children }) {
    return (
        <span
            onClick={onClick}
            className={`
                px-3 py-1 rounded-full
                text-sm font-medium
                cursor-pointer select-none
                transition
                ${
                    selected
                        ? "bg-green-600 text-white"
                        : "bg-green-100 text-green-700 hover:bg-green-200"
                }
            `}
        >
            {children}
        </span>
    );
}
