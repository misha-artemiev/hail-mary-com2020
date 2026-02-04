/**
 * useUser.jsx
 * @author Thomas Noakes
 */

import { useEffect, useState } from "react";

export function useUser(username) {
    // State object: stores the user information
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(null);

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
                location: "Exeter, England",
                openingHours: "9am-5pm daily",
                role: "seller",
                categories: ["Fast Food", "Tacos", "Mexican", "Spicy"],
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
