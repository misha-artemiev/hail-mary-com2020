/**
 * main.jsx
 * @author Thomas Noakes
 */

import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App"; // Loads the SPA
import { AuthProvider } from "./context/AuthProvider"; // Authentication context
import "./styles/index.css"; // Loads TailwindCSS

// Apply the app to the HTML
createRoot(document.getElementById("root")).render(
    <React.StrictMode>
        <AuthProvider>
            <BrowserRouter>
                <App />
            </BrowserRouter>
        </AuthProvider>
    </React.StrictMode>,
);
