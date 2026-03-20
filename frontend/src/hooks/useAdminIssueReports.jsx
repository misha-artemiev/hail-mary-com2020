/**
 * useAdminIssueReports.jsx
 * @author Ed Brown
 */

import { useEffect, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Fetches all issue reports available to admins.
 * Combines seller issue reports and admin issue reports into one list.
 */
export default function useAdminIssueReports() {
    const [issueReports, setIssueReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchIssueReports() {
            setLoading(true);
            setError(null);

            const token = localStorage.getItem("authToken");
            if (!token) {
                setLoading(false);
                return;
            }

            try {
                const headers = {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                };

                const [sellerRes, adminRes] = await Promise.all([
                    fetch(`${API_BASE_URL}/admins/database/reports/seller`, {
                        method: "GET",
                        headers,
                    }),
                    fetch(`${API_BASE_URL}/admins/database/reports/admin`, {
                        method: "GET",
                        headers,
                    }),
                ]);

                if (!sellerRes.ok || !adminRes.ok) {
                    const sellerError = await sellerRes.json().catch(() => null);
                    const adminError = await adminRes.json().catch(() => null);
                    throw new Error(
                        sellerError?.detail ||
                            adminError?.detail ||
                            "Failed to fetch issue reports",
                    );
                }

                const sellerIssues = (await sellerRes.json()).map((report) => ({
                    ...report,
                    source_type: "seller",
                }));

                const adminIssues = (await adminRes.json()).map((report) => ({
                    ...report,
                    source_type: "admin",
                    reservation_id: null,
                }));

                const combined = [...sellerIssues, ...adminIssues].sort((a, b) => {
                    const first = new Date(a.created_at).getTime();
                    const second = new Date(b.created_at).getTime();
                    return second - first;
                });

                setIssueReports(combined);
            } catch (err) {
                setError(err?.message || "Failed to fetch issue reports");
                setIssueReports([]);
            } finally {
                setLoading(false);
            }
        }

        fetchIssueReports();
    }, []);

    return { issueReports, loading, error };
}
