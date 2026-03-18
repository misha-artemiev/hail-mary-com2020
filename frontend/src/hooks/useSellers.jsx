/**
 * useSellers.jsx
 * Custom hook for fetching all sellers for the dropdown
 */

import { useEffect, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export default function useSellers() {
    const [sellerOptions, setSellerOptions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let cancelled = false;

        async function fetchSellers() {
            const res = await fetch(`${API_BASE_URL}/sellers`);
            const data = await res.json();

            if (!cancelled) {
                const formattedSellers = data.map((seller) => ({
                    value: seller.seller_name,
                    label: seller.seller_name,
                }));

                setSellerOptions(
                    formattedSellers.sort((a, b) =>
                        a.label.localeCompare(b.label),
                    ),
                );
                setLoading(false);
            }
        }

        fetchSellers();

        return () => {
            cancelled = true;
        };
    }, []);

    return { sellerOptions, loading };
}
