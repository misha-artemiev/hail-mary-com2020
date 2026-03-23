import { getAuthToken } from "../services/authService";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export function useSellerAnalytics() {
    const fetchGraphTypes = async () => {
        const token = getAuthToken();
        const response = await fetch(`${API_BASE_URL}/sellers/me/analytics`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        if (!response.ok) throw new Error("Failed to fetch graph types");
        return response.json();
    };

    const fetchGraph = async (graphTypeId) => {
        const token = getAuthToken();
        const response = await fetch(
            `${API_BASE_URL}/sellers/me/analytics/${graphTypeId}`,
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            },
        );
        if (!response.ok)
            throw new Error(`Failed to fetch graph ${graphTypeId}`);
        return response.json();
    };

    const refreshAnalytics = async () => {
        const token = getAuthToken();
        const response = await fetch(`${API_BASE_URL}/sellers/me/analytics`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        if (!response.ok) throw new Error("Failed to refresh analytics");
        return response.json();
    };

    const getCombinedTimelineData = async () => {
        const [actualData, forecastData] = await Promise.all([
            fetchGraph(1),
            fetchGraph(5),
        ]);

        const actualSales = actualData[1].find(
            (s) => s[0].series_name === "sales",
        );
        const actualPosted = actualData[1].find(
            (s) => s[0].series_name === "posted",
        );
        const forecastSales = forecastData[1].find(
            (s) => s[0].series_name === "sales",
        );
        const forecastPosted = forecastData[1].find(
            (s) => s[0].series_name === "posted",
        );

        const timelineMap = new Map();

        if (actualSales) {
            for (const point of actualSales[1]) {
                timelineMap.set(point.x, {
                    date: point.x,
                    actualSales: Number(point.y),
                    actualPosted: timelineMap.get(point.x)?.actualPosted || 0,
                });
            }
        }
        if (actualPosted) {
            for (const point of actualPosted[1]) {
                timelineMap.set(point.x, {
                    date: point.x,
                    actualSales: timelineMap.get(point.x)?.actualSales || 0,
                    actualPosted: Number(point.y),
                });
            }
        }
        if (forecastSales) {
            for (const point of forecastSales[1]) {
                timelineMap.set(point.x, {
                    date: point.x,
                    forecastSales: Number(point.y),
                    forecastPosted:
                        timelineMap.get(point.x)?.forecastPosted || 0,
                });
            }
        }
        if (forecastPosted) {
            for (const point of forecastPosted[1]) {
                timelineMap.set(point.x, {
                    date: point.x,
                    forecastSales: timelineMap.get(point.x)?.forecastSales || 0,
                    forecastPosted: Number(point.y),
                });
            }
        }

        return Array.from(timelineMap.values()).sort(
            (a, b) => new Date(a.date) - new Date(b.date),
        );
    };

    return {
        fetchGraphTypes,
        fetchGraph,
        refreshAnalytics,
        getCombinedTimelineData,
    };
}
