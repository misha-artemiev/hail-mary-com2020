/**
 * DeveloperProfile.jsx
 * @author Ed Brown
 */

import React from "react";

// Components
import Card from "../components/Card";

// Resources
import defaultProfile from "../assets/default-user.jpg";

export default function DeveloperProfile() {
    const dev_list = [
        {
            type: "TODO",
            message: "Edit profile functionality with backend"
        },
        {
            type: "In progress",
            message: "User profile page + progress tracking"
        },
        {
            type: "TODO",
            message: "Bundle product page"
        },
        {
            type: "TODO",
            message: "Connect endpoints 1.0"
        },
        {
            type: "TODO",
            message: "Documentation sections 1-4"
        }
    ];

    return (
        <div className="max-w-3xl mx-auto p-4">
            <Card>
                <div className="flex items-center space-x-4">
                    {/* Header */}
                    <h1 className="text-3xl items-center justify-between mb-6">
                        Dev Profile
                    </h1>

                    {/* Profile Picture */}
                    <img
                        src={defaultProfile}
                        alt="Profile"
                        className="w-32 h-32 rounded-full mb-4 mx-auto"
                    />
                </div>
            </Card>

            {/* DevList Container */}
            <Card>
                {/* DevList Header */}
                <h2 className="text-2xl font-bold mb-4 text-green-700">
                    Dev TODO List
                </h2>
                {/* DevList Items */}
                <ul className="space-y-3">
                    {dev_list.map((item, index) => (
                        <li key={index} className="border-1-4 border-green-500 pl-4 py-2 bg-gray-50 rounded">
                            <p className="font-semibold text-gray-800">
                                {item.type}
                            </p>
                            <p className="text-gray-600">
                                {item.message}
                            </p>
                        </li>
                    ))}
                </ul>
            </Card>
        </div>
    )
}