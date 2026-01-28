/**
 * App.jsx
 * @author Thomas Noakes
 */

import React from "react";
import { Route, Routes } from "react-router-dom";

// Components
import Navbar from "./components/Navbar";

// Routes (individual pages)
import Home from "./pages/Home";
import Profile from "./pages/Profile";
import NotFound from "./pages/NotFound";
import Login from "./pages/Login";
import Signup from "./pages/Signup";

/**
 * Uses the React Router to display a client-side rendered single-page application (SPA).
 *
 * @returns {JSX.Element} the full single-page application.
 */
export default function App() {
    return (
        <div className="bg-gray-50 min-h-screen">
            <Navbar />

            {/* Load pages in the React Router */}
            <Routes>
                <Route path="/" element={<Home />}></Route>
                <Route path="/profile" element={<Profile />}></Route>
                <Route path="/login" element={<Login />}></Route>
                <Route path="/signup" element={<Signup />}></Route>

                {/* Catch-all (i.e. 404) */}
                <Route path="*" element={<NotFound />}></Route>
            </Routes>
        </div>
    );
}
