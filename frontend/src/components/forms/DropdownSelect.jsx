/**
 * DropdownSelect.jsx
 * @author Thomas Noakes
 */

import React, { useState, useEffect, useRef } from "react";

/**
 * A dropdown menu that allows choosing toggling given options.
 *
 * @param {Object} props
 * @param {Array<{ value: string, label: string }>} props.options
 *          - List of selectable options.
 * @param {string[]} props.value - List of currently selected values.
 * @param {string} props.name - Description text (*i.e.* type) to give the button.
 * @param {(event: React.ChangeEvent<HTMLButtonElement>) => void} props.onChange
 *          - Change event handler.
 *
 * @returns {JSX.Element} a dropdown select area.
 */
export default function DropdownSelect({ options, value, name, onChange }) {
    // State object: if the dropdown is open
    const [open, setOpen] = useState(false);

    // Reference object to the the dropdown
    const dropdownRef = useRef(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (
                dropdownRef.current &&
                !dropdownRef.current.contains(event.target)
            ) {
                setOpen(false);
            }
        };

        // Once opened, start listening for clicks outside
        if (open) {
            document.addEventListener("mousedown", handleClickOutside);
        }

        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [open]);

    const toggle = (v) => {
        onChange(
            // Converts objects to list of values
            value.includes(v)
                ? value.filter((x) => x !== v) // Remove if present
                : [...value, v], // Add if not present
        );
    };

    return (
        <div className="relative" ref={dropdownRef}>
            {/* Open button */}
            <button
                type="button"
                onClick={() => setOpen(!open)}
                className="w-full border rounded-md px-3 py-2 flex items-center justify-between
                           hover:bg-green-50 transition
                           focus:ring-2 focus:ring-green-500 focus:outline-none"
            >
                {value.length > 0
                    ? `${value.length} ${name}${value.length === 1 ? "" : "s"} selected`
                    : `Select ${name} options`}

                {/* Spinning arrow */}
                <svg
                    className={`w-5 h-5 text-gray-400 transition
                                ${open ? "rotate-180" : ""}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 9l-7 7-7-7"
                    />
                </svg>
            </button>

            {/* Dropdown menu */}
            {open && (
                <div
                    className="absolute z-10 mt-2
                               w-full rounded-lg shadow-lg overflow-hidden
                               border border-gray-200 bg-white
                               animate-in"
                >
                    {/* Extra div to cap size, enables scrolling */}
                    <div className="max-h-60 overflow-y-auto">
                        {options.map((opt) => (
                            <label
                                key={opt.value}
                                className="flex items-center gap-3 px-4 py-2.5
                                           cursor-pointer text-sm
                                           hover:bg-green-100 transition
                                           border-b border-gray-100 last:border-b-0"
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
                </div>
            )}
        </div>
    );
}
