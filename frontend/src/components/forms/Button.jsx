import React from "react";

export default function Button({ children, onClick }) {
    return (
        <button
            onClick={onClick}
            className="w-full px-4 py-3 rounded-md
                       text-green-700 font-semibold
                       hover:bg-green-50
                       border border-green-600
                       focus:outline-none focus:ring-2 focus:ring-green-50"
        >
            {children}
        </button>
    );
}
