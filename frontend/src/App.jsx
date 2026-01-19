import React from "react";
import { Route, Routes } from "react-router-dom";

// Components
import Navbar from "./components/Navbar";

// Routes (individual pages)
import NotFound from "./pages/NotFound";

export default function App() {
    return (
        <>
            {/* Display a navigation bar */}
            <Navbar />

            {/* Load pages in the React Router */}
            <Routes>
                {/* Catch-all (i.e. 404) */}
                <Route path="*" element={<NotFound />}></Route>
            </Routes>
        </>
    );
}
