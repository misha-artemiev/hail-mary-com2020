import { useEffect, useState } from "react";
import { getAuthToken } from "../services/authService";

export function useUserImage() {
    const [imageUrl, setImageUrl] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        let cancelled = false;
        let revoked = false;
        let currentUrl = null;

        async function fetchUserImage() {
            const token = getAuthToken();
            if (!token) return;

            setLoading(true);

            try {
                const response = await fetch(
                    `${import.meta.env.VITE_API_BASE_URL || "/api"}/users/me/image`,
                    {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    },
                );
                if (response.ok) {
                    const blob = await response.blob();
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

        fetchUserImage();

        return () => {
            cancelled = true;
            if (revoked && currentUrl) {
                URL.revokeObjectURL(currentUrl);
            }
        };
    }, []);

    return { imageUrl, loading };
}
