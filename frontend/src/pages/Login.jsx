/**
 * Login.jsx
 * @author Ed Brown
 */

import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

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
    const location = useLocation();
    const navigate = useNavigate();

    // Where to return once submitted (default: homepage)
    const from = location.state?.from?.pathname || "/";

    // State object: holds all fields for the form
    const [form, setForm] = useState({
        email: "",
        password: "",
    });

    /**
     * Handles changes to the form.
     */
    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));
    };

    /**
     * Handles submitting the form.
     * Redirects to `/`
     */
    const handleSubmit = (e) => {
        e.preventDefault();

        // TODO: sign-in logic
        alert("Login submitted");

        // Redirect to home page
        navigate(from, { replace: true });
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

                {/* Header */}
                <h1 className="text-3xl font-bold text-green-700 mb-6 text-center">
                    Sign In
                </h1>

                {/* Login Form */}
                <form onSubmit={handleSubmit} className="space-y-4">
                    {renderFields(LOGIN_FORM_FIELDS)}

                    {/* Submit */}
                    <SubmitButton>Sign in</SubmitButton>
                </form>

                <Divider>or</Divider>

                {/* Signup redirect */}
                <Button onClick={() => navigate("/signup")}>
                    Create an Account
                </Button>
            </Card>
        </div>
    );
}
