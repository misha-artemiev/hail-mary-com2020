import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

const defaultIcon = L.icon({
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    iconRetinaUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
});

L.Marker.prototype.options.icon = defaultIcon;

function LocationMarker({ position, onPositionChange }) {
    useMapEvents({
        click(e) {
            onPositionChange({ lat: e.latlng.lat, lng: e.latlng.lng });
        },
    });

    return position ? <Marker position={[position.lat, position.lng]} /> : null;
}

export default function LocationPicker({
    value,
    onChange,
    label = "Pick Location on Map",
    required = false,
}) {
    const [position, setPosition] = useState(value || null);

    useEffect(() => {
        if (value) {
            setPosition(value);
        }
    }, [value]);

    const handlePositionChange = (newPosition) => {
        setPosition(newPosition);
        onChange(newPosition);
    };

    const center = position ? [position.lat, position.lng] : [51.505, -0.09];

    return (
        <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
                {label}
                {required && <span className="text-red-500"> *</span>}
            </label>
            <p className="text-xs text-gray-500">
                Click on the map to set your location
            </p>
            <div className="h-64 rounded-lg overflow-hidden border border-gray-300">
                <MapContainer
                    center={center}
                    zoom={13}
                    style={{ height: "100%", width: "100%" }}
                    scrollWheelZoom={true}
                >
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    <LocationMarker
                        position={position}
                        onPositionChange={handlePositionChange}
                    />
                </MapContainer>
            </div>
        </div>
    );
}
