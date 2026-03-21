/**
 * AdminsTable.jsx
 */

import React from "react";

export default function AdminsTable({ admins, onRowClick, onToggleStatus }) {
    return (
        <div className="overflow-x-auto mt-6">
            <table className="w-full">
                <thead>
                    <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">
                            Username
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">
                            Email
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">
                            Status
                        </th>
                        <th className="text-right py-3 px-4 font-semibold text-gray-700">
                            Actions
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {admins.map((admin) => (
                        <tr
                            key={admin.user_id}
                            className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
                            onClick={() => onRowClick(admin)}
                        >
                            <td className="py-3 px-4">
                                {admin.username}
                            </td>
                            <td className="py-3 px-4">
                                {admin.email}
                            </td>
                            <td className="py-3 px-4">
                                <span
                                    className={`px-2 py-1 rounded text-sm ${
                                        admin.active
                                            ? "bg-green-100 text-green-700"
                                            : "bg-red-100 text-red-700"
                                    }`}
                                >
                                    {admin.active
                                        ? "Active"
                                        : "Inactive"}
                                </span>
                            </td>
                            <td
                                className="py-3 px-4 text-right"
                                onClick={(e) => e.stopPropagation()}
                            >
                                <button
                                    onClick={() =>
                                        onToggleStatus(admin.user_id, admin.active)
                                    }
                                    className={`px-3 py-1 rounded text-sm ${
                                        admin.active
                                            ? "bg-red-100 text-red-700 hover:bg-red-200"
                                            : "bg-green-100 text-green-700 hover:bg-green-200"
                                    }`}
                                >
                                    {admin.active
                                        ? "Deactivate"
                                        : "Activate"}
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
