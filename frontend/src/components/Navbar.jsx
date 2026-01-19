import React from "react";
import { NavLink } from "react-router-dom";

// Default profile picture
import defaultProfile from "../assets/default-user.jpg";

export default function Navbar() {
    const user = {
        displayName: "User0001",
        profilePic: defaultProfile,
    };

    return (
        <nav className="bg-green-600 text-white px-6 py-4 flex justify-between items-center shadow-md">
            <NavLink to="/" className="font-bold text-xl">
                RescueMarket
            </NavLink>

            {/* Profile picture */}
            <NavLink to="/profile">
                <img
                    src={user.profilePic}
                    alt={`${user.displayName}'s profile`}
                    className="w-10 h-10 rounded-full hover:scale-110 transition"
                />
            </NavLink>
        </nav>
    );
}
