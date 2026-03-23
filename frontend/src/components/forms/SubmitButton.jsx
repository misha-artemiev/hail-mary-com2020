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
 * @param {boolean} [props.disabled=false] - Whether the button is disabled.
 * @param {string} [props.className=""] - Additional styling to give the button.
 *
 * @returns {JSX.Element} the styled button with inner text.
 */
export default function SubmitButton({
    children,
    disabled = false,
    className = "",
}) {
    const disabledStyles = disabled
        ? "opacity-50 cursor-not-allowed"
        : "hover:bg-green-700";

    return (
        <button
            type="submit"
            disabled={disabled}
            className={`w-full px-4 py-3 mt-4 rounded-md
                       text-white font-semibold
                       bg-green-600 ${disabledStyles}
                       focus:outline-none focus:ring-2 focus:ring-green-500
                       ${className}`}
        >
            {children}
        </button>
    );
}
