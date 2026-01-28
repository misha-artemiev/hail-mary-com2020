/**
 * Signup.jsx
 * @author Ed Brown
 */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

// Components
import Card from "../components/Card";
import FormInput from "../components/forms/FormInput";
import RoleSelect from "../components/forms/RoleSelect";
import Divider from "../components/forms/Divider";
import SubmitButton from "../components/forms/SubmitButton";
import Button from "../components/forms/Button";

// Config
import { SIGNUP_FORM_FIELDS } from "../config/signupFormFields";

/**
 * The signup page of the site.
 * Users can choose a role (seller or consumer).
 * Required information changes according to role.
 *
 * @returns {JSX.Elements} the signup page
 */
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

        // Ensure passwords match
        if (form.password !== form.confirmPassword) {
            alert("Please ensure that passwords match");
            return;
        }

        // TODO: sign-up logic
        alert("Signup submitted");

        // Redirect to home page
        navigate("/");
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
            {/* Signup container */}
            <Card>
                {/* Header */}
                <h1 className="text-3xl font-bold text-green-700 mb-6">
                    Create Account
                </h1>

                {/* Signup form */}
                <form onSubmit={handleSubmit} className="space-y-4">
                    {/* Dynamically render all common fields */}
                    {renderFields(SIGNUP_FORM_FIELDS.common)}

                    {/* Role dropdown */}
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
                    <SubmitButton>Sign up</SubmitButton>
                </form>

                <Divider text="or" />

                {/* Login redirect */}
                <Button onClick={() => navigate("/login")}>
                    Already have an account? Sign In
                </Button>
            </Card>
        </div>
    );
}
