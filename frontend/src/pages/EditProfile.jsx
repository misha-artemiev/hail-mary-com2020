/**
 * EditProfile.jsx
 * @author Ed Brown
 */

import React, {useState} from "react";
import { useNavigate } from "react-router-dom";

// Components
import Card from "../components/Card";

// Resources
import defaultProfile from "../assets/default-user.jpg";

export default function EditProfile({ role = "consumer"}) {
    const navigate = useNavigate();
    // Form state
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
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
    
    // Handles profile image changes
    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setProfileImage(file);
    };

    const handleAddressChange = (e) => {
        const { name, value } = e.target;
        setAddress((prev) => ({ ...prev, [name]: value}));
    };

    // Handles form submission
    const handleSubmit = (e) => {
        e.preventDefault();

        let updatedProfile = {
            profileImage,
            email,
            password,
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
        //REPLACE WITH API CALL HERE
        navigate("/profile");
    };

    //Handles cancel button
    const handleCancel = () => {
        navigate("/profile");
    };

    return (
        <div className="max-w-3xl mx-auto p-6">
            <Card>
                <h1 className="text-3xl font-bold text-green-700 mb-6">
                    Edit Profile
                </h1>

                <form onSubmit={handleSubmit} className="space-y-6">

                    {/* Profile Image */}
                    <div className="flex flex-col items-center">
                        <img
                            src={
                                profileImage instanceof File
                                    ? URL.createObjectURL(profileImage)
                                    : profileImage
                            }
                            alt="Profile"
                            className="w-32 h-32 rounded-full mb-4 object-cover"
                        />

                        <label className="cursor-pointer bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:ring-2 focus:ring-green-500">
                            Change Picture
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handleImageChange}
                                className="hidden"
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

                    {/* Password */}
                    <div>
                        <label className="block text-sm font-medium mb-1">
                            Password
                        </label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                        />
                    </div>

                    {/* SELLER FIELDS */}
                    {role === "seller" && (
                        <>
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
                                <h2 className="text-lg font-semibold">
                                    Address
                                </h2>

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
                        </>
                    )}

                    {/* CONSUMER FIELDS */}
                    {role === "consumer" && (
                        <>
                            <div>
                                <label className="block text-sm font-medium mb-1">
                                    First Name
                                </label>
                                <input
                                    type="text"
                                    value={fName}
                                    onChange={(e) => setFName(e.target.value)}
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
                                    onChange={(e) => setLName(e.target.value)}
                                    required
                                    className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                                />
                            </div>
                        </>
                    )}

                    {/* Buttons */}
                    <div className="flex justify-end space-x-4">
                        <button
                            type="button"
                            onClick={handleCancel}
                            className="px-4 py-2 border rounded-md hover:bg-gray-100"
                        >
                            Cancel
                        </button>

                        <button
                            type="submit"
                            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:ring-2 focus:ring-green-500"
                        >
                            Save Changes
                        </button>
                    </div>
                </form>
            </Card>
        </div>
    );
}