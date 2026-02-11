/**
 * useListings.jsx
 * @author Thomas Noakes
 */

import { useEffect, useState } from "react";

/**
 * Custom React hook for fetching all listings.
 */
export default function useListings() {
    // State object: stores the listings
    const [listings, setListings] = useState(null);
    const [loading, setLoading] = useState(true);

    // Fetch listings information
    useEffect(() => {
        let cancelled = false;

        // TODO: get listings information properly
        async function fetchListings() {
            // const res = await fetch("/api/bundles/");
            // const data = await res.json;
            // setListings(data);

            // TODO: REMOVE
            const data = [
                {
                    id: 1,
                    title: "Fresh Bagels",
                    image: "",
                    info: [
                        { value: "£2.50" },
                        { value: "Pack of 4" },
                        { label: "Pickup available", value: "4pm-5pm" },
                    ],
                    footer: "Best before today",
                },
                {
                    id: 2,
                    title: "Sandwich Platter",
                    image: "",
                    info: [
                        { value: "£5.00" },
                        { label: "Variety", value: "Mixed" },
                        { label: "Pickup available", value: "10am-12pm" },
                    ],
                    footer: "Vegetarian options available!",
                },
                {
                    id: 3,
                    title: "Pizza Slice",
                    image: "",
                    info: [
                        { value: "£1.50" },
                        { label: "Pickup available", value: "6pm-7pm" },
                    ],
                },
            ];

            if (!cancelled) {
                setListings(data);
                setLoading(false);
            }
        }

        fetchListings();

        return () => {
            cancelled = true;
        };
    }, []);

    // Exit with listings information and loading status
    return { listings, loading };
}
