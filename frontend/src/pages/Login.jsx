import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

// Components
import FormInput from "../components/forms/FormInput";
import Divider from "../components/forms/Divider";
import SubmitButton from "../components/forms/SubmitButton";
import Button from "../components/forms/Button";

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

                    {/* Submit */}
                    <SubmitButton />
                </form>

                <Divider text="or" />

                {/* Signup redirect */}
                <Button onClick={() => navigate("/signup")}>
                    Create an Account
                </Button>
            </div>
        </div>
    );
}
