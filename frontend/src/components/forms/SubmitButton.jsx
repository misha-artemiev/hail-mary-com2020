import React from "react";

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
