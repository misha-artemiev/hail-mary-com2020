/**
 * RootAuthForm.jsx
 */

import React from "react";

import FormInput from "./FormInput";
import SubmitButton from "./SubmitButton";
import { ROOT_AUTH_FIELDS } from "../../config/rootAuthFields";

export default function RootAuthForm({ credentials, onChange, onSubmit, loading }) {
    return (
        <form onSubmit={onSubmit} className="space-y-4">
            <div className="bg-gray-50 border border-gray-300 rounded-lg p-4 mb-4">
                <h2 className="text-lg font-semibold text-gray-700 mb-3">
                    Root Authentication
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {ROOT_AUTH_FIELDS.map((field) => (
                        <FormInput
                            key={field.name}
                            label={field.label}
                            name={field.name}
                            type={field.type}
                            value={credentials[field.name]}
                            onChange={onChange}
                            required
                            placeholder={field.placeholder}
                        />
                    ))}
                </div>
            </div>
            <div className="flex gap-4 pt-4">
                <SubmitButton type="submit" className="w-auto px-6 mt-0" disabled={loading}>
                    {loading ? "Loading..." : "View Admins"}
                </SubmitButton>
            </div>
        </form>
    );
}
