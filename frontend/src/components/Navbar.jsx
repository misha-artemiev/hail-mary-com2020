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
        <nav style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <NavLink to="/">Home</NavLink>

            {/* Profile picture */}
            <NavLink to="/profile" style={{ marginLeft: "auto" }}>
                <img
                    src={user.profilePic}
                    alt={`${user.displayName}'s profile`}
                    style={{
                        width: "40px",
                        height: "40px",
                        borderRadius: "50%",
                        objectFit: "cover",
                        border: "2px solid #4CAF50",
                        cursor: "pointer",
                    }}
                />
            </NavLink>
        </nav>
    );
}
