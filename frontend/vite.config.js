import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
    plugins: [react(), tailwindcss()],

    // Default development (hot) server
    server: {
        port: 5173,
        open: true,
        proxy: {
            "/api/": {
                target: "http://127.0.0.1:8080",
            },
        },
    },

    // Preview built package
    preview: {
        port: 4173,
    },

    // Build info
    build: {
        outDir: "dist",
        sourcemap: true, // For easier debugging
    },
});
