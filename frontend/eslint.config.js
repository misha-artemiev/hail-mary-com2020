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
        extends: ["js/recommended", pluginReact.configs.flat.recommended],
        settings: {
            react: {
                version: "detect",
            },
        },
        languageOptions: {
            globals: globals.browser,
        },
        rules: {
            "react/prop-types": "off",
        },
    },
]);
