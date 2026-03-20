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
    const { profile, loading, error, refetch, updateProfile, updateImage } =
        useSellerProfile();
    const { imageUrl } = useUserImage();
    const [isEditing, setIsEditing] = useState(false);

    const handleSave = async (formData, newImage) => {
        await updateProfile(formData);
        if (newImage) {
            await updateImage(newImage);
        }
        setIsEditing(false);
        refetch();
    };

    const handleCancel = () => {
        setIsEditing(false);
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
        <Card className="mb-6 relative">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h2 className="text-xl font-bold text-green-700 mb-2">
                        {profile.seller_name}
                    </h2>
                    <div className="text-sm text-gray-600 space-y-1">
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
                <div className="flex items-center gap-2">
                    {!isEditing && (
                        <Button onClick={() => setIsEditing(true)}>Edit</Button>
                    )}
                    <Button onClick={onLogout} variant="danger">
                        Logout
                    </Button>
                </div>
            </div>

            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
                <img
                    src={imageUrl || defaultProfile}
                    alt={profile.seller_name}
                    className="w-24 h-24 rounded-full object-cover border-2 border-green-600"
                    onError={(e) => {
                        e.target.src = defaultProfile;
                    }}
                />
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
                <SellerProfileEditForm
                    profile={profile}
                    imageUrl={imageUrl}
                    defaultProfile={defaultProfile}
                    onSave={handleSave}
                    onCancel={handleCancel}
                />
            )}
        </Card>
    );
}
