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
    const { isAuthenticated } = useAuth();

    // TODO: get correct user information
    const user = {
        displayName: "User0001",
        profilePic: defaultProfile,
    };

    return (
        <nav className="bg-green-600 text-white px-6 py-4 flex justify-between items-center shadow-md">
            {/* Home page logo */}
            <NavLink to="/">
                <img
                    src={logoFull}
                    alt="Logo"
                    // Grow on hover:
                    className="h-16 w-auto hover:scale-102 transition"
                />
            </NavLink>

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
                    <NavLink to="/login" className="text-md font-bold">
                        Log In /<br />
                        Sign Up
                    </NavLink>
                )}
            </div>
        </nav>
    );
}
