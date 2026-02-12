/**
 * useAllergens.jsx
 * @author Misha Artemiev
 */

import { useEffect, useState } from "react";

/**
 * Custom React hook for fetching all allergens.
 */
export default function useAllergens() {
    // State object: stores the allergens
    const [allergenOptions, setAllergenOptions] = useState([]);
    const [loading, setLoading] = useState(true);

    // Fetch allergens information
    useEffect(() => {
        let cancelled = false;

        async function fetchAllergens() {
            const res = await fetch("/api/allergens");
            const data = await res.json();

            if (!cancelled) {
                const formattedAllergens = data.map((allergen) => ({
                        value: allergen.allergen_id,
                        label: allergen.allergen_name
                    }));

                setAllergenOptions(formattedAllergens);
                setLoading(false);
            }
        }

        fetchAllergens();

        return () => {
            cancelled = true;
        };
    }, []);

    // Exit with allergens information and loading status
    return { allergenOptions, loading };
}
