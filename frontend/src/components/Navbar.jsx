/**
 * Navbar.jsx
 * @author Thomas Noakes
 */

import React, { useState, useRef, useEffect } from "react";
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
    const [isAboutDropdownOpen, setIsAboutDropdownOpen] = useState(false);

    // Reference object to the the dropdown
    const aboutDropdownRef = useRef(null);

    // TODO: get correct user information
    const user = {
        displayName: "User0001",
        profilePic: defaultProfile,
    };

    // State object: if the dropdown is open
    const closeMenu = () => setIsMenuOpen(false);

    // Close dropdown when clicking outside
    useEffect(() => {
        function handleClickOutside(event) {
            if (
                aboutDropdownRef.current &&
                !aboutDropdownRef.current.contains(event.target)
            ) {
                setIsAboutDropdownOpen(false);
            }
        }

        // Once opened, start listening for clicks outside
        document.addEventListener("mousedown", handleClickOutside);
        return () =>
            document.removeEventListener("mousedown", handleClickOutside);
    }, []);

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

                <div className="relative" ref={aboutDropdownRef}>
                    <button
                        className="text-bold text-lg flex items-center gap-1"
                        onClick={() =>
                            setIsAboutDropdownOpen(!isAboutDropdownOpen)
                        }
                    >
                        About Us
                        <svg
                            className={`w-4 h-4 transition-transform ${isAboutDropdownOpen ? "rotate-180" : ""}`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M19 9l-7 7-7-7"
                            />
                        </svg>
                    </button>
                    {isAboutDropdownOpen && (
                        <div className="absolute left-0 mt-2 w-40 bg-white text-black rounded-md shadow-lg py-1 z-50 animate-in">
                            <NavLink
                                to="/aboutus"
                                className="block px-4 py-2 hover:bg-gray-100"
                                onClick={() => setIsAboutDropdownOpen(false)}
                            >
                                About Us
                            </NavLink>
                            <NavLink
                                to="/our-team"
                                className="block px-4 py-2 hover:bg-gray-100"
                                onClick={() => setIsAboutDropdownOpen(false)}
                            >
                                Our Team
                            </NavLink>
                            <NavLink
                                to="/contact"
                                className="block px-4 py-2 hover:bg-gray-100"
                                onClick={() => setIsAboutDropdownOpen(false)}
                            >
                                Contact
                            </NavLink>
                        </div>
                    )}
                </div>
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
                        <NavLink to="/dashboard" className="text-bold text-lg">
                            Seller Dashboard
                        </NavLink>
                        <NavLink
                            to="/dashboard/issues"
                            className="text-bold text-lg"
                        >
                            Issue Reports
                        </NavLink>
                        <NavLink
                            to="/bundles/create"
                            className="px-2 py-1.5 rounded-md bg-green-100 text-green-700 text-md font-bold hover:scale-102 transition"
                        >
                            Create new listing
                        </NavLink>
                    </>
                )}

                {userRole === "admin" && (
                    <>
                        <NavLink
                            to="/admin/create"
                            className="text-bold text-lg"
                        >
                            Create Admin
                        </NavLink>
                        <NavLink
                            to="/admin/manage"
                            className="text-bold text-lg"
                        >
                            Manage Admins
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
