/**
 * GuestRoot.jsx
 * @author Thomas Noakes
 */

import React from "react";
import { Navigate } from "react-router-dom";

export default function GuestRoot({ children }) {
    const isAuthenticated = false; // TODO: replace with actual authentication logic

    return isAuthenticated ? <Navigate to="/" replace /> : children;
}
