/**
 * Analysis.jsx
 * @Author Noe Bouchard
 */

import React from "react";

// Components
import Card from "../components/Card";
import useSellerAnalyticsGraphs from "../hooks/useSellerAnalyticsGraphs";

/**
 * Displays analytics placeholders for upcoming graph integrations.
 *
 * @returns {JSX.Element} the analysis page
 */
export default function Analysis() {
    const { graphs, reportPeriod, sellerUserId, loading, error } =
        useSellerAnalyticsGraphs();

    return (
        <div className="max-w-6xl mx-auto p-6">
            <Card>
                <h1 className="text-3xl font-bold text-green-700 mb-2">
                    Analysis
                </h1>
                <p className="text-gray-600">Weekly seller performance graphs.</p>
                {sellerUserId !== null && (
                    <p className="text-sm text-gray-500 mt-2">
                        Showing data for seller: {sellerUserId}
                    </p>
                )}
                {reportPeriod && (
                    <p className="text-sm text-gray-500 mt-2">
                        Report week: {reportPeriod}
                    </p>
                )}
            </Card>

            {loading && <Card>Loading analytics graphs...</Card>}

            {error && (
                <Card className="text-red-700 bg-red-50 border border-red-200">
                    {error}
                </Card>
            )}

            {!loading && !error && graphs.length === 0 && (
                <Card>No graph data is currently available.</Card>
            )}

            {!loading && !error && graphs.length > 0 && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {graphs.map((graph) => (
                        <Card key={graph.key}>
                            <h2 className="text-xl font-semibold text-gray-700 mb-4">
                                {graph.title}
                            </h2>
                            <img
                                src={graph.image_data_url}
                                alt={graph.title}
                                className="w-full h-auto rounded-md border border-gray-200"
                            />
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}
