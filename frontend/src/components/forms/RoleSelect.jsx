import React from "react";

export default function RoleSelect({ label, value, onChange, options }) {
    return (
        <div>
            <label className="block font-semibold text-gray-700">{label}</label>
            <select
                required
                value={value}
                onChange={onChange}
                className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
            >
                {options.map((option) => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </select>
        </div>
    );
}
