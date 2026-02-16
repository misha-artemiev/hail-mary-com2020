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
 * @param {Array<string>} [props.allowedRoles] - Optional list of allowed roles.
 *
 * @returns {JSX.Element} a potential redirect to the login page, if unauthenticated.
 */
export default function ProtectedRoute({ children, allowedRoles }) {
    const location = useLocation();

    const { isAuthenticated, userRole } = useAuth();

    // Redirect to the login page
    if (!isAuthenticated) {
        return <Navigate to="/login" replace state={{ from: location }} />;
    }

    // Redirect if role is not authorised for this route.
    if (allowedRoles && !allowedRoles.includes(userRole)) {
        return <Navigate to="/" replace />;
    }

    return children;
}

