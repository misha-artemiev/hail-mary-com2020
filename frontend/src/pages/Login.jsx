/**
 * Login.jsx
 * @author Ed Brown
 */

import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

// Authentication
import { createSession, storeAuthToken } from "../services/authService";
import { useAuth } from "../context/authContext";

// Components
import Card from "../components/Card";
import FormInput from "../components/forms/FormInput";
import Divider from "../components/Divider";
import SubmitButton from "../components/forms/SubmitButton";
import Button from "../components/forms/Button";

// Config
import { LOGIN_FORM_FIELDS } from "../config/loginFormFields";

/**
 * The login page of the site.
 * Allows users to login using their email and password.
 *
 * @returns {JSX.Element} the login page
 */
export default function Login() {
    const auth_ctx = useAuth();
    const location = useLocation();
    const navigate = useNavigate();

    // Where to return once submitted (default: homepage)
    const from = location.state?.from?.pathname || "/";

    // State object: holds all fields for the form
    const [form, setForm] = useState({
        email: "",
        password: "",
    });

    // Loading and error states
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    /**
     * Handles changes to the form.
     */
    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));
        // Clear errors
        if (error) setError(null);
    };

    /**
     * Handles submitting the form.
     * Redirects to `/`
     */
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            // Authenticate to get token, store it
            const tokenData = await createSession(form.email, form.password);
            storeAuthToken(tokenData);

            console.log(tokenData);

            // Update AuthContext state
            auth_ctx.login(tokenData);

            // Redirect to home page or redirect
            navigate(from, { replace: true });
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    /**
     * Dynamically renders given information fields.
     *
     * @param {Object} fields
     * @returns {JSX.Element} a set of FormInput elements.
     */
    const renderFields = (fields) =>
        fields.map((field) => (
            <FormInput
                key={field.name}
                label={field.label}
                name={field.name}
                type={field.type}
                value={form[field.name]}
                onChange={handleChange}
                required={field.required}
            />
        ));

    return (
        <div className="max-w-xl mx-auto p-6">
            {/* Login container */}
            <Card>
                {/* Warning, if from 'protected' page */}
                {location.state?.from?.pathname && (
                    <div className="text-center font-semibold bg-red-100 text-red-800 p-3 mb-4 rounded">
                        You must be logged in to do that!
                    </div>
                )}

                {/* Error message */}
                {error && (
                    <div className="text-center font-semibold bg-red-100 text-red-800 p-3 mb-4 rounded">
                        {error}
                    </div>
                )}

                {/* Header */}
                <h1 className="text-3xl font-bold text-green-700 mb-6 text-center">
                    Sign In
                </h1>

                {/* Login Form */}
                <form onSubmit={handleSubmit} className="space-y-4">
                    {renderFields(LOGIN_FORM_FIELDS)}

                    {/* Submit */}
                    <SubmitButton disabled={loading}>
                        {loading ? "Signing in..." : "Sign in"}
                    </SubmitButton>
                </form>

                <Divider>or</Divider>

                {/* Signup redirect */}
                <Button onClick={() => navigate("/signup")} disabled={loading}>
                    Create an Account
                </Button>
            </Card>
        </div>
    );
}
