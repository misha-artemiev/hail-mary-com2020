/**
 * ManageAdmins.jsx
 */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

import Card from "../components/Card";
import FormInput from "../components/forms/FormInput";
import SubmitButton from "../components/forms/SubmitButton";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export default function ManageAdmins() {
    const navigate = useNavigate();

    const [rootCredentials, setRootCredentials] = useState({
        username: "",
        password: "",
    });

    const [admins, setAdmins] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const [selectedAdmin, setSelectedAdmin] = useState(null);
    const [editForm, setEditForm] = useState({ first_name: "", last_name: "", email: "", password: "" });
    const [editing, setEditing] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setRootCredentials((prev) => ({ ...prev, [name]: value }));
    };

    const fetchAdmins = async () => {
        setLoading(true);
        const credentials = btoa(
            `${rootCredentials.username}:${rootCredentials.password}`,
        );

        try {
            const response = await fetch(`${API_BASE_URL}/admins`, {
                method: "GET",
                headers: {
                    Authorization: `Basic ${credentials}`,
                },
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to fetch admins");
            }

            const data = await response.json();
            setAdmins(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const toggleAdminStatus = async (adminId, currentlyActive) => {
        const credentials = btoa(
            `${rootCredentials.username}:${rootCredentials.password}`,
        );
        const endpoint = currentlyActive ? "deactivate" : "activate";

        try {
            const response = await fetch(
                `${API_BASE_URL}/admins/${adminId}/${endpoint}`,
                {
                    method: "PATCH",
                    headers: {
                        Authorization: `Basic ${credentials}`,
                    },
                },
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(
                    errorData.detail || `Failed to ${endpoint} admin`,
                );
            }

            await fetchAdmins();
        } catch (err) {
            setError(err.message);
        }
    };

    const openEditModal = (admin) => {
        setSelectedAdmin(admin);
        setEditForm({
            first_name: admin.first_name || "",
            last_name: admin.last_name || "",
            email: admin.email || "",
            password: "",
        });
        setEditing(true);
    };

    const closeEditModal = () => {
        setSelectedAdmin(null);
        setEditForm({ first_name: "", last_name: "", email: "", password: "" });
        setEditing(false);
    };

    const handleEditChange = (e) => {
        const { name, value } = e.target;
        setEditForm((prev) => ({ ...prev, [name]: value }));
    };

    const updateAdmin = async (e) => {
        e.preventDefault();
        const credentials = btoa(
            `${rootCredentials.username}:${rootCredentials.password}`,
        );

        try {
            const profileResponse = await fetch(
                `${API_BASE_URL}/admins/${selectedAdmin.user_id}`,
                {
                    method: "PATCH",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Basic ${credentials}`,
                    },
                    body: JSON.stringify({
                        first_name: editForm.first_name,
                        last_name: editForm.last_name,
                    }),
                },
            );

            if (!profileResponse.ok) {
                const errorData = await profileResponse.json();
                throw new Error(errorData.detail || "Failed to update admin profile");
            }

            if (editForm.email && editForm.email !== selectedAdmin.email) {
                const emailResponse = await fetch(
                    `${API_BASE_URL}/admins/database/users/${selectedAdmin.user_id}/email`,
                    {
                        method: "PATCH",
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: `Basic ${credentials}`,
                        },
                        body: JSON.stringify({ email: editForm.email }),
                    },
                );

                if (!emailResponse.ok) {
                    const errorData = await emailResponse.json();
                    throw new Error(errorData.detail || "Failed to update email");
                }
            }

            if (editForm.password) {
                const passwordResponse = await fetch(
                    `${API_BASE_URL}/admins/database/users/${selectedAdmin.user_id}/password`,
                    {
                        method: "PATCH",
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: `Basic ${credentials}`,
                        },
                        body: JSON.stringify({ password: editForm.password }),
                    },
                );

                if (!passwordResponse.ok) {
                    const errorData = await passwordResponse.json();
                    throw new Error(errorData.detail || "Failed to update password");
                }
            }

            closeEditModal();
            await fetchAdmins();
        } catch (err) {
            setError(err.message);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setError(null);
        fetchAdmins();
    };

    return (
        <div className="max-w-4xl mx-auto p-4 md:p-6">
            <Card>
                <h1 className="text-3xl font-bold text-green-700 mb-6 text-center">
                    Manage Admins
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
                                name="username"
                                type="text"
                                value={rootCredentials.username}
                                onChange={handleChange}
                                required
                                placeholder="Enter root username"
                            />
                            <FormInput
                                label="Root Password"
                                name="password"
                                type="password"
                                value={rootCredentials.password}
                                onChange={handleChange}
                                required
                                placeholder="Enter root password"
                            />
                        </div>
                    </div>

                    <div className="flex gap-4 pt-4">
                        <SubmitButton
                            type="submit"
                            className="w-auto px-6 mt-0"
                            disabled={loading}
                        >
                            {loading ? "Loading..." : "View Admins"}
                        </SubmitButton>
                        <SubmitButton
                            type="button"
                            onClick={() => navigate("/admin/create")}
                            className="w-auto px-6 mt-0"
                        >
                            Create Admin
                        </SubmitButton>
                    </div>
                </form>

                {admins.length > 0 && (
                    <div className="overflow-x-auto mt-6">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-200">
                                    <th className="text-left py-3 px-4 font-semibold text-gray-700">
                                        Username
                                    </th>
                                    <th className="text-left py-3 px-4 font-semibold text-gray-700">
                                        Email
                                    </th>
                                    <th className="text-left py-3 px-4 font-semibold text-gray-700">
                                        Status
                                    </th>
                                    <th className="text-right py-3 px-4 font-semibold text-gray-700">
                                        Actions
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {admins.map((admin) => (
                                    <tr
                                        key={admin.user_id}
                                        className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
                                        onClick={() => openEditModal(admin)}
                                    >
                                        <td className="py-3 px-4">
                                            {admin.username}
                                        </td>
                                        <td className="py-3 px-4">
                                            {admin.email}
                                        </td>
                                        <td className="py-3 px-4">
                                            <span
                                                className={`px-2 py-1 rounded text-sm ${
                                                    admin.active
                                                        ? "bg-green-100 text-green-700"
                                                        : "bg-red-100 text-red-700"
                                                }`}
                                            >
                                                {admin.active
                                                    ? "Active"
                                                    : "Inactive"}
                                            </span>
                                        </td>
                                        <td
                                            className="py-3 px-4 text-right"
                                            onClick={(e) => e.stopPropagation()}
                                        >
                                            <button
                                                onClick={() =>
                                                    toggleAdminStatus(
                                                        admin.user_id,
                                                        admin.active,
                                                    )
                                                }
                                                className={`px-3 py-1 rounded text-sm ${
                                                    admin.active
                                                        ? "bg-red-100 text-red-700 hover:bg-red-200"
                                                        : "bg-green-100 text-green-700 hover:bg-green-200"
                                                }`}
                                            >
                                                {admin.active
                                                    ? "Deactivate"
                                                    : "Activate"}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {editing && selectedAdmin && (
                    <div className="fixed inset-0 bg-black/20 bg-opacity-50 flex items-center justify-center z-50 p-4">
                        <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
                            <h2 className="text-xl font-bold text-gray-800 mb-4">
                                Edit Admin: {selectedAdmin.username}
                            </h2>

                            {error && (
                                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                                    {error}
                                </div>
                            )}

                            <form onSubmit={updateAdmin} className="space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <FormInput
                                        label="First Name"
                                        name="first_name"
                                        type="text"
                                        value={editForm.first_name}
                                        onChange={handleEditChange}
                                        required
                                    />
                                    <FormInput
                                        label="Last Name"
                                        name="last_name"
                                        type="text"
                                        value={editForm.last_name}
                                        onChange={handleEditChange}
                                        required
                                    />
                                </div>
                                <FormInput
                                    label="Email"
                                    name="email"
                                    type="email"
                                    value={editForm.email}
                                    onChange={handleEditChange}
                                    required
                                />
                                <FormInput
                                    label="New Password"
                                    name="password"
                                    type="password"
                                    value={editForm.password}
                                    onChange={handleEditChange}
                                    placeholder="Leave blank to keep current password"
                                />
                                <div className="flex gap-3 pt-2">
                                    <SubmitButton type="submit">
                                        Save Changes
                                    </SubmitButton>
                                    <button
                                        type="button"
                                        onClick={closeEditModal}
                                        className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}
            </Card>
        </div>
    );
}
