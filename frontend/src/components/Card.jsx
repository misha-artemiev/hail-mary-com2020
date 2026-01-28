/**
 * Card.jsx
 * @author Thomas Noakes
 */

import React from "react";

/**
 * A container card for structuring main pages.
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - Content to be rendered inside the card.
 * @param {string} [props.className=""] - Additional styling to give the card.
 *
 * @returns {JSX.Element} a card container
 */
export default function Card({ children, className = "" }) {
    return (
        <div className={`bg-white shadow-md rounded-lg p-6 mb-2 ${className}`}>
            {children}
        </div>
    );
}
