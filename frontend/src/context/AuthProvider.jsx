/**
 * AuthContext.jsx
 * @author Thomas Noakes
 */

import React, { createContext, useContext, useState, useEffect } from "react";
import { getAuthToken, clearAuthToken } from "../services/authService";
import { AuthContext } from "./auth-context";

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

    useEffect(() => {
        const token = getAuthToken();
        const role = localStorage.getItem("userRole");

        if (token) {
            setIsAuthenticated(true);
            setUserRole(role);
        }
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
        clearAuthToken();
        setIsAuthenticated(false);
        setUserRole(null);
    };

    return (
        <AuthContext.Provider
            value={{ isAuthenticated, userRole, login, logout }}
        >
            {children}
        </AuthContext.Provider>
    );
}
