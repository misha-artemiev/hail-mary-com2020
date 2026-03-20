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
        <Card className="mb-6">
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                    <img
                        src={imageUrl || defaultProfile}
                        alt={profile.seller_name}
                        className="w-16 h-16 rounded-full object-cover"
                        onError={(e) => {
                            e.target.src = defaultProfile;
                        }}
                    />
                    <div>
                        <h2 className="text-xl font-bold text-green-700">
                            {profile.seller_name}
                        </h2>
                        <div className="text-sm text-gray-600">
                            <p>{profile.address_line1}</p>
                            {profile.address_line2 && (
                                <p>{profile.address_line2}</p>
                            )}
                            <p>
                                {profile.city}
                                {profile.region && `, ${profile.region}`}
                                {profile.post_code && `, ${profile.post_code}`}
                            </p>
                            <p>{profile.country}</p>
                        </div>
                    </div>
                </div>
                <div className="flex flex-col gap-2">
                    {!isEditing && (
                        <Button onClick={() => setIsEditing(true)}>Edit</Button>
                    )}
                    <Button onClick={onLogout} variant="danger">
                        Logout
                    </Button>
                </div>
            </div>

            {hasLocation && (
                <div className="w-full h-40 rounded-lg overflow-hidden border border-gray-300">
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
                    onSave={handleSave}
                    onCancel={handleCancel}
                />
            )}
        </Card>
    );
}
