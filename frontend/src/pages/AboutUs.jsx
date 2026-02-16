/**
 * AboutUs.jsx
 */

import React from "react";

// Components
import Card from "../components/Card";

/**
 * Displays project background and team overview.
 *
 * @returns {JSX.Element} the About Us page
 */
export default function AboutUs() {
    const values = [
        "Reduce food waste through affordable rescued bundles.",
        "Support local businesses with a simple redistribution channel.",
        "Help communities access low-cost food options.",
    ];

    return (
        <div className="max-w-5xl mx-auto p-6">
            <Card>
                <h1 className="text-3xl font-bold text-green-700 mb-2">
                    About Us
                </h1>
                <p className="text-gray-600">
                    Food Rescue connects surplus food from local sellers with
                    users who want quality meals at reduced prices.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    Our Mission
                </h2>
                <ul className="space-y-2 text-gray-700">
                    {values.map((value) => (
                        <li
                            key={value}
                            className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100"
                        >
                            {value}
                        </li>
                    ))}
                </ul>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    Team
                </h2>
                <p className="text-gray-700">
                    We are a student development team building practical tools
                    for sustainable food access and waste reduction.
                </p>
            </Card>
        </div>
    );
}
