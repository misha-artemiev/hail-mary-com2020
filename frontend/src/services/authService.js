/**
 * authService.js
 */

// Set the default base API route
const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

export async function createSession(email, password) {
    // Convert credentials (i.e. email:password) to Base64 token
    const credentials = btoa(`${email}:${password}`);

    const response = await fetch(`${API_BASE_URL}/session`, {
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

export function storeAuthToken(tokenData) {
    // Push auth information to local storage
    localStorage.setItem("authToken", tokenData.token);
    localStorage.setItem("tokenExpiresAt", tokenData.expires_at);
    localStorage.setItem("userRole", tokenData.role);
}

export function getAuthToken() {
    return localStorage.getItem("authToken");
}

export function clearAuthToken() {
    // Clears auth
    localStorage.removeItem("authToken");
    localStorage.removeItem("tokenExpiresAt");
    localStorage.removeItem("userRole");
}
