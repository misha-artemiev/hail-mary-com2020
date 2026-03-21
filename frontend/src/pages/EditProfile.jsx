/**
 * EditProfile.jsx
 * @author Ed Brown
 */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

// Components
import Card from "../components/Card";
import Button from "../components/forms/Button";
import SubmitButton from "../components/forms/SubmitButton";

// Resources
import defaultProfile from "../assets/default-user.jpg";

export default function EditProfile({ role = "consumer" }) {
    const navigate = useNavigate();
    // Form state
    const [email, setEmail] = useState("");
    const [profileImage, setProfileImage] = useState(defaultProfile);

    // Seller fields
    const [sellerName, setSellerName] = useState("SellerExample");
    const [address, setAddress] = useState({
        address_line1: "",
        address_line2: "",
        city: "",
        postcode: "",
        region: "",
    });

    // Consumer fields
    const [fName, setFName] = useState("User");
    const [lName, setLName] = useState("Example");

    // Password fields
    const [oldPassword, setOldPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");

    // Handles profile image changes
    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setProfileImage(file);
    };

    const handleAddressChange = (e) => {
        const { name, value } = e.target;
        setAddress((prev) => ({ ...prev, [name]: value }));
    };

    // Handles profile form submission
    const handleProfileSubmit = (e) => {
        e.preventDefault();

        let updatedProfile = {
            profileImage,
            email,
        };

        if (role === "seller") {
            updatedProfile = {
                ...updatedProfile,
                sellerName: sellerName,
                address,
            };
        }

        if (role === "consumer") {
            updatedProfile = {
                ...updatedProfile,
                fName,
                lName,
            };
        }

        console.log("Updated profile:", updatedProfile);
        alert("Profile updated");
        navigate("/profile");
    };

    // Handles password form submission
    const handlePasswordSubmit = (e) => {
        e.preventDefault();

        console.log("Password change:", { oldPassword, newPassword });
        alert("Password updated");
        setOldPassword("");
        setNewPassword("");
    };

    //Handles cancel button
    const handleCancel = () => {
        navigate("/profile");
    };

    return (
        <div className="max-w-3xl mx-auto p-4 md:p-6">
            <Card>
                <h1 className="text-3xl font-bold text-green-700 mb-6">
                    Edit Profile
                </h1>

                {/* SELLER FORM */}
                {role === "seller" && (
                    <form onSubmit={handleProfileSubmit} className="space-y-6">
                        {/* Profile Image */}
                        <div className="flex justify-center">
                            <label className="cursor-pointer relative">
                                <div className="w-32 h-32 rounded-full overflow-hidden border-2 border-green-600">
                                    <img
                                        src={
                                            profileImage instanceof File
                                                ? URL.createObjectURL(
                                                      profileImage,
                                                  )
                                                : profileImage
                                        }
                                        alt="Profile"
                                        className="w-full h-full object-cover"
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

                        {/* Email */}
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

                            {Object.keys(address).map((field) => (
                                <input
                                    key={field}
                                    name={field}
                                    placeholder={field.replace("_", " ")}
                                    value={address[field]}
                                    onChange={handleAddressChange}
                                    className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                                />
                            ))}
                        </div>

                        {/* Buttons */}
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
                        {/* Profile Info Form */}
                        <form
                            onSubmit={handleProfileSubmit}
                            className="space-y-6"
                        >
                            <h2 className="text-xl font-semibold text-gray-800">
                                Personal Information
                            </h2>

                            {/* Profile Image */}
                            <div className="flex justify-center">
                                <label className="cursor-pointer relative">
                                    <div className="w-32 h-32 rounded-full overflow-hidden border-2 border-green-600">
                                        <img
                                            src={
                                                profileImage instanceof File
                                                    ? URL.createObjectURL(
                                                          profileImage,
                                                      )
                                                    : profileImage
                                            }
                                            alt="Profile"
                                            className="w-full h-full object-cover"
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

                        {/* Password Form */}
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
