import React from "react";

export default function Divider({ text }) {
    return (
        <div className="flex items-center my-6">
            <div className="flex-grow border-t border-gray-300" />
            <span className="px-3 text-gray-500 text-sm">{text}</span>
            <div className="flex-grow border-t border-gray-300" />
        </div>
    );
}
