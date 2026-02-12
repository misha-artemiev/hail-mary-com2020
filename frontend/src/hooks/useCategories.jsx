/**
 * useCategories.jsx
 * @author Misha Artemiev
 */

import { useEffect, useState } from "react";

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
            const res = await fetch("/api/categories");
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
