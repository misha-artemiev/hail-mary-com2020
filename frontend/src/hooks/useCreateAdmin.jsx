/**
 * useCreateAdmin.jsx
 * @author Thomas Noakes
 */

import { useState } from "react";

// Set the default base API route
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * A custom React hook to create a new admin.
 *
 * @returns {{ creating: boolean, createAdmin: () => Promise<void> }}
 */
export default function useCreateAdmin() {
    const [creating, setCreating] = useState(false);

    /**
     * Create a new admin with the given data.
     *
     * @param {Object} adminData - The data of the admin
     * @param {string} rootUsername - Root username
     * @param {string} rootPassword - Root password
     * @returns {Promise<void>}
     */
    async function createAdmin(adminData, rootUsername, rootPassword) {
        setCreating(true);

        const credentials = btoa(`${rootUsername}:${rootPassword}`);

        try {
            const response = await fetch(`${API_BASE_URL}/admins`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Basic ${credentials}`,
                },
                body: JSON.stringify({
                    username: adminData.username,
                    email: adminData.email,
                    password: adminData.password,
                    first_name: adminData.first_name,
                    last_name: adminData.last_name,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to create admin");
            }

            const data = await response.json();
            return data;
        } catch (err) {
            console.error(err.message);
            throw err;
        } finally {
            setCreating(false);
        }
    }

    return {
        creating,
        createAdmin,
    };
}
