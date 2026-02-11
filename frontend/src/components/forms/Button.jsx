/**
 * Button.jsx
 * @author Thomas Noakes, Ed Brown
 */

import React from "react";

/**
 * A reusable styled button with customisable inner HTML (*i.e.* text) and click function.
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - Content to be rendered inside the button (*i.e.* text).
 * @param {(event: React.MouseEvent<HTMLButtonElement>) => void} props.onClick
 *          - Click event handler.
 * @param {string} [props.className=""] - Additional styling to give the button.
 *
 * @returns {JSX.Element} the styled button with inner text and click function.
 */
export default function Button({ children, onClick, className }) {
    return (
        <button
            onClick={onClick}
            className={`w-full px-4 py-3 rounded-md
                       text-green-700 font-semibold
                       hover:bg-green-50
                       border border-green-600
                       focus:outline-none focus:ring-2 focus:ring-green-50
                       ${className}`}
        >
            {children}
        </button>
    );
}
