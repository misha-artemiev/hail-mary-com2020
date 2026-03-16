/**
 * useSignup.js
 * @author Thomas Noakes
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { createSession, storeAuthToken } from "../services/authService";
import { useAuth } from "../context/AuthContext";

// Set the default base API route
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Constructs a payload and selects an endpoint based on the selected role.
 *
 * @param {string} role - The chosen role of the user.
 * @param {Object} form - The HTML form to get data from.
 *
 * @returns {{endpoint: string, payload: Object} | null}
 */
const buildRequest = (role, form) => {
    if (role === "consumer") {
        return {
            endpoint: `${API_BASE_URL}/consumers`,
            payload: {
                username: form.username,
                email: form.email,
                password: form.password,
                first_name: form.firstName,
                last_name: form.lastName,
            },
        };
    }

    if (role === "seller") {
        return {
            endpoint: `${API_BASE_URL}/sellers`,
            payload: {
                username: form.username,
                email: form.email,
                password: form.password,
                seller_name: form.sellerName,
                address_line1: form.address1,
                address_line2: form.address2,
                city: form.city,
                post_code: form.postCode,
                region: form.county,
                country: form.country,
            },
        };
    }

    // If no role type
    return null;
};

export function useSignup() {
    const navigate = useNavigate();
    const authContext = useAuth();

    // State object: holds all fields for the form
    const [role, setRole] = useState("");
    const [form, setForm] = useState({
        username: "",
        email: "",
        password: "",
        confirmPassword: "",
        terms: false,
        firstName: "",
        lastName: "",
        sellerName: "",
        address1: "",
        address2: "",
        city: "",
        postCode: "",
        county: "",
        country: "",
    });
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    /**
     * Handles changes to the form.
     */
    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setForm((prev) => ({
            ...prev,
            [name]: type === "checkbox" ? checked : value,
        }));
    };

    /**
     * Handles submitting the form.
     * Redirects to `/` on success.
     */
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        // Check a role has been selected.
        if (!role) {
            setError("Please select a role.");
            return;
        }

        // Ensure passwords match
        if (form.password !== form.confirmPassword) {
            alert("Please ensure that passwords match");
            return;
        }

        // Ensure terms are accepted
        if (!form.terms) {
            setError("You must accept the terms and conditions.");
            return;
        }

        // Construct the request data
        const request = buildRequest(role, form);
        if (!request) {
            setError("Invalid role selected.");
            return;
        }

        setLoading(true);

        try {
            // Send the request
            const response = await fetch(request.endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(request.payload),
            });

            // Catch bad HTTP codes
            if (!response.ok) {
                const data = await response.json().catch(() => null);
                throw new Error(
                    data?.message ?? `Signup failed (${response.status}).`,
                );
            }

            // Auto-login with new user
            const tokenData = await createSession(form.email, form.password);
            storeAuthToken(tokenData);
            authContext.login(tokenData);

            // Redirect to home page
            navigate("/");
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return { form, handleChange, role, setRole, error, loading, handleSubmit };
}
