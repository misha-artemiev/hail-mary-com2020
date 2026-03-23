/**
 * useUser.jsx
 * @author Thomas Noakes
 */

import { useEffect, useState } from "react";
import { getAuthToken } from "../services/authService";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Custom React hook for fetching and managing user data.
 *
 * @param {string} username - The name of the user to fetch.
 *
 * @returns {{ user: Object|null, loading: boolean, error: string|null }}
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
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!username) return;

        let cancelled = false;

        async function fetchUser() {
            setLoading(true);
            setError(null);

            try {
                const token = getAuthToken();
                const headers = token
                    ? { Authorization: `Bearer ${token}` }
                    : {};

                const idRes = await fetch(
                    `${API_BASE_URL}/users/id/${encodeURIComponent(username)}`,
                    { headers },
                );

                if (!idRes.ok) {
                    if (!cancelled) {
                        setError("User not found");
                        setLoading(false);
                    }
                    return;
                }

                const [userId, role] = await idRes.json();

                if (role === "seller") {
                    const sellerRes = await fetch(
                        `${API_BASE_URL}/sellers/${userId}`,
                        { headers },
                    );

                    if (!sellerRes.ok) {
                        if (!cancelled) {
                            setError("Failed to fetch seller data");
                            setLoading(false);
                        }
                        return;
                    }

                    const sellerData = await sellerRes.json();

                    if (!cancelled) {
                        setUser({
                            ...sellerData,
                            role: "seller",
                        });
                        setLoading(false);
                    }
                } else {
                    const consumerRes = await fetch(
                        `${API_BASE_URL}/consumers/${userId}`,
                        { headers },
                    );

                    if (!consumerRes.ok) {
                        if (!cancelled) {
                            setError("Failed to fetch consumer data");
                            setLoading(false);
                        }
                        return;
                    }

                    const consumerData = await consumerRes.json();

                    if (!cancelled) {
                        setUser({
                            ...consumerData,
                            role: "consumer",
                        });
                        setLoading(false);
                    }
                }
            } catch (err) {
                if (!cancelled) {
                    setError(err.message);
                    setLoading(false);
                }
            }
        }

        fetchUser();

        return () => {
            cancelled = true;
        };
    }, [username]);

    return { user, loading, error };
}
