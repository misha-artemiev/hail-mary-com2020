import { useState, useEffect } from "react";
import { getAuthToken } from "../services/authService";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export default function useConsumerProfile() {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchProfile = async () => {
        const token = getAuthToken();
        if (!token) {
            setError("Not authenticated");
            setLoading(false);
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${API_BASE_URL}/consumers/me`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                setProfile(data);
            } else {
                setError(`Failed to load profile (${response.status})`);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const updateProfile = async (profileData) => {
        const token = getAuthToken();
        if (!token) {
            throw new Error("Not authenticated");
        }

        const response = await fetch(`${API_BASE_URL}/consumers/me`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(profileData),
        });

        if (!response.ok) {
            const data = await response.json().catch(() => null);
            throw new Error(data?.detail ?? "Failed to update profile");
        }

        return response.json();
    };

    const updateImage = async (file) => {
        const token = getAuthToken();
        if (!token) {
            throw new Error("Not authenticated");
        }

        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(`${API_BASE_URL}/users/me/image`, {
            method: "PATCH",
            headers: {
                Authorization: `Bearer ${token}`,
            },
            body: formData,
        });

        if (!response.ok) {
            throw new Error("Failed to update image");
        }
    };

    const updateEmail = async (email) => {
        const token = getAuthToken();
        if (!token) {
            throw new Error("Not authenticated");
        }

        const response = await fetch(
            `${API_BASE_URL}/users/me/email?email=${encodeURIComponent(email)}`,
            {
                method: "PATCH",
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            },
        );

        if (!response.ok) {
            const data = await response.json().catch(() => null);
            throw new Error(data?.detail ?? "Failed to update email");
        }
    };

    const updatePassword = async (oldPassword, newPassword) => {
        const token = getAuthToken();
        if (!token) {
            throw new Error("Not authenticated");
        }

        const response = await fetch(`${API_BASE_URL}/users/me/password`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
                old_password: oldPassword,
                new_password: newPassword,
            }),
        });

        if (!response.ok) {
            const data = await response.json().catch(() => null);
            throw new Error(data?.detail ?? "Failed to update password");
        }
    };

    useEffect(() => {
        fetchProfile();
    }, []);

    return {
        profile,
        loading,
        error,
        refetch: fetchProfile,
        updateProfile,
        updateImage,
        updateEmail,
        updatePassword,
    };
}
