/**
 * Tabs.jsx
 * @author Ed Brown
 */

import React from "react";

/**
 * Reusable tabs navigation component.
 *
 * @param {Object} props
 * @param {Array<{id: string, label: string}>} props.tabs - Tab definitions.
 * @param {string} props.activeTab - The id of the currently active tab.
 * @param {(tabId: string) => void} props.onTabChange - Called when a tab is selected.
 * @param {string} [props.className=""] - Additional classes for the container.
 *
 * @returns {JSX.Element}
 */
export default function Tabs({ tabs, activeTab, onTabChange, className = "" }) {
    return (
        <div className={`flex space-x-2 border-b border-gray-200 ${className}`}>
            {tabs.map((tab) => (
                <button
                    key={tab.id}
                    type="button"
                    onClick={() => onTabChange(tab.id)}
                    className={`px-4 py-2 font-semibold transition ${
                        activeTab === tab.id
                            ? "text-green-700 border-b-2 border-green-700"
                            : "text-gray-600 hover:text-green-700"
                    }`}
                >
                    {tab.label}
                </button>
            ))}
        </div>
    );
}
