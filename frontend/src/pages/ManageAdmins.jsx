/**
 * ManageAdmins.jsx
 */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

import Card from "../components/Card";
import Modal from "../components/Modal";
import SubmitButton from "../components/forms/SubmitButton";
import FormInput from "../components/forms/FormInput";
import RootAuthForm from "../components/forms/RootAuthForm";
import AdminsTable from "../components/AdminsTable";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

const INITIAL_EDIT_FORM = { first_name: "", last_name: "", email: "", password: "" };

export default function ManageAdmins() {
    const navigate = useNavigate();

    const [rootCredentials, setRootCredentials] = useState({ username: "", password: "" });
    const [admins, setAdmins] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const [selectedAdmin, setSelectedAdmin] = useState(null);
    const [editForm, setEditForm] = useState(INITIAL_EDIT_FORM);
    const [editing, setEditing] = useState(false);

    const getCredentials = () => btoa(`${rootCredentials.username}:${rootCredentials.password}`);

    const fetchAdmins = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/admins`, {
                method: "GET",
                headers: { Authorization: `Basic ${getCredentials()}` },
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to fetch admins");
            }
            setAdmins(await response.json());
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const toggleAdminStatus = async (adminId, currentlyActive) => {
        try {
            const response = await fetch(
                `${API_BASE_URL}/admins/${adminId}/${currentlyActive ? "deactivate" : "activate"}`,
                { method: "PATCH", headers: { Authorization: `Basic ${getCredentials()}` } },
            );
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to update admin status");
            }
            await fetchAdmins();
        } catch (err) {
            setError(err.message);
        }
    };

    const openEditModal = (admin) => {
        setSelectedAdmin(admin);
        setEditForm({ first_name: admin.first_name || "", last_name: admin.last_name || "", email: admin.email || "", password: "" });
        setEditing(true);
    };

    const closeEditModal = () => {
        setSelectedAdmin(null);
        setEditForm(INITIAL_EDIT_FORM);
        setEditing(false);
    };

    const updateAdmin = async (e) => {
        e.preventDefault();
        try {
            const profileResponse = await fetch(`${API_BASE_URL}/admins/${selectedAdmin.user_id}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json", Authorization: `Basic ${getCredentials()}` },
                body: JSON.stringify({ first_name: editForm.first_name, last_name: editForm.last_name }),
            });
            if (!profileResponse.ok) throw new Error((await profileResponse.json()).detail || "Failed to update profile");

            if (editForm.email && editForm.email !== selectedAdmin.email) {
                const emailResponse = await fetch(
                    `${API_BASE_URL}/admins/database/users/${selectedAdmin.user_id}/email`,
                    { method: "PATCH", headers: { "Content-Type": "application/json", Authorization: `Basic ${getCredentials()}` }, body: JSON.stringify({ email: editForm.email }) },
                );
                if (!emailResponse.ok) throw new Error((await emailResponse.json()).detail || "Failed to update email");
            }

            if (editForm.password) {
                const passwordResponse = await fetch(
                    `${API_BASE_URL}/admins/database/users/${selectedAdmin.user_id}/password`,
                    { method: "PATCH", headers: { "Content-Type": "application/json", Authorization: `Basic ${getCredentials()}` }, body: JSON.stringify({ password: editForm.password }) },
                );
                if (!passwordResponse.ok) throw new Error((await passwordResponse.json()).detail || "Failed to update password");
            }

            closeEditModal();
            await fetchAdmins();
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="max-w-4xl mx-auto p-4 md:p-6">
            <Card>
                <h1 className="text-3xl font-bold text-green-700 mb-6 text-center">Manage Admins</h1>

                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                        {error}
                    </div>
                )}

                <RootAuthForm
                    credentials={rootCredentials}
                    onChange={(e) => setRootCredentials((prev) => ({ ...prev, [e.target.name]: e.target.value }))}
                    onSubmit={(e) => { e.preventDefault(); setError(null); fetchAdmins(); }}
                    loading={loading}
                />

                <div className="flex gap-4 pt-2">
                    <SubmitButton type="button" onClick={() => navigate("/admin/create")} className="w-auto px-6 mt-0">
                        Create Admin
                    </SubmitButton>
                </div>

                {admins.length > 0 && (
                    <AdminsTable admins={admins} onRowClick={openEditModal} onToggleStatus={toggleAdminStatus} />
                )}

                {editing && selectedAdmin && (
                    <Modal isOpen={editing} onClose={closeEditModal} title={`Edit Admin: ${selectedAdmin.username}`}>
                        {error && (
                            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                                {error}
                            </div>
                        )}
                        <form onSubmit={updateAdmin} className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <FormInput label="First Name" name="first_name" type="text" value={editForm.first_name} onChange={(e) => setEditForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))} required />
                                <FormInput label="Last Name" name="last_name" type="text" value={editForm.last_name} onChange={(e) => setEditForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))} required />
                            </div>
                            <FormInput label="Email" name="email" type="email" value={editForm.email} onChange={(e) => setEditForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))} required />
                            <FormInput label="New Password" name="password" type="password" value={editForm.password} onChange={(e) => setEditForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))} placeholder="Leave blank to keep current password" />
                            <div className="flex gap-3 pt-2">
                                <SubmitButton type="submit">Save Changes</SubmitButton>
                                <button type="button" onClick={closeEditModal} className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300">Cancel</button>
                            </div>
                        </form>
                    </Modal>
                )}
            </Card>
        </div>
    );
}
