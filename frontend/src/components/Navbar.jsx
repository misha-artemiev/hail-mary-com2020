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
    const navLinks = [{ to: "/about", label: "About Us" }];

    if (userRole === "seller") {
        navLinks.unshift({ to: "/analysis", label: "Analysis" });
    }

    // TODO: get correct user information
    const user = {
        displayName: "User0001",
        profilePic: defaultProfile,
    };

    return (
        <nav className="bg-green-600 text-white px-6 py-4 flex justify-between items-center shadow-md">
            <div className="flex items-center gap-6">
                {/* Home page logo */}
                <NavLink to="/">
                    <img
                        src={logoFull}
                        alt="Logo"
                        // Grow on hover:
                        className="h-16 w-auto hover:scale-102 transition"
                    />
                </NavLink>

                {/* Main nav links */}
                <div className="flex items-center gap-4">
                    {navLinks.map((link) => (
                        <NavLink
                            key={link.to}
                            to={link.to}
                            className={({ isActive }) =>
                                `text-sm font-semibold transition ${
                                    isActive
                                        ? "text-green-100 underline underline-offset-4"
                                        : "text-white/90 hover:text-white"
                                }`
                            }
                        >
                            {link.label}
                        </NavLink>
                    ))}
                </div>
            </div>

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
