/**
 * useUser.jsx
 * @author Thomas Noakes
 */

import { useEffect, useState } from "react";

/**
 * Custom React hook for fetching and managing user data.
 *
 * @param {string} username - The name of the user to fetch.
 *
 * @returns {{ user: Object|null, loading: boolean }}
 *          the object of user data and/or loading state.
 *
 * ---
 * @example
 * const { user, loading } = useUser("john_doe");
 *
 * if (loading) return <Spinner />;
 * if (!user) return <NotFound />;
 * return <UserProfile user={user} />
 */
export function useUser(username) {
    // State object: stores the user information
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Fetch user information
    useEffect(() => {
        let cancelled = false;

        // TODO: get user information properly
        async function fetchUser() {
            // const res = await fetch(`/api/user/&{username}`);
            // const data = await res.json();
            // setUser(data);

            // TODO: REMOVE
            const data = {
                username: username,
                bio: "Selling quality items with fast delivery and trusted service.",
                activeSince: "1st Jan, 2026",
                streak: "2 Weeks",
                mealsSaved: "15",
                co2e: "15kg",
                // location: "Exeter, England",
                // openingHours: "9am-5pm daily",
                // role: "seller",
                // categories: ["Fast Food", "Tacos", "Mexican", "Spicy"],
            };

            if (!cancelled) {
                console.log("done");
                setUser(data);
                setLoading(false);
            }
        }

        fetchUser();

        return () => {
            cancelled = true;
        };
    }, [username]);

    // Exit with user information and loading status
    return { user, loading };
}
