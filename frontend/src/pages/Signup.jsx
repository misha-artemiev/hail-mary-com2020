import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

// Components
import FormInput from "../components/forms/FormInput";
import RoleSelect from "../components/forms/RoleSelect";
import Divider from "../components/forms/Divider";

// Config
import { SIGNUP_FORM_FIELDS } from "../config/signupFormFields";

// Renders signup form for new consumers and sellers based on RBAC

export default function Signup() {
    const navigate = useNavigate();

    // State object: holds all fields for the form
    const [role, setRole] = useState("");
    const [form, setForm] = useState({
        email: "",
        password: "",
        confirmPassword: "",
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

    const handleChange = (e) => {
        // Handles changes to form
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        // Handles sign-up submission
        e.preventDefault();

        if (form.password !== form.confirmPassword) {
            // Ensures passwords match
            alert("Please ensure that passwords match");
            return;
        }

        // TODO: sign-up logic
        alert("Signup submitted");

        // Redirect to home page
        navigate("/");
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
        // Page design
        <div className="max-w-xl mx-auto p-6">
            <div className="bg-white shadow-md rounded-lg p-6">
                <h1 className="text-3xl font-bold text-green-700 mb-6">
                    Create Account
                </h1>

                {/* Signup Form */}
                <form onSubmit={handleSubmit} className="space-y-4">
                    {renderFields(SIGNUP_FORM_FIELDS.common)}

                    {/* Role */}
                    <RoleSelect
                        label="Role"
                        value={role}
                        onChange={(e) => setRole(e.target.value)}
                        options={[
                            { value: "", label: "Select role" },
                            { value: "consumer", label: "Consumer" },
                            { value: "seller", label: "Seller" },
                        ]}
                    />

                    {/* Role-specific fields */}
                    {role === "consumer" &&
                        renderFields(SIGNUP_FORM_FIELDS.consumer)}
                    {role === "seller" &&
                        renderFields(SIGNUP_FORM_FIELDS.seller)}

                    {/* Submit */}
                    <button
                        type="submit"
                        className="w-full bg-green-600 text-white px-4 py-3 rounded-md font-semibold
                                   hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 mt-4"
                    >
                        Sign Up
                    </button>
                </form>

                <Divider text="or" />

                {/* Login Redirect */}
                <button
                    onClick={() => navigate("/login")}
                    className="w-full border border-green-600 text-green-700 px-4 py-3 rounded-md font-semibold
                               hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                    Already have an account? Sign In
                </button>
            </div>
        </div>
    );
}
