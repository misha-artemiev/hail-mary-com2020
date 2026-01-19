import React from "react";
import { Route, Routes } from "react-router-dom";

// Components
import Navbar from "./components/Navbar";

// Routes (individual pages)
import Home from "./pages/Home";
import Profile from "./pages/Profile";
import NotFound from "./pages/NotFound";

export default function App() {
    return (
        <>
            {/* Display a navigation bar */}
            <Navbar />

            {/* Load pages in the React Router */}
            <Routes>
                <Route path="/" element={<Home />}></Route>
                <Route path="/profile" element={<Profile />}></Route>

                {/* Catch-all (i.e. 404) */}
                <Route path="*" element={<NotFound />}></Route>
            </Routes>
        </>
    );
}
