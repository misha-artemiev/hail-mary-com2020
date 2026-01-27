import React from "react";

export default function FormInput({
    label,
    name,
    type = "text",
    value,
    onChange,
    required = false,
}) {
    return (
        <div>
            {/* Label */}
            <label
                htmlFor="{name}"
                className="block font-semibold text-gray-700 mb-1"
            >
                {label}
                {/* Required 'star' */}
                {required && <span className="text-red-500"> *</span>}
            </label>

            {/* Input field */}
            <input
                id={name}
                type={type}
                name={name}
                required={required}
                value={value}
                onChange={onChange}
                className="w-full border rounded-md px-3 py-2 focus:ring-2
                           focus:ring-green-500 focus:outline-none"
            />
        </div>
    );
}
