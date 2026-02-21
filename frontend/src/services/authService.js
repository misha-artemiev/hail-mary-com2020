/**
 * authService.js
 */

// Set the default base API route
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Creates a session by authenticating with email and password.
 *
 * @param {string} email - User's email (used as username).
 * @param {string} password - User's password.
 *
 * @returns {Promise<Object>} the token object with `{token, expires_at, role}`
 * @throws {Error} if authentication fails.
 */
export async function createSession(email, password) {
    // Convert credentials (i.e. email:password) to Base64 token
    const credentials = btoa(`${email}:${password}`);

    const response = await fetch(`${API_BASE_URL}/sessions`, {
        method: "POST",
        headers: {
            Authorization: `Basic ${credentials}`,
            "Content-Type": "application/json",
        },
    });

    if (!response.ok) {
        // Check for invalid credentials
        if (response.status === 401) {
            throw new Error("Invalid email or password");
        }

        // Other authentication errors
        throw new Error("An error occurred. Please try again.");
    }

    return await response.json();
}

/**
 * Stores the authentication token object in localStorage.
 *
 * @param {Object} tokenData - Response from {@link createSession}.
 */
export function storeAuthToken(tokenData) {
    // Push auth information to local storage
    localStorage.setItem("authToken", tokenData.token);
    localStorage.setItem("tokenExpiresAt", tokenData.expires_at);
    localStorage.setItem("userRole", tokenData.role);
}

/**
 * Retrieves the current authentication token, if it exists.
 *
 * @returns {string|null} the stored token.
 */
export function getAuthToken() {
    return localStorage.getItem("authToken");
}

/**
 * Clears stored authentication data.
 */
export function clearAuthToken() {
    // Clears auth
    localStorage.removeItem("authToken");
    localStorage.removeItem("tokenExpiresAt");
    localStorage.removeItem("userRole");
}

/**
 * Logs out the user by removing the token from local storage.
 */
export function logout() {
    clearAuthToken();
}
