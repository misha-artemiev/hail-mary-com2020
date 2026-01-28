/**
 * NotFound.jsx
 * @author Thomas Noakes
 */

import React from "react";
import Card from "../components/Card";
import Button from "../components/forms/Button";
import { useNavigate } from "react-router-dom";

// Images
import logoIcon from "../assets/logos/logo-icon-512.png";

/**
 * Catches all unknown UI routes (*i.e.* `/*`) and displays a 404 error page.
 *
 * @returns {JSX.Element} a 404 page
 */
export default function NotFound() {
    const navigate = useNavigate();

    return (
        <>
            {/* 404 container */}
            <div className="max-w-xl mx-auto p-6">
                <Card className="flex flex-col items-centre text-center gap-6">
                    {/* Logo */}
                    <img
                        src={logoIcon}
                        alt="Logo"
                        className="h-56 w-auto object-contain flex-shrink-0"
                    />

                    {/* Header */}
                    <h1 className="text-3xl font-bold text-green-700">
                        404 Not Found
                    </h1>

                    {/* Error text */}
                    <p className="mb-6">
                        That&apos;s an error! The page could not be found.
                    </p>

                    {/* Redirect button */}
                    <Button onClick={() => navigate("/")}>Return Home</Button>
                </Card>
            </div>
        </>
    );
}
