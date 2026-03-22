import { useEffect, useState } from "react";
import { getAuthToken } from "../services/authService";

export function useUserProfileImage(username) {
    const [imageUrl, setImageUrl] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!username) return;

        let cancelled = false;
        let revoked = false;
        let currentUrl = null;

        async function fetchUserProfileImage() {
            const token = getAuthToken();
            if (!token) {
                setLoading(false);
                return;
            }

            setLoading(true);

            try {
                const idResponse = await fetch(
                    `${import.meta.env.VITE_API_BASE_URL || "/api"}/users/id/${username}`,
                    {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    },
                );

                if (!idResponse.ok) {
                    setLoading(false);
                    return;
                }

                const [userId, role] = await idResponse.json();

                const imageResponse = await fetch(
                    `${import.meta.env.VITE_API_BASE_URL || "/api"}/users/${userId}/image`,
                    {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    },
                );

                if (imageResponse.ok) {
                    const blob = await imageResponse.blob();
                    const url = URL.createObjectURL(blob);
                    currentUrl = url;
                    if (!cancelled) {
                        setImageUrl(url);
                    } else {
                        revoked = true;
                        URL.revokeObjectURL(url);
                    }
                }
            } catch {
                // Keep imageUrl as null to use default
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        }

        fetchUserProfileImage();

        return () => {
            cancelled = true;
            if (revoked && currentUrl) {
                URL.revokeObjectURL(currentUrl);
            }
        };
    }, [username]);

    return { imageUrl, loading };
}