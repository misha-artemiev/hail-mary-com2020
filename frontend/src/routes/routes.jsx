/**
 * routes.jsx
 * @author Thomas Noakes
 */

import React from "react";

// Routes (individual pages)
import Home from "../pages/Home";
import Profile from "../pages/Profile";
import NotFound from "../pages/NotFound";
import Login from "../pages/Login";
import Signup from "../pages/Signup";
import User from "../pages/User";
import DeveloperProfile from "../pages/DeveloperProfile";

// Route types
import ProtectedRoute from "./ProtectedRoute";
import GuestRoute from "./GuestRoute";

/**
 * Dynamically maps routes (i.e. pages) to their paths.
 * Used by the router to build a single-page application (SPA).
 *
 * Handles routes that are 'protected' (need to be signed in to access) and
 * 'guest' routes (cannot be accessed once logged in).
 */
export const ROUTES = [
    {
        path: "/",
        element: <Home />,
    },
    {
        path: "/profile",
        element: (
            <ProtectedRoute>
                <Profile />
            </ProtectedRoute>
        ),
    },
    {
        path: "/developer",
        element: <DeveloperProfile />,
    },
    {
        path: "/login",
        element: (
            <GuestRoute>
                <Login />
            </GuestRoute>
        ),
    },
    {
        path: "/signup",
        element: (
            <GuestRoute>
                <Signup />
            </GuestRoute>
        ),
    },
    {
        path: "/user/:username",
        element: <User />,
    },
    // Catch-all (i.e. 404)
    {
        path: "*",
        element: <NotFound />,
    },
];
