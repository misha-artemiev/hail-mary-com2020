import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), "");

    return {
        plugins: [react(), tailwindcss()],
        server: {
            port: 5173,
            open: true,
            ...(env.VITE_USE_PROXY === "true" && {
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
    };
});
