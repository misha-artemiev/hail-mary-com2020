import React from "react";

// Generic profile info row
function Info({ label, value }) {
    return (
        <p>
            <strong>{label}:</strong> {value}
        </p>
    );
}

export default function Profile() {
    const handleEdit = () => {
        // TODO: add edit profile
        alert("Clicked");
    };

    return (
        <>
            <h1>Profile</h1>

            <button onClick={handleEdit}>Edit Profile</button>

            {/* Profile information */}
            <div>
                <Info label="Display Name" value="User0001" />
                <Info label="Current rescue streak" value="0 weeks" />
                <Info label="Bundles rescued" value="0" />
            </div>

            <hr />

            {/* Badge information */}
            <h2>Badges</h2>
            <p>No badges yet...!</p>
        </>
    );
}
