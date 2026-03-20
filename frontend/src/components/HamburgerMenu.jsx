/**
 * HamburgerMenu.jsx
 * @author Thomas Noakes
 */

import React from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

// Images
import defaultProfile from "../assets/default-user.jpg";

/**
 * A responsive 'Hamburger' menu for use on mobile screens.
 * Replaces many options on Navbar hidden by small screens.
 *
 * @param {Object} props
 * @param {boolean} props.isOpen - State for if the menu should be open.
 * @param {() => void} props.onClose - Callback to close the menu.
 *
 * @returns {JSX.Element} A positioned Hamburger menu
 */
export default function HamburgerMenu({ isOpen, onClose }) {
    const { isAuthenticated, userRole } = useAuth();

    // TODO: get correct user information
    const user = {
        displayName: "User0001",
        profilePic: defaultProfile,
    };

    return (
        <div
            className={`absolute top-full left-0 right-0
                      p-4 md:hidden flex flex-col gap-4 z-50
                      bg-green-600 shadow-md
                      transition-all duration-200 ease-in-out ${
                          isOpen // Open and close
                              ? "opacity-100 translate-y-0"
                              : "opacity-0 -translate-y-2 pointer-events-none"
                      }`}
        >
            {userRole === "consumer" && (
                <>
                    <NavLink
                        to="/leaderboard"
                        className="text-bold text-lg"
                        onClick={onClose}
                    >
                        Leaderboard
                    </NavLink>
                    <NavLink
                        to="/reservations"
                        className="text-bold text-lg"
                        onClick={onClose}
                    >
                        My Reservations
                    </NavLink>
                </>
            )}

            {userRole === "seller" && (
                <NavLink
                    to="/seller-dashboard"
                    className="text-bold text-lg"
                    onClick={onClose}
                >
                    Seller Dashboard
                </NavLink>
            )}

            {userRole === "admin" && (
                <NavLink
                    to="/admin/create"
                    className="text-bold text-lg"
                    onClick={onClose}
                >
                    Admin
                </NavLink>
            )}

            <NavLink
                to="/aboutus"
                className="text-bold text-lg"
                onClick={onClose}
            >
                About Us
            </NavLink>

            {/* If user is a seller, show create bundle link */}
            {userRole === "seller" && (
                <NavLink
                    to="/bundles/create"
                    className="px-2 py-1.5 rounded-md bg-green-100 text-green-700 text-md font-bold"
                    onClick={onClose}
                >
                    Create new listing
                </NavLink>
            )}

            {/* If signed in, show profile picture (link to profile page) */}
            {/* Otherwise, show login/signup link */}
            {isAuthenticated ? (
                <NavLink
                    to="/profile"
                    className="flex items-center gap-2"
                    onClick={onClose}
                >
                    <img
                        src={user.profilePic}
                        alt={`${user.displayName}'s profile`}
                        className="w-10 h-10 rounded-full"
                    />
                    <span>{user.displayName}</span>
                </NavLink>
            ) : (
                <NavLink
                    to="/login"
                    className="px-2 py-1.5 rounded-md bg-green-100 text-green-700 text-md font-bold text-center"
                    onClick={onClose}
                >
                    Log In / Sign Up
                </NavLink>
            )}
        </div>
    );
}
