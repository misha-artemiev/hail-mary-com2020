/**
 * useSearchBundles.jsx
 * @author Misha Artemiev
 */

import { useState, useCallback, useEffect } from "react";

// Set the default base API route
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export default function useSearchBundles() {
    const [listings, setListings] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const [userLocation, setUserLocation] = useState({ lat: 0, lon: 0 });

    /**
     * Search function
     * Uses provided filters, but falls back to internal userLocation
     * if specific coordinates aren't passed in the arguments.
     */
    const search = useCallback(
        async (filters = {}) => {
            setLoading(true);
            setError(null);

            try {
                const searchLat =
                    filters.lat !== undefined ? filters.lat : userLocation.lat;
                const searchLon =
                    filters.lon !== undefined ? filters.lon : userLocation.lon;

                const payload = {
                    lat: searchLat,
                    lon: searchLon,
                    max_dist: filters.maxDistance
                        ? Number(filters.maxDistance)
                        : null,
                    max_price: filters.maxPrice
                        ? Number(filters.maxPrice)
                        : null,
                    seller_name: filters.restaurant || null,
                    allergens: (filters.allergens || []).map((a) =>
                        Number(a.value ?? a),
                    ),
                    categories: filters.category
                        ? [Number(filters.category)]
                        : [],
                };

                const response = await fetch(`${API_BASE_URL}/bundles/search`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });

                if (!response.ok) {
                    throw new Error("Failed to search bundles");
                }

                const data = await response.json();
                setListings(data);
            } catch (err) {
                console.error(err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        },
        [userLocation],
    );

    /**
     * Geolocation Effect
     * Runs once on mount to find the user.
     */
    useEffect(() => {
        if (!navigator.geolocation) {
            console.warn("Geolocation is not supported by your browser.");
            // We just run an initial search with default 0,0
            search({});
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                setUserLocation({ lat, lon });

                search({ lat, lon });
            },
            (err) => {
                console.warn("Location access denied or failed:", err.message);
                search({});
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0,
            },
        );
    }, []);

    return { listings, loading, error, search, userLocation };
}
