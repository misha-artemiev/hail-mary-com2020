/**
 * RoleSelect.jsx
 * @author Thomas Noakes
 */

import React from "react";

/**
 * Select input for choosing a role type from a list of options.
 *
 * @param {Object} props
 * @param {string} props.label - Text to be displayed for the input.
 * @param {string} props.value - Currently selected value.
 * @param {(event: React.ChangeEvent<HTMLSelectElement>) => void} props.onChange
 *          - The change event handler.
 * @param {Array<{ value: string, label: string }>} props.options
 *          - The list of selectable options.
 *
 * @returns {JSX.Element} a styled select field.
 */
export default function RoleSelect({
    label,
    value,
    onChange,
    options,
    required = false,
}) {
    return (
        <div>
            {/* Label */}
            <label className="block font-semibold text-gray-700">
                {label}
                {required && <span className="text-red-500"> *</span>}
            </label>
            <select
                required
                value={value}
                onChange={onChange}
                className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
            >
                {/* Dynamically create options from list */}
                {options.map((option) => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </select>
        </div>
    );
}
