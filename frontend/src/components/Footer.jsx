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

                    <p className="text-xs">
                        Copyright © Rescue Market. All Rights Reserved
                    </p>
                </div>
            </div>
        </footer>
    );
}
