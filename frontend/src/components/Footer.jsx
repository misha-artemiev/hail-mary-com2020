/**
 * Footer.jsx
 * @author Thomas Noakes
 */

import React from "react";
import { Link } from "react-router-dom";

// Config
import { FOOTER_LINKS } from "../config/footerLinks";

/**
 * A dark-gray footer containing links to various pages, and copyright info.
 *
 * @returns {JSX.Element} a footer container.
 */
export default function Footer() {
    /**
     * Dynamically renders given links.
     *
     * @param {Object} links
     * @param {string} links.to - The destination of the link.
     * @param {string} links.description - The content of the link.
     *
     * @returns {JSX.Element} a set of Link elements.
     */
    const renderLinks = (links) =>
        links.map((link) => (
            <Link
                key={link.to}
                to={link.to}
                className="hover:text-white hover:scale-102 transition text-sm"
            >
                {link.description}
            </Link>
        ));

    return (
        <footer className="bg-gray-800 text-gray-400 py-6 mt-auto">
            {/* Extra spacing */}
            <div className="container mx-auto px-4">
                {/* Footer items */}
                <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                    {/* Group links together */}
                    <div className="flex flex-wrap justify-center gap-4 md:gap-6">
                        {/* Dynamically render all footer links */}
                        {renderLinks(FOOTER_LINKS)}
                    </div>

                    <div className="flex flex-wrap justify-center gap-4 md:gap-6 items-center">
                        <p className="text-xs">
                            Copyright © Rescue Market. All Rights Reserved
                        </p>

                        {/* Github logo */}
                        <a
                            href="https://github.com/misha-artemiev/hail-mary-com2020"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-gray-400 hover:text-white hover:scale-105 transition"
                        >
                            <svg className="w-6 h-6" viewBox="0 0 20 20">
                                <path
                                    fill="currentColor"
                                    d="M10 0c5.523 0 10 4.59 10 10.253 0 4.529-2.862 8.371-6.833 9.728-.507.101-.687-.219-.687-.492 0-.338.012-1.442.012-2.814 0-.956-.32-1.58-.679-1.898 2.227-.254 4.567-1.121 4.567-5.059 0-1.12-.388-2.034-1.03-2.752.104-.259.447-1.302-.098-2.714 0 0-.838-.275-2.747 1.051A9.4 9.4 0 0 0 10 4.958a9.4 9.4 0 0 0-2.503.345C5.586 3.977 4.746 4.252 4.746 4.252c-.543 1.412-.2 2.455-.097 2.714-.639.718-1.03 1.632-1.03 2.752 0 3.928 2.335 4.808 4.556 5.067-.286.256-.545.708-.635 1.371-.57.262-2.018.715-2.91-.852 0 0-.529-.985-1.533-1.057 0 0-.975-.013-.068.623 0 0 .655.315 1.11 1.5 0 0 .587 1.83 3.369 1.21.005.857.014 1.665.014 1.909 0 .271-.184.588-.683.493C2.865 18.627 0 14.783 0 10.253 0 4.59 4.478 0 10 0"
                                />
                            </svg>
                        </a>
                    </div>
                </div>
            </div>
        </footer>
    );
}
