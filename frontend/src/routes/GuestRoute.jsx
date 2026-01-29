/**
 * GuestRoot.jsx
 * @author Thomas Noakes
 */

import React from "react";
import { Navigate } from "react-router-dom";

/**
 * Protects some pages from being accessed if the user is already logged in.
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - The page to be protected.
 *
 * @returns {JSX.Element} a potential redirect to the home page, if already authenticated.
 */
export default function GuestRoot({ children }) {
    const isAuthenticated = false; // TODO: replace with actual authentication logic

    // Redirect to the homepage
    return isAuthenticated ? <Navigate to="/" replace /> : children;
}
