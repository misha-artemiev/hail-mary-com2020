/**
 * authService.js
 */

// Set the default base API route
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Fetches the current user's profile to get their username.
 *
 * @param {string} role - The user's role (consumer/seller).
 * @param {string} token - The auth token.
 * @returns {Promise<string|null>} The username or null if failed.
 */
export async function fetchUsername(role, token) {
    const endpoint = role === "seller" ? "/sellers/me" : "/consumers/me";

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        if (!response.ok) return null;
        const data = await response.json();
        return data.username || null;
    } catch {
        return null;
    }
}

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

    // Handle errors
    if (!response.ok) {
        let errorMessage = "An error occurred. Please try again.";

        try {
            const errorData = await response.json();
            errorMessage =
                errorData.detail || errorData.message || errorMessage;
        } catch {
            // Response wasn't JSON, use default message
        }

        throw new Error(errorMessage);
    }

    return await response.json();
}

/**
 * Stores the authentication token object in localStorage.
 *
 * @param {Object} tokenData - Response from {@link createSession}.
 */
export async function storeAuthToken(tokenData) {
    // Push auth information to local storage
    localStorage.setItem("authToken", tokenData.token);
    localStorage.setItem("tokenExpiresAt", tokenData.expires_at);
    localStorage.setItem("userRole", tokenData.role);

    // Fetch username based on role
    const username = await fetchUsername(tokenData.role, tokenData.token);
    if (username) {
        localStorage.setItem("username", username);
    }
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
 * Retrieves the current username, if authenticated.
 *
 * @returns {string|null} the stored username.
 */
export function getUsername() {
    return localStorage.getItem("username");
}

/**
 * Clears stored authentication data.
 */
export function clearAuthToken() {
    // Clears auth
    localStorage.removeItem("authToken");
    localStorage.removeItem("tokenExpiresAt");
    localStorage.removeItem("userRole");
    localStorage.removeItem("username");
}

/**
 * Logs out the user by removing the token from local storage.
 */
export function logout() {
    clearAuthToken();
}
