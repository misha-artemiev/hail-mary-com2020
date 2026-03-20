import { useState, useEffect } from "react";
import { getAuthToken } from "../services/authService";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export function useSellerAllReservations(bundles) {
    const [allReservations, setAllReservations] = useState([]);

    useEffect(() => {
        async function fetchAllReservations() {
            if (!bundles || bundles.length === 0) {
                return;
            }

            const token = getAuthToken();
            if (!token) {
                return;
            }

            const allRes = [];
            try {
                for (const bundle of bundles) {
                    const response = await fetch(
                        `${API_BASE_URL}/sellers/me/bundles/${bundle.bundle_id}/reservations`,
                        {
                            headers: {
                                Authorization: `Bearer ${token}`,
                            },
                        },
                    );
                    if (response.ok) {
                        const data = await response.json();
                        allRes.push(
                            ...data.map((r) => ({
                                ...r,
                                bundle_name: bundle.bundle_name,
                            })),
                        );
                    }
                }
                setAllReservations(allRes);
            } catch (err) {
                console.error(err.message);
            }
        }

        fetchAllReservations();
    }, [bundles]);

    return allReservations;
}
