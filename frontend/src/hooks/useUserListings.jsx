/**
 * useUserListings.jsx
 * @author Thomas Noakes
 */

import { useEffect, useState } from "react";

/**
 * Custom React hook for fetching user's listings
 *
 * @param {string} username - The name of the user to fetch listings for.
 *
 * @returns {Array<Object>|null} the array of listings objects.
 *
 * ---
 * @example
 * const listings = useUserListings("seller_123");
 *
 * if (!listings) return <Loading />;
 * return <ListingsGrid listings={listings} />;
 */
export function useUserListings(username) {
    // State object: stores the listing information
    const [listings, setListings] = useState(null);

    // Fetch user listings
    useEffect(() => {
        // TODO: get user listings properly
        async function fetchListings() {
            // const res = await fetch(`/api/listings?user=&{username}`);
            // const data = await res.json();
            // setListings(data);

            // TODO: remove
            setListings([
                {
                    title: "Item 1",
                    image: "",
                    info: [
                        { label: "Pickup", value: "13:00-15:00" },
                        { label: "", value: "3 left" },
                    ],
                },
                {
                    title: "Item 2",
                    image: "",
                    info: [
                        { label: "Pickup", value: "09:00-10:00" },
                        { label: "", value: "Collection only" },
                    ],
                },
                {
                    title: "Item 3",
                    image: "",
                    info: [{ label: "Pickup", value: "13:00-15:00" }],
                },
            ]);
        }

        fetchListings();
    }, [username]);

    // Exit with user listings
    return listings;
}
