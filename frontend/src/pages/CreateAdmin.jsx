/**
 * CreateAdmin.jsx
 * @author Thomas Noakes
 */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

import Card from "../components/Card";
import Button from "../components/forms/Button";
import FormInput from "../components/forms/FormInput";
import SubmitButton from "../components/forms/SubmitButton";
import useCreateAdmin from "../hooks/useCreateAdmin";

export default function CreateAdmin() {
    const navigate = useNavigate();
    const { creating, createAdmin } = useCreateAdmin();

    const [form, setFormData] = useState({
        rootUsername: "",
        rootPassword: "",
        username: "",
        email: "",
        password: "",
        confirmPassword: "",
        first_name: "",
        last_name: "",
    });

    const [error, setError] = useState(null);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        if (form.password !== form.confirmPassword) {
            setError("Passwords do not match");
            return;
        }

        const adminData = {
            username: form.username,
            email: form.email,
            password: form.password,
            first_name: form.first_name,
            last_name: form.last_name,
        };

        try {
            await createAdmin(adminData, form.rootUsername, form.rootPassword);
            navigate("/");
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="max-w-2xl mx-auto p-4 md:p-6">
            <Card>
                <h1 className="text-2xl font-bold text-green-700 mb-6">
                    Create New Admin
                </h1>

                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="bg-gray-50 border border-gray-300 rounded-lg p-4 mb-4">
                        <h2 className="text-lg font-semibold text-gray-700 mb-3">
                            Root Authentication
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <FormInput
                                label="Root Username"
                                name="rootUsername"
                                type="text"
                                value={form.rootUsername}
                                onChange={handleChange}
                                required
                                placeholder="Enter root username"
                            />
                            <FormInput
                                label="Root Password"
                                name="rootPassword"
                                type="password"
                                value={form.rootPassword}
                                onChange={handleChange}
                                required
                                placeholder="Enter root password"
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <FormInput
                            label="Username"
                            name="username"
                            type="text"
                            value={form.username}
                            onChange={handleChange}
                            required
                            placeholder="Enter username"
                        />
                        <FormInput
                            label="Email"
                            name="email"
                            type="email"
                            value={form.email}
                            onChange={handleChange}
                            required
                            placeholder="Enter email"
                        />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <FormInput
                            label="First Name"
                            name="first_name"
                            type="text"
                            value={form.first_name}
                            onChange={handleChange}
                            required
                            placeholder="Enter first name"
                        />
                        <FormInput
                            label="Last Name"
                            name="last_name"
                            type="text"
                            value={form.last_name}
                            onChange={handleChange}
                            required
                            placeholder="Enter last name"
                        />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <FormInput
                            label="Password"
                            name="password"
                            type="password"
                            value={form.password}
                            onChange={handleChange}
                            required
                            placeholder="Enter password"
                        />
                        <FormInput
                            label="Confirm Password"
                            name="confirmPassword"
                            type="password"
                            value={form.confirmPassword}
                            onChange={handleChange}
                            required
                            placeholder="Confirm password"
                        />
                    </div>

                    <div className="flex gap-4 pt-4">
                        <SubmitButton disabled={creating}>
                            {creating ? "Creating Admin..." : "Create Admin"}
                        </SubmitButton>
                        <Button onClick={() => navigate("/")}>Cancel</Button>
                    </div>
                </form>
            </Card>
        </div>
    );
}
