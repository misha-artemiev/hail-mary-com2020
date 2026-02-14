/**
 * useCategories.jsx
 * @author Misha Artemiev
 */

import { useEffect, useState } from "react";

// Set the default base API route
const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

/**
 * Custom React hook for fetching all categories.
 */
export default function useAllergens() {
    // State object: stores the allergens
    const [categoryOptions, setCategoryOptions] = useState([]);
    const [loading, setLoading] = useState(true);

    // Fetch category information
    useEffect(() => {
        let cancelled = false;

        async function fetchCategories() {
            const res = await fetch(`${API_BASE_URL}/categories/`);
            const data = await res.json();

            if (!cancelled) {
                const formattedCategories = data.map((category) => ({
                    value: category.category_id,
                    label: category.category_name,
                }));

                setCategoryOptions(formattedCategories);
                setLoading(false);
            }
        }

        fetchCategories();

        return () => {
            cancelled = true;
        };
    }, []);

    // Exit with categories information and loading status
    return { categoryOptions, loading };
}
