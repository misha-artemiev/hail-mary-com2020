/**
 * Navbar.jsx
 * @author Thomas Noakes
 */

import React, { useState } from "react";
import { NavLink } from "react-router-dom";

// Authentication
import { useAuth } from "../context/AuthContext";

// Images
import logoFull from "../assets/logos/logo-full-512.png";
import defaultProfile from "../assets/default-user.jpg";

// Components
import HamburgerMenu from "./HamburgerMenu";

/**
 * A simple navigation header with links to other pages.
 *
 * @returns {JSX.Element} the navbar component.
 */
export default function Navbar() {
    const { isAuthenticated, userRole } = useAuth();
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    // TODO: get correct user information
    const user = {
        displayName: "User0001",
        profilePic: defaultProfile,
    };

    const closeMenu = () => setIsMenuOpen(false);

    return (
        <nav className="bg-green-600 text-white px-4 py-3 flex justify-between items-center shadow-md relative">
            {/* Left side: Logo and main nav links */}
            <div className="hidden md:flex items-center gap-4 lg:gap-8">
                {/* Home page logo */}
                <NavLink to="/" onClick={closeMenu}>
                    <img
                        src={logoFull}
                        alt="Logo"
                        className="h-10 md:h-16 w-auto hover:scale-102 transition"
                    />
                </NavLink>

                {userRole === "consumer" && (
                    <NavLink to="/leaderboard" className="text-bold text-lg">
                        Leaderboard
                    </NavLink>
                )}
            </div>

            {/* Right side: User actions */}
            <div className="hidden md:flex items-center gap-4 lg:gap-8">
                {userRole === "consumer" && (
                    <NavLink to="/reservations" className="text-bold text-lg">
                        My Reservations
                    </NavLink>
                )}

                {userRole === "seller" && (
                    <>
                        <NavLink
                            to="/seller-dashboard"
                            className="text-bold text-lg"
                        >
                            Seller Dashboard
                        </NavLink>
                        <NavLink
                            to="/bundles/create"
                            className="px-2 py-1.5 rounded-md bg-green-100 text-green-700 text-md font-bold hover:scale-102 transition"
                        >
                            Create new listing
                        </NavLink>
                    </>
                )}

                {/* If signed in, show profile picture (link to profile page) */}
                {/* Otherwise, show login/signup link */}
                <div className="hover:scale-110 transition">
                    {isAuthenticated ? (
                        <NavLink to="/profile">
                            <img
                                src={user.profilePic}
                                alt={`${user.displayName}'s profile`}
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

            {/* Mobile: Logo only */}
            <div className="md:hidden">
                <NavLink to="/" onClick={closeMenu}>
                    <img
                        src={logoFull}
                        alt="Logo"
                        className="h-10 w-auto hover:scale-102 transition"
                    />
                </NavLink>
            </div>

            {/* Mobile Menu Button */}
            <button
                className="md:hidden p-2"
                onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
                {/* Menu icons */}
                <svg
                    className="w-6 h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    {isMenuOpen ? (
                        // 'Close' icon
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M6 18L18 6M6 6l12 12"
                        />
                    ) : (
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M4 6h16M4 12h16M4 18h16"
                        />
                    )}
                </svg>
            </button>

            {/* Mobile Menu Dropdown */}
            <HamburgerMenu isOpen={isMenuOpen} onClose={closeMenu} />
        </nav>
    );
}
