/**
 * routes.jsx
 * @author Thomas Noakes
 */

import React from "react";

// Routes (individual pages)
import Home from "../pages/Home";
import AboutUs from "../pages/AboutUs";
import OurTeam from "../pages/OurTeam";
import Leaderboard from "../pages/Leaderboard";
import Analytics from "../pages/Analytics";
import Profile from "../pages/Profile";
import NotFound from "../pages/NotFound";
import Login from "../pages/Login";
import AdminLogin from "../pages/AdminLogin";
import Signup from "../pages/Signup";
import User from "../pages/User";
import EditProfile from "../pages/EditProfile";
import Bundle from "../pages/Bundle";
import Collect from "../pages/Collect";
import CreateBundle from "../pages/CreateBundle";
import CreateAdmin from "../pages/CreateAdmin";
import ManageAdmins from "../pages/ManageAdmins";
import SellerDashboard from "../pages/SellerDashboard";
import SellerIssues from "../pages/SellerIssues";
import ConsumerDashboard from "../pages/ConsumerDashboard";
import ReportError from "../pages/ReportError";
import AdminPage from "../pages/AdminPage";
import TermsAndConditions from "../pages/TermsAndConditions";

// Route types
import ProtectedRoute from "./ProtectedRoute";
import GuestRoute from "./GuestRoute";
import AdminRoute from "./AdminRoute";

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
        path: "/aboutus",
        element: <AboutUs />,
    },
    {
        path: "/terms",
        element: <TermsAndConditions />,
    }
    {
        path: "/our-team",
        element: <OurTeam />,
    },
    {
        path: "/leaderboard",
        element: <Leaderboard />,
    },
    {
        path: "/analytics",
        element: <Analytics />,
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
    {
        path: "/dashboard",
        element: (
            <ProtectedRoute>
                <SellerDashboard />
            </ProtectedRoute>
        ),
    },
    {
        path: "/dashboard/issues",
        element: (
            <ProtectedRoute>
                <SellerIssues />
            </ProtectedRoute>
        ),
    },
    {
        path: "/reservations",
        element: (
            <ProtectedRoute>
                <ConsumerDashboard />
            </ProtectedRoute>
        ),
    },
    {
        path: "/admin",
        element: (
            <AdminRoute>
                <AdminPage />
            </AdminRoute>
        ),
    },
    {
        path: "/report-error",
        element: <ReportError />,
    },
    {
        path: "/admin/login",
        element: (
            <GuestRoute>
                <AdminLogin />
            </GuestRoute>
        ),
    },
    {
        path: "/admin/create",
        element: <CreateAdmin />,
    },
    {
        path: "/admin/manage",
        element: <ManageAdmins />,
    },
    // Catch-all (i.e. 404)
    {
        path: "*",
        element: <NotFound />,
    },
];
