/**
 * ProtectedRoute.jsx
 * @author Thomas Noakes
 */

import React from "react";
import { Navigate, useLocation } from "react-router-dom";

// Authentication
import { useAuth } from "../context/AuthContext";

/**
 * Protects some pages from being accessed unless by an authenticated user.
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - The page to be protected.
 * @param {string[]} [props.allowedRoles] - Optional list of roles that can access the route.
 *
 * @returns {JSX.Element} a potential redirect to the login page, if unauthenticated.
 */
export default function ProtectedRoute({ children, allowedRoles = null }) {
    const location = useLocation();

    const { isAuthenticated, userRole, loading } = useAuth();

    // Wait for loading to complete
    if (loading) {
        return null;
    }

    // Redirect to the login page
    if (!isAuthenticated) {
        return <Navigate to="/login" replace state={{ from: location }} />;
    }

    // Redirect authenticated users without the required role.
    if (allowedRoles && !allowedRoles.includes(userRole)) {
        return <Navigate to="/" replace />;
    }

    return children;
}
