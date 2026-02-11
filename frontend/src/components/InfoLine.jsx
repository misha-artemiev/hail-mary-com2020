/**
 * InfoLine.jsx
 * @author Thomas Noakes
 */

import React from "react";

/**
 * Displays a labelled information field.
 *
 * @param {Object} props
 * @param {string} props.label - The label to describe the value
 * @param {string | number} props.label - The value to display
 *
 * @returns {JSX.Element} a paragraph element containing the label and value
 */
export default function InfoLine({ label, value }) {
    return (
        <p className="text-gray-700 mb-2">
            <span className="font-semibold">{label}:</span> {value}
        </p>
    );
}
