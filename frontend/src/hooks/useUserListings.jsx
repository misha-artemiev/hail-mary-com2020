/**
 * useUserListings.jsx
 * @author Thomas Noakes
 */

import { useEffect, useState } from "react";

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
