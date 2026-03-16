/**
 * Analytics.jsx
 * @author Thomas Noakes
 */

import React from "react";

// Components
import Card from "../components/Card";

// Images
import img1 from "../assets/analysis_sell_rate_capacity.png";
import img2 from "../assets/analysis_top_categories.png";
import img3 from "../assets/analysis_top_time_windows.png";

export default function Analytics() {
    return (
        <div className="max-w-4xl mx-auto p-4 md:p-6">
            <Card>
                {/* Header */}
                <h1 className="text-3xl font-bold text-green-700 mb-6 text-center">
                    Analytics
                </h1>

                {/* Images */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-8">
                    <img
                        src={img1}
                        alt="title"
                        className="w-full h-full object-cover border"
                    />
                    <img
                        src={img2}
                        alt="title"
                        className="w-full h-full object-cover border"
                    />
                    <img
                        src={img3}
                        alt="title"
                        className="w-full h-full object-cover border"
                    />
                </div>
            </Card>
        </div>
    );
}
