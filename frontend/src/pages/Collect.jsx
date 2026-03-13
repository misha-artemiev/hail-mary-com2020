/**
 * Collect.jsx
 * @author Thomas Noakes
 */

import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

// Authentication
import { useAuth } from "../context/AuthContext";

// Hooks
import { useCollectReservation } from "../hooks/useCollectReservation";

// Components
import Card from "../components/Card";
import FormInput from "../components/forms/FormInput";
import Button from "../components/forms/Button";
import SubmitButton from "../components/forms/SubmitButton";

export default function Collect() {
    const { id } = useParams();
    const { userRole } = useAuth();

    const navigate = useNavigate();

    const { collecting, collectSuccess, handleCollect, reset } =
        useCollectReservation(id);

    // State object: stores the current claim code
    const [claimCode, setClaimCode] = useState("");

    /**
     * Handles submitting the claim code.
     */
    const handleSubmit = (e) => {
        e.preventDefault();
        handleCollect(claimCode);
    };

    /**
     * Handles resetting the
     */
    const handleReset = () => {
        setClaimCode("");
        reset();
    };

    // Not accessible if the user is a consumer
    if (userRole !== "seller") {
        return (
            <div className="max-w-4xl mx-auto p-4 md:p-6">
                <Card className="flex flex-col items-centre text-center gap-6">
                    {/* Header */}
                    <h1 className="text-3xl font-bold text-green-700">
                        Access Error
                    </h1>

                    <p className="text-gray-600 mb-6">
                        This page is only accessible to sellers.
                    </p>
                    <Button onClick={() => navigate("/")}>Go Home</Button>
                </Card>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto p-4 md:p-6">
            <Card>
                {/* Heading */}
                <h1 className="text-2xl font-bold text-green-700 mb-4">
                    Collect Bundle
                </h1>

                <p className="text-gray-600 mb-6">
                    Enter the claim code from the customer to mark this bundle
                    as collected.
                </p>

                {/* Depends on if the bundle was collected */}
                {collectSuccess ? (
                    // Success message
                    <div className="text-center py-6">
                        <p className="text-green-600 font-semibold text-lg">
                            Bundle successfully collected!
                        </p>

                        {/* Option to collect another */}
                        <Button onClick={handleReset} className="mt-4">
                            Collect Another
                        </Button>
                    </div>
                ) : (
                    // Otherwise, initial collection
                    <form onSubmit={handleSubmit}>
                        {/* Code input */}
                        <FormInput
                            label="Claim Code"
                            name="claimCode"
                            value={claimCode}
                            onChange={(e) => setClaimCode(e.target.value)}
                            placeholder="Enter the claim code"
                            required
                        />

                        {/* Submit button */}
                        <SubmitButton disabled={collecting}>
                            {collecting
                                ? "Collecting..."
                                : "Confirm Collection"}
                        </SubmitButton>
                    </form>
                )}
            </Card>
        </div>
    );
}
