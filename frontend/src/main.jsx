import { React, StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

// Apply the app to the HTML
createRoot(document.getElementById("root")).render(
    <StrictMode>
        <App />
    </StrictMode>,
);
