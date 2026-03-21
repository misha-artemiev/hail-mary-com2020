import React, { useState } from "react";
import { MapContainer, TileLayer, Marker } from "react-leaflet";
import L from "leaflet";
import useSellerProfile from "../hooks/useSellerProfile";
import { useUserImage } from "../hooks/useUserImage";
import Card from "./Card";
import Button from "./forms/Button";
import defaultProfile from "../assets/default-user.jpg";
import SellerProfileEditForm from "./SellerProfileEditForm";

const markerIcon = L.icon({
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    iconRetinaUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
});

export default function SellerProfileCard({ onLogout }) {
    const {
        profile,
        loading,
        error,
        refetch,
        updateProfile,
        updateImage,
        updateEmail,
        updatePassword,
    } = useSellerProfile();
    const { imageUrl } = useUserImage();
    const [isEditing, setIsEditing] = useState(false);

    const [emailForm, setEmailForm] = useState("");
    const [oldPassword, setOldPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [emailSuccess, setEmailSuccess] = useState("");
    const [emailError, setEmailError] = useState("");
    const [passwordSuccess, setPasswordSuccess] = useState("");
    const [passwordError, setPasswordError] = useState("");

    const handleSave = async (formData, newImage) => {
        await updateProfile(formData);
        if (newImage) {
            await updateImage(newImage);
        }
        setIsEditing(false);
        refetch();
    };

    const handleEmailSubmit = async (e) => {
        e.preventDefault();
        setEmailError("");
        setEmailSuccess("");

        try {
            await updateEmail(emailForm);
            setEmailSuccess("Email updated");
            setEmailForm("");
            refetch();
        } catch (err) {
            setEmailError(err.message || "Failed to update email");
        }
    };

    const handlePasswordSubmit = async (e) => {
        e.preventDefault();
        setPasswordError("");
        setPasswordSuccess("");

        try {
            await updatePassword(oldPassword, newPassword);
            setPasswordSuccess("Password updated");
            setOldPassword("");
            setNewPassword("");
        } catch (err) {
            setPasswordError(err.message || "Failed to update password");
        }
    };

    if (loading) {
        return (
            <Card className="mb-6">
                <p className="text-gray-500 text-center py-4">
                    Loading profile...
                </p>
            </Card>
        );
    }

    if (error || !profile) {
        return (
            <Card className="mb-6">
                <p className="text-red-500 text-center py-4">
                    {error ?? "Profile not found"}
                </p>
            </Card>
        );
    }

    const hasLocation = profile.latitude && profile.longitude;
    const center = hasLocation
        ? [profile.latitude, profile.longitude]
        : [51.505, -0.09];

    return (
        <Card className="mb-6">
            <div className="flex justify-between items-center mb-4 gap-4">
                <div className="flex-1">
                    <h2 className="text-xl font-bold text-green-700 mb-2">
                        {profile.seller_name}
                    </h2>
                    <div className="text-sm text-gray-600 space-y-1">
                        <div className="flex gap-2">
                            <span className="font-semibold w-32">Name:</span>
                            <span>{profile.seller_name}</span>
                        </div>
                        <div className="flex gap-2">
                            <span className="font-semibold w-32">
                                Address Line 1:
                            </span>
                            <span>{profile.address_line1}</span>
                        </div>
                        <div className="flex gap-2">
                            <span className="font-semibold w-32">
                                Address Line 2:
                            </span>
                            <span>{profile.address_line2 || "-"}</span>
                        </div>
                        <div className="flex gap-2">
                            <span className="font-semibold w-32">City:</span>
                            <span>{profile.city}</span>
                        </div>
                        {profile.region && (
                            <div className="flex gap-2">
                                <span className="font-semibold w-32">
                                    Region:
                                </span>
                                <span>{profile.region}</span>
                            </div>
                        )}
                        <div className="flex gap-2">
                            <span className="font-semibold w-32">
                                Post Code:
                            </span>
                            <span>{profile.post_code}</span>
                        </div>
                        <div className="flex gap-2">
                            <span className="font-semibold w-32">Country:</span>
                            <span>{profile.country}</span>
                        </div>
                    </div>
                </div>

                <div className="flex justify-center">
                    <img
                        src={imageUrl || defaultProfile}
                        alt={profile.seller_name}
                        className="w-30 h-30 rounded-full object-cover border-2 border-green-600"
                        onError={(e) => {
                            e.target.src = defaultProfile;
                        }}
                    />
                </div>

                <div className="flex-1 flex justify-end items-center gap-2">
                    <div className="flex gap-2 w-fit">
                        <Button
                            onClick={() =>
                                isEditing
                                    ? setIsEditing(false)
                                    : setIsEditing(true)
                            }
                            variant={isEditing ? "danger" : undefined}
                        >
                            {isEditing ? "Cancel" : "Edit"}
                        </Button>
                        <Button onClick={onLogout} variant="danger">
                            Logout
                        </Button>
                    </div>
                </div>
            </div>

            {hasLocation && (
                <div className="w-full h-40 rounded-lg overflow-hidden border border-gray-300 mt-4">
                    <MapContainer
                        center={center}
                        zoom={15}
                        style={{ height: "100%", width: "100%" }}
                        scrollWheelZoom={false}
                        dragging={false}
                        zoomControl={false}
                    >
                        <TileLayer
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                        <Marker position={center} icon={markerIcon} />
                    </MapContainer>
                </div>
            )}

            {isEditing && (
                <>
                    <SellerProfileEditForm
                        profile={profile}
                        imageUrl={imageUrl}
                        defaultProfile={defaultProfile}
                        onSave={handleSave}
                    />

                    <hr className="my-6 border-gray-200" />

                    <form onSubmit={handleEmailSubmit} className="space-y-4">
                        <h3 className="text-lg font-semibold text-gray-800">
                            Change Email
                        </h3>

                        {emailError && (
                            <div className="p-3 rounded bg-red-100 text-red-700 font-semibold">
                                {emailError}
                            </div>
                        )}

                        {emailSuccess && (
                            <div className="p-3 rounded bg-green-100 text-green-700 font-semibold">
                                {emailSuccess}
                            </div>
                        )}

                        <div>
                            <label className="block text-sm font-medium mb-1">
                                New Email
                            </label>
                            <input
                                type="email"
                                value={emailForm}
                                onChange={(e) => setEmailForm(e.target.value)}
                                required
                                className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                            />
                        </div>

                        <div className="flex justify-end">
                            <button
                                type="submit"
                                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                            >
                                Update Email
                            </button>
                        </div>
                    </form>

                    <hr className="my-6 border-gray-200" />

                    <form onSubmit={handlePasswordSubmit} className="space-y-4">
                        <h3 className="text-lg font-semibold text-gray-800">
                            Change Password
                        </h3>

                        {passwordError && (
                            <div className="p-3 rounded bg-red-100 text-red-700 font-semibold">
                                {passwordError}
                            </div>
                        )}

                        {passwordSuccess && (
                            <div className="p-3 rounded bg-green-100 text-green-700 font-semibold">
                                {passwordSuccess}
                            </div>
                        )}

                        <div>
                            <label className="block text-sm font-medium mb-1">
                                Old Password
                            </label>
                            <input
                                type="password"
                                value={oldPassword}
                                onChange={(e) => setOldPassword(e.target.value)}
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
                                onChange={(e) => setNewPassword(e.target.value)}
                                required
                                className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                            />
                        </div>

                        <div className="flex justify-end">
                            <button
                                type="submit"
                                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                            >
                                Update Password
                            </button>
                        </div>
                    </form>
                </>
            )}
        </Card>
    );
}
