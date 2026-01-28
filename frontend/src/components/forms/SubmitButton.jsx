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
 *
 * @returns {JSX.Element} the styled button with inner text.
 */
export default function SubmitButton({ children }) {
    return (
        <button
            type="submit"
            className="w-full px-4 py-3 mt-4 rounded-md
                       text-white font-semibold
                       bg-green-600 hover:bg-green-700
                       focus:outline-none focus:ring-2 focus:ring-green-500"
        >
            {children}
        </button>
    );
}
