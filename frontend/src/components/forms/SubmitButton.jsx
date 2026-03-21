/**
 * SubmitButton.jsx
 * @author Thomas Noakes
 */

import React from "react";

/**
 * Submit button for forms.
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - Content to be rendered inside the button (*i.e.* text).
 * @param {string} [props.className=""] - Additional styling to give the button.
 * @param {Function} [props.onClick] - Click event handler.
 *
 * @returns {JSX.Element} the styled button with inner text.
 */
export default function SubmitButton({ children, className = "", onClick }) {
    return (
        <button
            type="submit"
            onClick={onClick}
            className={`w-full px-4 py-3 mt-4 rounded-md
                       text-white font-semibold
                       bg-green-600 hover:bg-green-700
                       focus:outline-none focus:ring-2 focus:ring-green-500
                       ${className}`}
        >
            {children}
        </button>
    );
}
