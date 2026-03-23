/**
 * Navbar.jsx
 * @author Thomas Noakes
 */

import React, { useState, useRef, useEffect } from "react";
import { NavLink } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useUserImage } from "../hooks/useUserImage";

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
    const INBOX_AUTO_REFRESH_MS = 1500;
    const { isAuthenticated, userRole } = useAuth();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isAboutDropdownOpen, setIsAboutDropdownOpen] = useState(false);
    const [isInboxDropdownOpen, setIsInboxDropdownOpen] = useState(false);
    const [inboxItems, setInboxItems] = useState([]);
    const [isInboxLoading, setIsInboxLoading] = useState(false);
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";
    const { imageUrl } = useUserImage();

    const aboutDropdownRef = useRef(null);
    const inboxDropdownRef = useRef(null);
    const mobileInboxDropdownRef = useRef(null);

    const user = {
        displayName: "User0001",
        profilePic: defaultProfile,
    };

    const closeMenu = () => setIsMenuOpen(false);

    const fetchInbox = async ({ silent = false } = {}) => {
        const token = localStorage.getItem("authToken");
        if (!token) {
            setInboxItems([]);
            return;
        }

        if (!silent) {
            setIsInboxLoading(true);
        }
        try {
            const response = await fetch(`${API_BASE_URL}/users/me/inbox`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (!response.ok) {
                setInboxItems([]);
                return;
            }

            const data = await response.json();
            const sorted = [...data].sort(
                (a, b) => new Date(b.sent_at) - new Date(a.sent_at),
            );
            setInboxItems(sorted);
        } catch (error) {
            console.error("Unable to load inbox", error);
            setInboxItems([]);
        } finally {
            if (!silent) {
                setIsInboxLoading(false);
            }
        }
    };

    const dismissInboxItem = async (messageId) => {
        const token = localStorage.getItem("authToken");
        if (!token) {
            return;
        }

        try {
            const response = await fetch(
                `${API_BASE_URL}/users/me/inbox/${messageId}`,
                {
                    method: "PATCH",
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                },
            );

            if (!response.ok) {
                const data = await response.json().catch(() => null);
                throw new Error(
                    data?.detail || "Unable to dismiss inbox message.",
                );
            }

            setInboxItems((prev) =>
                prev.filter((item) => item.message_id !== messageId),
            );
        } catch (error) {
            console.error(error.message);
        }
    };

    // Close dropdown when clicking outside
    useEffect(() => {
        function handleClickOutside(event) {
            if (
                aboutDropdownRef.current &&
                !aboutDropdownRef.current.contains(event.target)
            ) {
                setIsAboutDropdownOpen(false);
            }
            if (
                inboxDropdownRef.current &&
                !inboxDropdownRef.current.contains(event.target)
            ) {
                if (
                    !mobileInboxDropdownRef.current ||
                    !mobileInboxDropdownRef.current.contains(event.target)
                ) {
                    setIsInboxDropdownOpen(false);
                }
            }
        }

        // Once opened, start listening for clicks outside
        document.addEventListener("mousedown", handleClickOutside);
        return () =>
            document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    useEffect(() => {
        if (isAuthenticated) {
            fetchInbox();
        } else {
            setInboxItems([]);
        }
    }, [isAuthenticated]);

    useEffect(() => {
        if (!isAuthenticated) {
            return;
        }

        const refreshInbox = () => {
            fetchInbox({ silent: true });
        };

        const handleVisibilityChange = () => {
            if (document.visibilityState === "visible") {
                refreshInbox();
            }
        };

        const intervalId = setInterval(() => {
            if (document.visibilityState === "visible") {
                refreshInbox();
            }
        }, INBOX_AUTO_REFRESH_MS);

        window.addEventListener("focus", refreshInbox);
        document.addEventListener("visibilitychange", handleVisibilityChange);

        return () => {
            clearInterval(intervalId);
            window.removeEventListener("focus", refreshInbox);
            document.removeEventListener(
                "visibilitychange",
                handleVisibilityChange,
            );
        };
    }, [isAuthenticated]);

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
                {isAuthenticated && (
                    <div className="relative" ref={inboxDropdownRef}>
                        <button
                            className="text-bold text-lg flex items-center gap-2"
                            onClick={() => {
                                const nextOpen = !isInboxDropdownOpen;
                                setIsInboxDropdownOpen(nextOpen);
                                if (nextOpen) {
                                    fetchInbox();
                                }
                            }}
                        >
                            Inbox
                            <span className="inline-flex items-center justify-center min-w-6 h-6 px-1 rounded-full bg-green-100 text-green-700 text-xs font-bold">
                                {inboxItems.length}
                            </span>
                        </button>
                        {isInboxDropdownOpen && (
                            <div className="absolute right-0 mt-2 w-96 max-w-[90vw] bg-white text-black rounded-md shadow-lg py-2 z-50 animate-in">
                                <div className="flex items-center justify-between px-4 pb-2 border-b border-gray-200">
                                    <h3 className="text-sm font-semibold text-gray-700">
                                        Your Inbox
                                    </h3>
                                    <button
                                        type="button"
                                        className="text-xs text-green-700 hover:underline"
                                        onClick={fetchInbox}
                                    >
                                        Refresh
                                    </button>
                                </div>
                                <div className="max-h-80 overflow-y-auto">
                                    {isInboxLoading ? (
                                        <p className="px-4 py-3 text-sm text-gray-600">
                                            Loading messages...
                                        </p>
                                    ) : inboxItems.length === 0 ? (
                                        <p className="px-4 py-3 text-sm text-gray-600">
                                            No inbox messages yet.
                                        </p>
                                    ) : (
                                        inboxItems.map((item) => (
                                            <div
                                                key={item.message_id}
                                                className="px-4 py-3 border-b border-gray-100"
                                            >
                                                <div className="flex items-start justify-between gap-2">
                                                    <p className="text-sm font-semibold text-gray-800">
                                                        {item.message_subject}
                                                    </p>
                                                    <button
                                                        type="button"
                                                        className="text-xs font-semibold text-red-600 hover:underline"
                                                        onClick={() =>
                                                            dismissInboxItem(
                                                                item.message_id,
                                                            )
                                                        }
                                                    >
                                                        Dismiss
                                                    </button>
                                                </div>
                                                <p className="text-sm text-gray-600 mt-1">
                                                    {item.message_text}
                                                </p>
                                                <p className="text-xs text-gray-500 mt-1">
                                                    {new Date(
                                                        item.sent_at,
                                                    ).toLocaleString("en-GB")}
                                                </p>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {userRole === "consumer" && (
                    <NavLink to="/reservations" className="text-bold text-lg">
                        My Reservations
                    </NavLink>
                )}

                {userRole === "seller" && (
                    <>
                        <NavLink to="/bundles/create">
                            <button className="px-2 py-1.5 rounded-md bg-green-100 text-green-700 text-md font-bold hover:scale-102 transition">
                                Create new listing
                            </button>
                        </NavLink>
                        <NavLink
                            to="/dashboard"
                            className="px-2 py-1.5 rounded-md bg-green-100 text-green-700 text-md font-bold hover:scale-102 transition flex items-center gap-2"
                        >
                            <span>Seller Dashboard</span>
                            <img
                                src={imageUrl || user.profilePic}
                                alt={`${user.displayName}'s profile`}
                                className="w-8 h-8 rounded-full"
                                onError={(e) => {
                                    e.target.src = defaultProfile;
                                }}
                            />
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
                {userRole !== "seller" && (
                    <div>
                        {isAuthenticated ? (
                            <NavLink
                                to="/profile"
                                className="px-2 py-1.5 rounded-md bg-green-100 text-green-700 text-md font-bold hover:scale-102 transition flex items-center gap-2"
                            >
                                <span>Profile</span>
                                <img
                                    src={imageUrl || defaultProfile}
                                    alt="Profile"
                                    className="w-10 h-10 rounded-full object-cover"
                                    onError={(e) => {
                                        e.target.src = defaultProfile;
                                    }}
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
                )}
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

            {/* Mobile buttons */}
            <div className="md:hidden flex items-center gap-2">
                {isAuthenticated && (
                    <button
                        type="button"
                        className="p-2 text-sm font-semibold"
                        onClick={() => {
                            const nextOpen = !isInboxDropdownOpen;
                            setIsInboxDropdownOpen(nextOpen);
                            if (nextOpen) {
                                fetchInbox();
                            }
                        }}
                    >
                        Inbox ({inboxItems.length})
                    </button>
                )}
                <button
                    className="p-2"
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
            </div>

            {isAuthenticated && isInboxDropdownOpen && (
                <div
                    ref={mobileInboxDropdownRef}
                    className="md:hidden absolute right-2 top-14 w-96 max-w-[95vw] bg-white text-black rounded-md shadow-lg py-2 z-50"
                >
                    <div className="flex items-center justify-between px-4 pb-2 border-b border-gray-200">
                        <h3 className="text-sm font-semibold text-gray-700">
                            Your Inbox
                        </h3>
                        <button
                            type="button"
                            className="text-xs text-green-700 hover:underline"
                            onClick={fetchInbox}
                        >
                            Refresh
                        </button>
                    </div>
                    <div className="max-h-80 overflow-y-auto">
                        {isInboxLoading ? (
                            <p className="px-4 py-3 text-sm text-gray-600">
                                Loading messages...
                            </p>
                        ) : inboxItems.length === 0 ? (
                            <p className="px-4 py-3 text-sm text-gray-600">
                                No inbox messages yet.
                            </p>
                        ) : (
                            inboxItems.map((item) => (
                                <div
                                    key={item.message_id}
                                    className="px-4 py-3 border-b border-gray-100"
                                >
                                    <div className="flex items-start justify-between gap-2">
                                        <p className="text-sm font-semibold text-gray-800">
                                            {item.message_subject}
                                        </p>
                                        <button
                                            type="button"
                                            className="text-xs font-semibold text-red-600 hover:underline"
                                            onClick={() =>
                                                dismissInboxItem(
                                                    item.message_id,
                                                )
                                            }
                                        >
                                            Dismiss
                                        </button>
                                    </div>
                                    <p className="text-sm text-gray-600 mt-1">
                                        {item.message_text}
                                    </p>
                                    <p className="text-xs text-gray-500 mt-1">
                                        {new Date(item.sent_at).toLocaleString(
                                            "en-GB",
                                        )}
                                    </p>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}

            {/* Mobile Menu Dropdown */}
            <HamburgerMenu isOpen={isMenuOpen} onClose={closeMenu} />
        </nav>
    );
}
