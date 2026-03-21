import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig(({ mode }) => ({
    plugins: [react(), tailwindcss()],
    server: {
        port: 5173,
        open: true,
        ...(mode === "development" && {
            proxy: {
                "/api": {
                    target: "http://localhost:8080",
                    changeOrigin: true,
                },
            },
        }),
    },
    preview: {
        port: 4173,
    },
    build: {
        outDir: "dist",
        sourcemap: true,
    },
}));
