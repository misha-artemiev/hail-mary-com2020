import { createContext, useContext } from "react";

export const AuthContext = createContext(null);

/**
 * Custom hook to access authentication context.
 * Must be used within an AuthProvider element.
 *
 * @returns {Object} the authentication context.
 *
 * ---
 * @example
 * const { isAuthenticated, userRole, login, logout } = useAuth();
 */
export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within AuthProvider");
    }
    return context;
}
