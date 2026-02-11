/**
 * FormInput.jsx
 * @author Thomas Noakes
 */

import React from "react";

/**
 * Controlled form input with labels and optional required indicator.
 *
 * @param {Object} props
 * @param {string} props.label - Text to be displayed for the field.
 * @param {string} props.name - The name (and ID) of the `input` element.
 * @param {string} [props.type="text"] - Input type (*e.g.* `text`, `email`, `password`, ...).
 * @param {string | number} props.value - The current input value.
 * @param {string | number} [props.placeholder=""] - The placeholder value.
 * @param {(event: React.ChangeEvent<HTMLInputElement>) => void} props.onChange
 *          - The change event handler.
 * @param {boolean} [props.required="false"] - Whether the input is required
 *
 * @returns {JSX.Element} a labelled input field.
 */
export default function FormInput({
    label,
    name,
    type = "text",
    value,
    placeholder = "",
    onChange,
    required = false,
}) {
    return (
        <div>
            {/* Label */}
            {label && (
                <label
                    htmlFor="{name}"
                    className="block font-semibold text-gray-700 mb-1"
                >
                    {label}

                    {/* Required 'star' */}
                    {required && <span className="text-red-500"> *</span>}
                </label>
            )}

            {/* Input field */}
            <input
                id={name}
                type={type}
                name={name}
                required={required}
                value={value}
                placeholder={placeholder}
                onChange={onChange}
                className="w-full border rounded-md px-3 py-2 focus:ring-2
                           focus:ring-green-500 focus:outline-none"
            />
        </div>
    );
}
