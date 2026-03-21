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
 * @param {(event: React.MouseEvent<HTMLButtonElement>) => void} [props.onClick]
 *          - Click event handler.
 * @param {string} [props.className=""] - Additional styling to give the button.
 * @param {string} [props.type="button"] - Button type (*e.g.* `button`, `submit`, `reset`).
 * @param {boolean} [props.disabled=false] - Whether the button is disabled.
 * @param {"default"|"danger"} [props.variant="default"] - Button style variant.
 *
 * @returns {JSX.Element} the styled button with inner text and click function.
 */
export default function Button({
    children,
    onClick,
    className = "",
    type = "button",
    disabled = false,
    variant = "default",
}) {
    const baseStyles =
        "w-full px-4 py-3 rounded-md font-semibold border focus:outline-none focus:ring-2";

    const variantStyles = {
        default: "text-green-700 hover:bg-green-50 border-green-600",
        danger: "text-red-600 hover:bg-red-50 border-red-600",
    };

    const disabledStyles = disabled
        ? "opacity-50 cursor-not-allowed"
        : "hover:scale-102 transition";

    return (
        <button
            type={type}
            onClick={onClick}
            disabled={disabled}
            className={`${baseStyles} ${variantStyles[variant]} ${disabledStyles} ${className}`}
        >
            {children}
        </button>
    );
}
