/**
 * App.jsx
 * @author Thomas Noakes
 */

import React from "react";
import { Route, Routes } from "react-router-dom";

// Components
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

// Dynamic routing
import { ROUTES } from "./routes/routes";

/**
 * Uses the React Router to display a client-side rendered single-page application (SPA).
 *
 * @returns {JSX.Element} the full single-page application.
 */
export default function App() {
    return (
        <div className="bg-gray-50 min-h-screen flex flex-col">
            <Navbar />

            {/* Dynamically load pages in the React Router */}
            {/* Content expands to fill screen */}
            <div className="grow">
                <Routes>
                    {ROUTES.map(({ path, element }) => (
                        <Route key={path} path={path} element={element} />
                    ))}
                </Routes>
            </div>

            {/* Footer pushed to the bottom */}
            <div className="hidden md:block">
                <Footer />
            </div>
        </div>
    );
}
