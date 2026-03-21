/**
 * EditProfile.jsx
 * @author Ed Brown
 */

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

// Components
import Card from "../components/Card";
import Button from "../components/forms/Button";
import SubmitButton from "../components/forms/SubmitButton";

// Hooks
import useConsumerProfile from "../hooks/useConsumerProfile";
import { useUserImage } from "../hooks/useUserImage";

// Resources
import defaultProfile from "../assets/default-user.jpg";

export default function EditProfile({ role = "consumer" }) {
    const navigate = useNavigate();
    const {
        profile,
        loading,
        error,
        refetch,
        updateProfile,
        updateImage,
        updateEmail,
        updatePassword,
    } = useConsumerProfile();
    const { imageUrl } = useUserImage();

    // Form state
    const [email, setEmail] = useState("");
    const [newProfileImage, setNewProfileImage] = useState(null);
    const [displayImage, setDisplayImage] = useState(defaultProfile);

    // Consumer fields
    const [fName, setFName] = useState("");
    const [lName, setLName] = useState("");

    // Password fields
    const [oldPassword, setOldPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");

    // Feedback state
    const [success, setSuccess] = useState("");
    const [formError, setFormError] = useState("");

    // Seller fields
    const [sellerName, setSellerName] = useState("");
    const [address, setAddress] = useState({
        address_line1: "",
        address_line2: "",
        city: "",
        postcode: "",
        region: "",
    });

    useEffect(() => {
        if (profile) {
            if (role === "consumer") {
                setFName(profile.fname || "");
                setLName(profile.lname || "");
                setEmail(profile.email || "");
            } else if (role === "seller") {
                setSellerName(profile.seller_name || "");
                setEmail(profile.email || "");
                setAddress({
                    address_line1: profile.address_line1 || "",
                    address_line2: profile.address_line2 || "",
                    city: profile.city || "",
                    postcode: profile.post_code || "",
                    region: profile.region || "",
                });
            }
        }
    }, [profile, role]);

    useEffect(() => {
        if (imageUrl) {
            setDisplayImage(imageUrl);
        }
    }, [imageUrl]);

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setNewProfileImage(file);
        setDisplayImage(URL.createObjectURL(file));
    };

    const handleAddressChange = (e) => {
        const { name, value } = e.target;
        setAddress((prev) => ({ ...prev, [name]: value }));
    };

    const handleProfileSubmit = async (e) => {
        e.preventDefault();
        setFormError("");
        setSuccess("");

        try {
            if (role === "consumer") {
                await updateProfile({
                    first_name: fName,
                    last_name: lName,
                });

                if (email !== profile.email) {
                    await updateEmail(email);
                }
            } else if (role === "seller") {
                await updateProfile({
                    seller_name: sellerName,
                    address_line1: address.address_line1,
                    address_line2: address.address_line2,
                    city: address.city,
                    post_code: address.postcode,
                    region: address.region,
                });
            }

            if (newProfileImage) {
                await updateImage(newProfileImage);
            }

            setSuccess("Profile updated");
            refetch();
            setTimeout(() => navigate("/profile"), 1000);
        } catch (err) {
            setFormError(err.message || "Failed to update profile");
        }
    };

    const handlePasswordSubmit = async (e) => {
        e.preventDefault();
        setFormError("");
        setSuccess("");

        try {
            await updatePassword(oldPassword, newPassword);
            setSuccess("Password updated");
            setOldPassword("");
            setNewPassword("");
        } catch (err) {
            setFormError(err.message || "Failed to update password");
        }
    };

    const handleCancel = () => {
        navigate("/profile");
    };

    if (loading) {
        return (
            <div className="max-w-3xl mx-auto p-4 md:p-6">
                <Card>
                    <p className="text-gray-500 text-center py-4">
                        Loading profile...
                    </p>
                </Card>
            </div>
        );
    }

    if (error || !profile) {
        return (
            <div className="max-w-3xl mx-auto p-4 md:p-6">
                <Card>
                    <p className="text-red-500 text-center py-4">
                        {error ?? "Profile not found"}
                    </p>
                </Card>
            </div>
        );
    }

    return (
        <div className="max-w-3xl mx-auto p-4 md:p-6">
            <Card>
                <div className="relative mb-6">
                    <h1 className="text-3xl font-bold text-green-700">
                        Edit Profile
                    </h1>
                    <div className="absolute top-0 right-0">
                        <Button onClick={handleCancel} variant="danger">
                            Back
                        </Button>
                    </div>
                </div>

                {formError && (
                    <div className="mb-4 p-3 rounded bg-red-100 text-red-700 font-semibold">
                        {formError}
                    </div>
                )}

                {success && (
                    <div className="mb-4 p-3 rounded bg-green-100 text-green-700 font-semibold">
                        {success}
                    </div>
                )}

                {/* SELLER FORM */}
                {role === "seller" && (
                    <form onSubmit={handleProfileSubmit} className="space-y-6">
                        <div className="flex justify-center">
                            <label className="cursor-pointer relative">
                                <div className="w-32 h-32 rounded-full overflow-hidden border-2 border-green-600">
                                    <img
                                        src={displayImage}
                                        alt="Profile"
                                        className="w-full h-full object-cover"
                                        onError={(e) => {
                                            e.target.src = defaultProfile;
                                        }}
                                    />
                                    <div className="absolute inset-0 rounded-full bg-black/50 flex items-center justify-center opacity-100">
                                        <span className="text-white text-sm font-medium">
                                            Change
                                        </span>
                                    </div>
                                </div>
                                <input
                                    type="file"
                                    accept="image/*"
                                    onChange={handleImageChange}
                                    className="absolute inset-0 opacity-0 cursor-pointer"
                                />
                            </label>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-1">
                                Email
                            </label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-1">
                                Seller Name
                            </label>
                            <input
                                type="text"
                                value={sellerName}
                                onChange={(e) => setSellerName(e.target.value)}
                                required
                                className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                            />
                        </div>

                        <div className="space-y-2">
                            <h2 className="text-lg font-semibold">Address</h2>

                            <input
                                name="address_line1"
                                placeholder="Address Line 1"
                                value={address.address_line1}
                                onChange={handleAddressChange}
                                className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                            />
                            <input
                                name="address_line2"
                                placeholder="Address Line 2"
                                value={address.address_line2}
                                onChange={handleAddressChange}
                                className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                            />
                            <input
                                name="city"
                                placeholder="City"
                                value={address.city}
                                onChange={handleAddressChange}
                                className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                            />
                            <input
                                name="postcode"
                                placeholder="Post Code"
                                value={address.postcode}
                                onChange={handleAddressChange}
                                className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                            />
                            <input
                                name="region"
                                placeholder="Region"
                                value={address.region}
                                onChange={handleAddressChange}
                                className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                            />
                        </div>

                        <div className="flex justify-end space-x-4">
                            <Button
                                onClick={handleCancel}
                                className="px-6 py-2.5 w-auto"
                            >
                                Cancel
                            </Button>
                            <SubmitButton className="px-6 py-2.5 w-auto">
                                Save Changes
                            </SubmitButton>
                        </div>
                    </form>
                )}

                {/* CONSUMER FORMS */}
                {role === "consumer" && (
                    <div className="space-y-8">
                        <form
                            onSubmit={handleProfileSubmit}
                            className="space-y-6"
                        >
                            <div className="flex justify-center">
                                <label className="cursor-pointer relative">
                                    <div className="w-32 h-32 rounded-full overflow-hidden border-2 border-green-600">
                                        <img
                                            src={displayImage}
                                            alt="Profile"
                                            className="w-full h-full object-cover"
                                            onError={(e) => {
                                                e.target.src = defaultProfile;
                                            }}
                                        />
                                        <div className="absolute inset-0 rounded-full bg-black/50 flex items-center justify-center opacity-100">
                                            <span className="text-white text-sm font-medium">
                                                Change
                                            </span>
                                        </div>
                                    </div>
                                    <input
                                        type="file"
                                        accept="image/*"
                                        onChange={handleImageChange}
                                        className="absolute inset-0 opacity-0 cursor-pointer"
                                    />
                                </label>
                            </div>

                            <h2 className="text-xl font-semibold text-gray-800">
                                Personal Information
                            </h2>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">
                                        First Name
                                    </label>
                                    <input
                                        type="text"
                                        value={fName}
                                        onChange={(e) =>
                                            setFName(e.target.value)
                                        }
                                        required
                                        className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-1">
                                        Last Name
                                    </label>
                                    <input
                                        type="text"
                                        value={lName}
                                        onChange={(e) =>
                                            setLName(e.target.value)
                                        }
                                        required
                                        className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-1">
                                    Email
                                </label>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                                />
                            </div>

                            <div className="flex justify-end">
                                <SubmitButton className="px-6 py-2.5 w-auto">
                                    Save Changes
                                </SubmitButton>
                            </div>
                        </form>

                        <hr className="border-gray-200" />

                        <form
                            onSubmit={handlePasswordSubmit}
                            className="space-y-6"
                        >
                            <h2 className="text-xl font-semibold text-gray-800">
                                Change Password
                            </h2>

                            <div>
                                <label className="block text-sm font-medium mb-1">
                                    Old Password
                                </label>
                                <input
                                    type="password"
                                    value={oldPassword}
                                    onChange={(e) =>
                                        setOldPassword(e.target.value)
                                    }
                                    required
                                    className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-1">
                                    New Password
                                </label>
                                <input
                                    type="password"
                                    value={newPassword}
                                    onChange={(e) =>
                                        setNewPassword(e.target.value)
                                    }
                                    required
                                    className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                                />
                            </div>

                            <div className="flex justify-end">
                                <SubmitButton className="px-6 py-2.5 w-auto">
                                    Update Password
                                </SubmitButton>
                            </div>
                        </form>
                    </div>
                )}
            </Card>
        </div>
    );
}
