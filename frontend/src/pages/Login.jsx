import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

// Components
import FormInput from "../components/forms/FormInput";

// Config
import { LOGIN_FORM_FIELDS } from "../config/loginFormFields";

export default function Login() {
    const navigate = useNavigate();

    // State object: holds all fields for the form
    const [form, setForm] = useState({
        email: "",
        password: "",
    });

    const handleChange = (e) => {
        // Handles changes to form
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        // Handles login submission
        e.preventDefault();

        // TODO: sign-in logic
        alert("Login submitted");

        // Redirect to home page
        navigate("/ ");
    };

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
        <div className="max-w-md mx-auto p-6">
            {/* Login card container */}
            <div className="bg-white shadow-md rounded-lg p-6">
                {/* Header */}
                <h1 className="text-3xl font-bold text-green-700 mb-6 text-center">
                    Sign In
                </h1>

                {/* Login Form */}
                <form onSubmit={handleSubmit} className="space-y-4">
                    {renderFields(LOGIN_FORM_FIELDS)}

                    {/* Sign In button */}
                    <button
                        type="submit"
                        className="w-full bg-green-600 text-white px-4 py-3 rounded-md font-semibold
                                   hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 mt-2"
                    >
                        Sign In
                    </button>
                </form>

                {/* Divider line */}
                <div className="flex items-center my-6">
                    <div className="flex-grow border-t border-gray-300" />
                    <span className="px-3 text-gray-500 text-sm">or</span>
                    <div className="flex-grow border-t border-gray-300" />
                </div>

                {/* Create Account Button */}
                <button
                    onClick={() => navigate("/signup")}
                    className="w-full border border-green-600 text-green-700 px-4 py-3 rounded-md font-semibold
                               hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                    Create an Account
                </button>
            </div>
        </div>
    );
}
