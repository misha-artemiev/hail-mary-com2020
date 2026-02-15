/**
 * ProtectedRoute.jsx
 * @author Thomas Noakes
 */

import React from "react";
import { Navigate, useLocation } from "react-router-dom";

// Authentication
import { useAuth } from "../context/auth-context.js";

/**
 * Protects some pages from being accessed unless by an authenticated user.
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - The page to be protected.
 *
 * @returns {JSX.Element} a potential redirect to the login page, if unauthenticated.
 */
export default function ProtectedRoute({ children }) {
    const location = useLocation();

    const { isAuthenticated } = useAuth();

    // Redirect to the login page
    if (!isAuthenticated) {
        return <Navigate to="/login" replace state={{ from: location }} />;
    }

    return children;
}
