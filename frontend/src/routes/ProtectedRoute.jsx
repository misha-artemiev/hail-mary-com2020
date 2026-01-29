/**
 * ProtectedRoute.jsx
 * @author Thomas Noakes
 */

import React from "react";
import { Navigate, useLocation } from "react-router-dom";

export default function ProtectedRoute({ children }) {
    const location = useLocation();

    const isAuthenticated = false; // TODO: replace with actual authentication logic

    if (!isAuthenticated) {
        return <Navigate to="/login" replace state={{ from: location }} />;
    }

    return children;
}
