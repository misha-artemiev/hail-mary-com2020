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

        const actualSales = actualData[1]?.find(
            (s) => s[0].series_name === "sales",
        );
        const actualPosted = actualData[1]?.find(
            (s) => s[0].series_name === "posted",
        );
        const forecastSales = forecastData[1]?.find(
            (s) => s[0].series_name === "sales",
        );
        const forecastPosted = forecastData[1]?.find(
            (s) => s[0].series_name === "posted",
        );

        const timelineMap = new Map();

        if (actualSales) {
            for (const point of actualSales[1]) {
                const existing = timelineMap.get(point.x) || { date: point.x };
                existing.actualSales = Number(point.y);
                timelineMap.set(point.x, existing);
            }
        }
        if (actualPosted) {
            for (const point of actualPosted[1]) {
                const existing = timelineMap.get(point.x) || { date: point.x };
                existing.actualPosted = Number(point.y);
                timelineMap.set(point.x, existing);
            }
        }
        if (forecastSales) {
            for (const point of forecastSales[1]) {
                const existing = timelineMap.get(point.x) || { date: point.x };
                existing.forecastSales = Number(point.y);
                timelineMap.set(point.x, existing);
            }
        }
        if (forecastPosted) {
            for (const point of forecastPosted[1]) {
                const existing = timelineMap.get(point.x) || { date: point.x };
                existing.forecastPosted = Number(point.y);
                timelineMap.set(point.x, existing);
            }
        }

        const sortedData = Array.from(timelineMap.values()).sort(
            (a, b) => new Date(a.date) - new Date(b.date),
        );

        const today = new Date().toISOString().split("T")[0];
        
        let lastActualDate = null;
        let firstForecastDate = null;

        for (const item of sortedData) {
            if (item.date <= today && item.actualSales !== undefined) {
                lastActualDate = item.date;
            }
            if (item.date >= today && item.forecastSales !== undefined && !firstForecastDate) {
                firstForecastDate = item.date;
            }
        }

        if (lastActualDate && firstForecastDate && lastActualDate !== firstForecastDate) {
            const insertIndex = sortedData.findIndex(item => item.date === firstForecastDate);
            if (insertIndex !== -1) {
                const existing = sortedData[insertIndex];
                existing.actualSales = existing.forecastSales;
                existing.actualPosted = existing.forecastPosted;
            }
        }

        return sortedData;
    };

    return {
        fetchGraphTypes,
        fetchGraph,
        refreshAnalytics,
        getCombinedTimelineData,
    };
}
