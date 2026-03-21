/**
 * AdminLogin.jsx
 */

import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

import { storeAuthToken } from "../services/authService";
import { useAuth } from "../context/AuthContext";

import Card from "../components/Card";
import FormInput from "../components/forms/FormInput";
import SubmitButton from "../components/forms/SubmitButton";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export default function AdminLogin() {
    const { login } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const from = location.state?.from?.pathname || "/admin";

    const [form, setForm] = useState({
        username: "",
        password: "",
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));
        if (error) setError(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const credentials = btoa(`${form.username}:${form.password}`);
            const response = await fetch(`${API_BASE_URL}/sessions`, {
                method: "POST",
                headers: {
                    Authorization: `Basic ${credentials}`,
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                let errorMessage = "Invalid credentials";
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch {
                    // Use default message
                }
                throw new Error(errorMessage);
            }

            const tokenData = await response.json();
            await storeAuthToken(tokenData);
            login(tokenData);

            navigate(from, { replace: true });
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-xl mx-auto p-4 md:p-6">
            <Card>
                {error && (
                    <div className="text-center font-semibold bg-red-100 text-red-800 p-3 mb-4 rounded">
                        {error}
                    </div>
                )}

                <h1 className="text-3xl font-bold text-green-700 mb-6 text-center">
                    Admin Sign In
                </h1>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <FormInput
                        label="Username"
                        name="username"
                        type="text"
                        value={form.username}
                        onChange={handleChange}
                        required
                    />
                    <FormInput
                        label="Password"
                        name="password"
                        type="password"
                        value={form.password}
                        onChange={handleChange}
                        required
                    />
                    <SubmitButton disabled={loading}>
                        {loading ? "Signing in..." : "Sign in"}
                    </SubmitButton>
                </form>
            </Card>
        </div>
    );
}
