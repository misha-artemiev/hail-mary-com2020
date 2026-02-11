/**
 * AuthContext.jsx
 * @author Thomas Noakes
 */

import React, { createContext, useContext, useState, useEffect } from "react";
import { getAuthToken, clearAuthToken } from "../services/authService";

const AuthContext = createContext(null);

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

    const login = (tokenData) => {
        setIsAuthenticated(true);
        setUserRole(tokenData.role);
    };

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

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within AuthProvider");
    }
    return context;
}
