import { useEffect, useState } from "react";

import { getAuthToken } from "../services/authService";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Loads analytics graphs for the authenticated seller account.
 *
 * @returns {{
 *   graphs: Array<{key: string, title: string, image_data_url: string}>,
 *   reportPeriod: string | null,
 *   loading: boolean,
 *   error: string | null
 * }}
 */
export default function useSellerAnalyticsGraphs() {
    const [graphs, setGraphs] = useState([]);
    const [reportPeriod, setReportPeriod] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadGraphs = async () => {
            const token = getAuthToken();
            if (!token) {
                setError("You must be signed in as a seller to view analytics.");
                setLoading(false);
                return;
            }

            try {
                const response = await fetch(
                    `${API_BASE_URL}/sellers/me/analytics/graphs`,
                    {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    },
                );

                if (!response.ok) {
                    if (response.status === 401) {
                        throw new Error(
                            "Only seller accounts can access analytics.",
                        );
                    }
                    if (response.status === 404) {
                        throw new Error(
                            "No analytics data has been generated yet.",
                        );
                    }
                    throw new Error("Failed to load analytics graphs.");
                }

                const data = await response.json();
                setGraphs(data.graphs || []);
                setReportPeriod(data.report_period || null);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        loadGraphs();
    }, []);

    return { graphs, reportPeriod, loading, error };
}
