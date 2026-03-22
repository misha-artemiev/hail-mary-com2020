/**
 * AdminRoute.jsx
 * @author Thomas Noakes
 */

import React from "react";
import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

/**
 * Protects pages from being accessed unless by an admin user.
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - The page to be protected.
 *
 * @returns {JSX.Element} a redirect to login or home if not an admin.
 */
export default function AdminRoute({ children }) {
    const location = useLocation();

    const { isAuthenticated, userRole, loading } = useAuth();

    if (loading) {
        return null;
    }

    if (!isAuthenticated) {
        return (
            <Navigate to="/admin/login" replace state={{ from: location }} />
        );
    }

    if (userRole !== "admin") {
        return <Navigate to="/" replace />;
    }

    return children;
}
