/**
 * Navbar.jsx
 * @author Thomas Noakes
 */

import React from "react";
import { NavLink } from "react-router-dom";

// Authentication
import { useAuth } from "../context/AuthContext";

// Images
import logoFull from "../assets/logos/logo-full-512.png";
import defaultProfile from "../assets/default-user.jpg";

/**
 * A simple navigation header with links to other pages.
 *
 * @returns {JSX.Element} the navigation bar
 */
export default function Navbar() {
    const { isAuthenticated, userRole } = useAuth();

    // TODO: get correct user information
    const user = {
        displayName: "User0001",
        profilePic: defaultProfile,
    };

    return (
        <nav className="bg-green-600 text-white px-6 py-4 flex justify-between items-center shadow-md">
            <div className="flex items-center gap-8">
                {/* Home page logo */}
                <NavLink to="/">
                    <img
                        src={logoFull}
                        alt="Logo"
                        className="h-16 w-auto hover:scale-102 transition"
                    />
                </NavLink>
                <NavLink to="/analytics" className="text-bold text-lg">
                    Analytics
                </NavLink>
                <NavLink to="/aboutus" className="text-bold text-lg">
                    About Us
                </NavLink>
            </div>

            <div className="flex items-center gap-8">
                {/* If user is a seller, show create bundle link */}
                {userRole === "seller" && (
                    <NavLink
                        to="/bundles/create"
                        className="px-2 py-1.5 rounded-md bg-green-100 text-green-700 text-md font-bold hover:scale-102 transition"
                    >
                        Create new listing
                    </NavLink>
                )}

                {/* If signed in, show profile picture (link to profile page) */}
                {/* Otherwise, show login/signup link */}
                <div className="hover:scale-110 transition">
                    {isAuthenticated ? (
                        <NavLink to="/profile">
                            <img
                                src={user.profilePic}
                                alt={`${user.displayName}'s profile`}
                                // Grow on hover
                                className="w-10 h-10 rounded-full"
                            />
                        </NavLink>
                    ) : (
                        <div className="px-2 py-1.5 rounded-md bg-green-100 text-green-700 text-md font-bold">
                            <NavLink to="/login">
                                Log In /<br />
                                Sign Up
                            </NavLink>
                        </div>
                    )}
                </div>
            </div>
        </nav>
    );
}
