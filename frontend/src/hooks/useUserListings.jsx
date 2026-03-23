/**
 * useUserListings.jsx
 * @author Thomas Noakes
 */

import { useEffect, useState } from "react";

/**
 * Custom React hook for fetching user's listings
 *
 * Note: The backend doesn't expose public endpoints for viewing other users'
 * bundles or reservations, so this returns null/empty listings.
 *
 * @param {string} username - The name of the user to fetch listings for.
 * @param {string} userRole - The role of the user (seller or consumer).
 * @param {number} userId - The ID of the user.
 *
 * @returns {{ listings: Array<Object>|null, loading: boolean, error: string|null }}
 *          the listings and loading state.
 *
 * ---
 * @example
 * const { listings, loading } = useUserListings("seller_123", "seller", 1);
 *
 * if (loading) return <Loading />;
 * return <ListingsGrid listings={listings} />;
 */
export function useUserListings(username, userRole, userId) {
    const [listings, setListings] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!username || !userRole || !userId) {
            setListings(null);
            setLoading(false);
            return;
        }

        setLoading(true);

        setTimeout(() => {
            setListings([]);
            setLoading(false);
        }, 100);
    }, [username, userRole, userId]);

    return { listings, loading };
}
