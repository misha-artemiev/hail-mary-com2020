import js from "@eslint/js";
import globals from "globals";
import pluginReact from "eslint-plugin-react";
import { defineConfig } from "eslint/config";

export default defineConfig([
    // Ignore distribution and prebuild modules
    {
        ignores: ["dist/", "node_modules/"],
    },

    // Default Javascript rules
    {
        files: ["**/*.{js,jsx}"],
        plugins: { js },
        extends: ["js/recommended"],
        settings: {
            react: {
                version: "detect",
            },
        },
        languageOptions: {
            globals: globals.browser,
        },
    },

    // Default React rules
    pluginReact.configs.flat.recommended,
]);
