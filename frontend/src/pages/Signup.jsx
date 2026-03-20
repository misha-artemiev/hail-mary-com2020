/**
 * Signup.jsx
 * @author Ed Brown
 */

import React from "react";
import { Link, useNavigate } from "react-router-dom";

// Components
import Card from "../components/Card";
import FormInput from "../components/forms/FormInput";
import RoleSelect from "../components/forms/RoleSelect";
import Divider from "../components/Divider";
import SubmitButton from "../components/forms/SubmitButton";
import Button from "../components/forms/Button";
import LocationPicker from "../components/LocationPicker";

// Config
import { SIGNUP_FORM_FIELDS } from "../config/signupFormFields";

// Hooks
import { useSignup } from "../hooks/useSignup";

/**
 * The signup page of the site.
 * Users can choose a role (seller or consumer).
 * Required information changes according to role.
 *
 * @returns {JSX.Elements} the signup page
 */
export default function Signup() {
    const navigate = useNavigate();
    const {
        form,
        handleChange,
        handleLocationChange,
        role,
        setRole,
        error,
        loading,
        handleSubmit,
    } = useSignup();

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
        <div className="max-w-xl mx-auto p-4 md:p-6">
            {/* Signup container */}
            <Card>
                {/* Error message */}
                {error && (
                    <div className="text-center font-semibold bg-red-100 text-red-800 p-3 mb-4 rounded">
                        {error}
                    </div>
                )}

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
                        required
                    />

                    {/* Role-specific fields */}
                    {role === "consumer" &&
                        renderFields(SIGNUP_FORM_FIELDS.consumer)}
                    {role === "seller" &&
                        renderFields(SIGNUP_FORM_FIELDS.seller)}

                    {/* Location picker for sellers */}
                    {role === "seller" && (
                        <LocationPicker
                            value={form.location}
                            onChange={handleLocationChange}
                            label="Pick Location on Map"
                            required
                        />
                    )}

                    {/* Terms and conditions */}
                    <div className="flex items-center gap-2">
                        <input
                            id="terms"
                            type="checkbox"
                            name="terms"
                            checked={form.terms}
                            onChange={handleChange}
                            required
                            className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                        />
                        <label htmlFor="terms" className="text-gray-700">
                            I have read and agree to the{" "}
                            <Link
                                to="/terms"
                                className="text-green-600 hover:underline"
                            >
                                Terms and Conditions
                            </Link>
                            <span className="text-red-500"> *</span>
                        </label>
                    </div>

                    {/* Submit */}
                    <SubmitButton disabled={loading}>
                        {loading ? "Signing up..." : "Sign up"}
                    </SubmitButton>
                </form>

                <Divider>or</Divider>

                {/* Login redirect */}
                <Button onClick={() => navigate("/login")}>
                    Already have an account? Sign In
                </Button>
            </Card>
        </div>
    );
}
