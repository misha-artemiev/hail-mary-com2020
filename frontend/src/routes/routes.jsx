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
import EditProfile from "../pages/EditProfile";
import Bundle from "../pages/Bundle";
import Collect from "../pages/Collect";
import CreateBundle from "../pages/CreateBundle";

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
        path: "/editprofile",
        element: (
            <ProtectedRoute>
                <EditProfile />
            </ProtectedRoute>
        ),
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
    {
        path: "/bundles/:id",
        element: <Bundle />,
    },
    {
        path: "/bundles/:id/collect",
        element: (
            <ProtectedRoute>
                <Collect />
            </ProtectedRoute>
        ),
    },
    {
        path: "/bundles/create",
        element: (
            <ProtectedRoute>
                <CreateBundle />
            </ProtectedRoute>
        ),
    },
    // Catch-all (i.e. 404)
    {
        path: "*",
        element: <NotFound />,
    },
];
