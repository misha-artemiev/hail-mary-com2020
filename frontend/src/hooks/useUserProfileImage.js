import { useEffect, useState } from "react";
import { getAuthToken } from "../services/authService";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export function useUserProfileImage(username) {
    const [imageUrl, setImageUrl] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!username) return;

        let cancelled = false;
        let revoked = false;
        let currentUrl = null;

        async function fetchUserProfileImage() {
            setLoading(true);

            try {
                const token = getAuthToken();
                const headers = token
                    ? { Authorization: `Bearer ${token}` }
                    : {};

                const idResponse = await fetch(
                    `${API_BASE_URL}/users/id/${username}`,
                    { headers },
                );

                if (!idResponse.ok) {
                    if (!cancelled) {
                        setLoading(false);
                    }
                    return;
                }

                const [userId] = await idResponse.json();

                const imageResponse = await fetch(
                    `${API_BASE_URL}/users/${userId}/image`,
                    { headers },
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
