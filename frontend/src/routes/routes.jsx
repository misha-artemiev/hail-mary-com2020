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

/**
 * Dynamically maps routes (i.e. pages) to their paths.
 * Used by the router to build a single-page application (SPA).
 */
export const ROUTES = [
    {
        path: "/",
        element: <Home />,
    },
    {
        path: "/profile",
        element: <Profile />,
    },
    {
        path: "/login",
        element: <Login />,
    },
    {
        path: "/signup",
        element: <Signup />,
    },
    // Catch-all (i.e. 404)
    {
        path: "*",
        element: <NotFound />,
    },
];
