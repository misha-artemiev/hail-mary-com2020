import React, { useState } from "react";
import FormInput from "./forms/FormInput";
import SubmitButton from "./forms/SubmitButton";
import Button from "./forms/Button";
import LocationPicker from "./LocationPicker";

export default function SellerProfileEditForm({ profile, onSave, onCancel }) {
    const [formData, setFormData] = useState({
        address_line1: profile.address_line1 ?? "",
        address_line2: profile.address_line2 ?? "",
        city: profile.city ?? "",
        region: profile.region ?? "",
        post_code: profile.post_code ?? "",
        country: profile.country ?? "",
        latitude: profile.latitude ?? null,
        longitude: profile.longitude ?? null,
    });
    const [newImage, setNewImage] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);

    const handleInputChange = (field, value) => {
        setFormData((prev) => ({ ...prev, [field]: value }));
    };

    const handleLocationChange = (location) => {
        setFormData((prev) => ({
            ...prev,
            latitude: location.lat,
            longitude: location.lng,
        }));
    };

    const handleImageChange = (e) => {
        const file = e.target.files?.[0];
        if (file) {
            setNewImage(file);
            setPreviewUrl(URL.createObjectURL(file));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSaving(true);

        try {
            await onSave(formData, newImage);
        } catch (err) {
            setError(err.message);
        } finally {
            setSaving(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
            {error && (
                <div className="text-red-600 text-sm bg-red-50 p-2 rounded">
                    {error}
                </div>
            )}

            <div className="flex flex-col items-center">
                <label className="cursor-pointer">
                    <div className="w-20 h-20 rounded-full overflow-hidden border-2 border-green-600">
                        <img
                            src={previewUrl ?? profile.profile_image}
                            alt="Profile"
                            className="w-full h-full object-cover"
                        />
                    </div>
                    <span className="block text-xs text-green-600 mt-1 text-center">
                        Change Photo
                    </span>
                    <input
                        type="file"
                        accept="image/*"
                        onChange={handleImageChange}
                        className="hidden"
                    />
                </label>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormInput
                    label="Address Line 1"
                    name="address_line1"
                    value={formData.address_line1}
                    onChange={(e) =>
                        handleInputChange("address_line1", e.target.value)
                    }
                    required
                />
                <FormInput
                    label="Address Line 2"
                    name="address_line2"
                    value={formData.address_line2}
                    onChange={(e) =>
                        handleInputChange("address_line2", e.target.value)
                    }
                />
                <FormInput
                    label="City"
                    name="city"
                    value={formData.city}
                    onChange={(e) => handleInputChange("city", e.target.value)}
                    required
                />
                <FormInput
                    label="Region / County"
                    name="region"
                    value={formData.region}
                    onChange={(e) =>
                        handleInputChange("region", e.target.value)
                    }
                />
                <FormInput
                    label="Post Code"
                    name="post_code"
                    value={formData.post_code}
                    onChange={(e) =>
                        handleInputChange("post_code", e.target.value)
                    }
                    required
                />
                <FormInput
                    label="Country"
                    name="country"
                    value={formData.country}
                    onChange={(e) =>
                        handleInputChange("country", e.target.value)
                    }
                    required
                />
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Pickup Location
                </label>
                <LocationPicker
                    value={
                        formData.latitude && formData.longitude
                            ? {
                                  lat: formData.latitude,
                                  lng: formData.longitude,
                              }
                            : null
                    }
                    onChange={handleLocationChange}
                    label=""
                />
            </div>

            <div className="flex justify-end gap-2 pt-2">
                <Button type="button" onClick={onCancel} disabled={saving}>
                    Cancel
                </Button>
                <SubmitButton disabled={saving}>
                    {saving ? "Saving..." : "Save Changes"}
                </SubmitButton>
            </div>
        </form>
    );
}
