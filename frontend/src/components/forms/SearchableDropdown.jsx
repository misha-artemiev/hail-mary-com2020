/**
 * SearchableDropdown.jsx
 * A searchable dropdown that filters options as user types
 */

import React, { useState, useEffect, useRef } from "react";

export default function SearchableDropdown({
    value,
    onChange,
    options,
    placeholder,
    name,
}) {
    const [isOpen, setIsOpen] = useState(false);
    const [inputValue, setInputValue] = useState(value || "");
    const wrapperRef = useRef(null);

    useEffect(() => {
        setInputValue(value || "");
    }, [value]);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (
                wrapperRef.current &&
                !wrapperRef.current.contains(event.target)
            ) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () =>
            document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const filteredOptions = options.filter((opt) =>
        opt.label.toLowerCase().includes(inputValue.toLowerCase()),
    );

    const handleInputChange = (e) => {
        setInputValue(e.target.value);
        setIsOpen(true);
    };

    const handleSelect = (selectedValue, selectedLabel) => {
        setInputValue(selectedLabel);
        setIsOpen(false);
        onChange({
            target: { name, value: selectedValue },
        });
    };

    return (
        <div className="relative" ref={wrapperRef}>
            <div className="flex items-center">
                <input
                    type="text"
                    value={inputValue}
                    onChange={handleInputChange}
                    onFocus={() => setIsOpen(true)}
                    placeholder={placeholder || "Search..."}
                    className="w-full border rounded-md px-3 py-2 focus:ring-2
                               focus:ring-green-500 focus:outline-none"
                />
                <button
                    type="button"
                    onClick={() => setIsOpen(!isOpen)}
                    className="absolute right-1 px-2 py-1 rounded-md hover:bg-green-50 transition"
                >
                    <svg
                        className={`w-5 h-5 text-gray-400 transition
                                    ${isOpen ? "rotate-180" : ""}`}
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
            </div>

            {isOpen && filteredOptions.length > 0 && (
                <div className="absolute z-10 mt-1 w-full rounded-lg shadow-lg overflow-hidden border border-gray-200 bg-white">
                    <div className="max-h-48 overflow-y-auto">
                        {filteredOptions.map((opt) => (
                            <div
                                key={opt.value}
                                onClick={() =>
                                    handleSelect(opt.value, opt.label)
                                }
                                className="px-4 py-2.5 cursor-pointer text-sm hover:bg-green-100 border-b border-gray-100 last:border-b-0"
                            >
                                {opt.label}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {isOpen && inputValue && filteredOptions.length === 0 && (
                <div className="absolute z-10 mt-1 w-full rounded-lg shadow-lg border border-gray-200 bg-white px-4 py-2.5 text-sm text-gray-500">
                    No results found
                </div>
            )}
        </div>
    );
}
