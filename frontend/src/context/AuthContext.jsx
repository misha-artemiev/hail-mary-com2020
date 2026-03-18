/**
 * AuthContext.jsx
 * @author Thomas Noakes
 */

import React, { createContext, useContext, useState, useEffect } from "react";
import {
    getAuthToken,
    fetchUsername,
    logout as logoutService,
} from "../services/authService";

const AuthContext = createContext(null);

/**
 * A component that wraps the application and supplies authentication logic.
 *
 * @param {object} props
 * @param {React.ReactNode} props.children
 *          - The elements to be protected by authentication context
 *
 * @returns {React.Element} the context provider component.
 */
export function AuthProvider({ children }) {
    // State object: if the user (within context) is authenticated
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [userRole, setUserRole] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const initAuth = async () => {
            const token = getAuthToken();
            const role = localStorage.getItem("userRole");
            const storedUsername = localStorage.getItem("username");

            if (token) {
                setIsAuthenticated(true);
                setUserRole(role);

                // Fetch username if not already stored
                if (!storedUsername && role) {
                    const username = await fetchUsername(role, token);
                    if (username) {
                        localStorage.setItem("username", username);
                    }
                }
            }
            setLoading(false);
        };

        initAuth();
    }, []);

    /**
     * Stores token data in context.
     *
     * @param {Object} tokenData the token data to store.
     */
    const login = (tokenData) => {
        setIsAuthenticated(true);
        setUserRole(tokenData.role);
    };

    /**
     * Removes token data from context.
     */
    const logout = () => {
        logoutService();
        setIsAuthenticated(false);
        setUserRole(null);
    };

    return (
        <AuthContext.Provider
            value={{ isAuthenticated, userRole, login, logout, loading }}
        >
            {children}
        </AuthContext.Provider>
    );
}

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
