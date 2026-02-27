/**
 * Footer.jsx
 * @author Thomas Noakes
 */

import React from "react";
import { Link } from "react-router-dom";

export default function Footer() {
    return (
        <footer className="bg-gray-800 text-gray-400 py-6 mt-auto">
            {/* Extra spacing */}
            <div className="container mx-auto px-4">
                {/* Footer items */}
                <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                    {/* Group links together */}
                    <div className="flex flex-wrap justify-center gap-4 md:gap-6">
                        <Link
                            to="/legal"
                            className="hover:text-white hover:scale-102 transition text-sm"
                        >
                            Legal
                        </Link>

                        <Link
                            to="/privacy"
                            className="hover:text-white hover:scale-102 transition text-sm"
                        >
                            Privacy Policy
                        </Link>

                        <Link
                            to="/cookies"
                            className="hover:text-white hover:scale-102 transition text-sm"
                        >
                            Cookie Policy
                        </Link>

                        <Link
                            to="/terms"
                            className="hover:text-white hover:scale-102 transition text-sm"
                        >
                            Terms and Conditions
                        </Link>

                        <Link
                            to="/contact"
                            className="hover:text-white hover:scale-102 transition text-sm"
                        >
                            Contact Us
                        </Link>
                    </div>

                    <p className="text-xs">
                        Copyright © Rescue Market. All Rights Reserved
                    </p>
                </div>
            </div>
        </footer>
    );
}
