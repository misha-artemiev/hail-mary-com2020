/**
 * DropdownSelect.jsx
 * @author Thomas Noakes
 */

import React, { useState } from "react";

/**
 * A dropdown menu that allows choosing toggling given options.
 *
 * @param {Object} props
 * @param {Array<{ value: string, label: string }>} props.options
 *          - List of selectable options.
 * @param {string[]} props.value - List of currently selected values.
 * @param {(event: React.ChangeEvent<HTMLButtonElement>) => void} props.onChange
 *          - Change event handler.
 *
 * @returns {JSX.Element} a dropdown select area.
 */
export default function DropdownSelect({ options, value, onChange }) {
    // State object: if the dropdown is open
    const [open, setOpen] = useState(false);

    const toggle = (v) => {
        onChange(
            // Converts objects to list of values
            value.includes(v)
                ? value.filter((x) => x !== v) // Remove if present
                : [...value, v], // Add if not present
        );
    };

    return (
        <div className="relative">
            {/* Open button */}
            <button
                type="button"
                onClick={() => setOpen(!open)}
                className="w-full border rounded-md px-3 py-2 flex items-center justify-between
                           hover:bg-green-50 transition
                           focus:ring-2 focus:ring-green-500 focus:outline-none"
            >
                {value.length > 0
                    ? `${value.length} selected`
                    : `Select options`}
            </button>

            {/* Dropdown menu */}
            {open && (
                <div className="absolute z-10 mt-2 w-full rounded-lg shadow-lg">
                    {options.map((opt) => (
                        <label
                            key={opt.value}
                            className="flex items-center gap-3 px-4 py-2.5 cursor-pointer text-sm"
                        >
                            {/* Checkbox */}
                            <input
                                type="checkbox"
                                checked={value.includes(opt.value)}
                                onChange={() => toggle(opt.value)}
                                className="h-4 w-4 accent-green-400"
                            />
                            {opt.label}
                        </label>
                    ))}
                </div>
            )}
        </div>
    );
}
