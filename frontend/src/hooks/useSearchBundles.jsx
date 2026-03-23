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
    const [totalPages, setTotalPages] = useState(1);
    const [currentPage, setCurrentPage] = useState(1);

    const [userLocation, setUserLocation] = useState({ lat: 0, lon: 0 });

    const search = useCallback(
        async (filters = {}, page = 1) => {
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
                    page: page,
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
                const bundles_list = Array.isArray(data) ? data[1] : data;
                const pages = Array.isArray(data) ? data[0] : 1;
                setListings(bundles_list || []);
                setTotalPages(pages || 1);
                setCurrentPage(page);
            } catch (err) {
                console.error(err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        },
        [userLocation],
    );

    const goToPage = useCallback(
        (page, filters = {}) => {
            if (page >= 1 && page <= totalPages) {
                setCurrentPage(page);
                search(filters, page);
            }
        },
        [totalPages, search],
    );

    const resetFilters = useCallback(
        (newFilters = {}) => {
            setCurrentPage(1);
            search(newFilters, 1);
        },
        [search],
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

                search({ lat, lon, maxDistance: 10 });
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

    return {
        listings,
        loading,
        error,
        search,
        userLocation,
        totalPages,
        currentPage,
        goToPage,
        resetFilters,
    };
}
