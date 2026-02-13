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

export default function EditProfile() {
    // Form state
    const [displayName, setDisplayName] = useState("UserExample");
    const [profileImage, setProfileImage] = useState(defaultProfile);

    // Handles profile image changes
    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setProfileImage(file);
    };

    // Handles form submission
    const handleSubmit = (e) => {
        e.preventDefault();

        //REPLACE WITH API CALL HERE
        const updatedProfile = {
            displayName,
            profileImage,
        };

        console.log("Updated profile:", updatedProfile);
        alert("Profile updated");
    };

    //Handles cancel button
    const navigate = useNavigate();
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
                    {/* Profile Image Preview */}
                    <div className="flex flex-col items-center">
                        <img
                            src={profileImage}
                            alt="Profile Preview"
                            className="w-32 h-32 rounded-full mb-4 object-cover"
                        />

                        <label className="cursor-pointer bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500">
                            Change Picture
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handleImageChange}
                                className="hidden"
                            />
                        </label>
                    </div>

                    {/* Display Name */}
                    <div>
                        <label
                            htmlFor="displayName"
                            className="block text-sm font-medium text-gray-700 mb-1"
                        >
                            Display Name
                        </label>
                        <input
                            id="displayName"
                            type="text"
                            value={displayName}
                            onChange={(e) => setDisplayName(e.target.value)}
                            required
                            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                        />
                    </div>

                    {/* Buttons */}
                    <div className="flex justify-end space-x-4">
                        <button
                            type="button"
                            onClick={handleCancel}
                            className="px-4 py-2 rounded-md border border-gray-300 hover:bg-gray-100"
                        >
                            Cancel
                        </button>

                        <button
                            type="submit"
                            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                        >
                            Save Changes
                        </button>
                    </div>
                </form>
            </Card>
        </div>
    );
}