import React from "react";

export default function Card({ children }) {
    return (
        <div className="bg-white shadow-md rounded-lg p-6 mb-2">{children}</div>
    );
}
