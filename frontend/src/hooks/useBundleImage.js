import { useEffect, useState } from "react";

export function useBundleImage(bundleId) {
    const [imageUrl, setImageUrl] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!bundleId) return;

        let cancelled = false;
        let revoked = false;
        let currentUrl = null;

        async function fetchBundleImage() {
            setLoading(true);

            try {
                const imageResponse = await fetch(
                    `${import.meta.env.VITE_API_BASE_URL || "/api"}/bundles/${bundleId}/image`,
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

        fetchBundleImage();

        return () => {
            cancelled = true;
            if (revoked && currentUrl) {
                URL.revokeObjectURL(currentUrl);
            }
        };
    }, [bundleId]);

    return { imageUrl, loading };
}
