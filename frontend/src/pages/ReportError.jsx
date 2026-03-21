/**
 * ReportError.jsx
 * @author Ed Brown
 */

import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

// Components
import Card from "../components/Card";
import FormInput from "../components/forms/FormInput";
import RoleSelect from "../components/forms/RoleSelect";
import SubmitButton from "../components/forms/SubmitButton";

// Config
import { ERROR_REPORT_FORM_FIELDS } from "../config/errorReportFormFields";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * The error reporting page.
 * Users can switch between user, bundle, and reservation issue forms.
 *
 * @returns {JSX.Element} the report error page
 */
export default function ReportError() {
    const [searchParams] = useSearchParams();
    const [issueType, setIssueType] = useState("");

    const [form, setForm] = useState({
        title: "",
        email: "",
        description: "",
        affected_username: "",
        bundle_id: "",
        seller_username: "",
        reservation_id: "",
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        const issueTypeQuery = searchParams.get("issueType");
        const bundleIdQuery = searchParams.get("bundle_id");
        const reservationIdQuery = searchParams.get("reservation_id");

        if (
            issueTypeQuery === "user" ||
            issueTypeQuery === "bundle" ||
            issueTypeQuery === "reservation"
        ) {
            setIssueType(issueTypeQuery);
        }

        setForm((prev) => ({
            ...prev,
            bundle_id: bundleIdQuery || prev.bundle_id,
            reservation_id: reservationIdQuery || prev.reservation_id,
        }));
    }, [searchParams]);

    const buildDescription = () => {
        const contextLines = [
            `Issue category: ${issueType || "unknown"}`,
            `Issue title: ${form.title}`,
            `Contact email: ${form.email}`,
        ];

        if (form.affected_username) {
            contextLines.push(`Affected username: ${form.affected_username}`);
        }

        if (form.bundle_id) {
            contextLines.push(`Bundle ID: ${form.bundle_id}`);
        }

        if (form.seller_username) {
            contextLines.push(`Seller username: ${form.seller_username}`);
        }

        if (form.reservation_id) {
            contextLines.push(`Reservation ID: ${form.reservation_id}`);
        }

        return `${form.description}\n\n---\n${contextLines.join("\n")}`;
    };

    const submitReport = async () => {
        const token = localStorage.getItem("authToken");
        const userRole = localStorage.getItem("userRole");

        if (!token) {
            throw new Error("Please sign in to submit an issue report.");
        }

        if (userRole !== "consumer" && userRole !== "seller") {
            throw new Error(
                "Only consumers and sellers can submit issue reports.",
            );
        }

        if (!issueType) {
            throw new Error("Please select an issue type.");
        }

        const commonHeaders = {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
        };

        if (issueType === "reservation") {
            if (!form.reservation_id) {
                throw new Error(
                    "Reservation ID is required for reservation issues.",
                );
            }

            const reservationEndpoint =
                userRole === "seller"
                    ? `${API_BASE_URL}/sellers/me/reservations/${form.reservation_id}/report`
                    : `${API_BASE_URL}/consumers/me/reservations/${form.reservation_id}/report`;

            const response = await fetch(reservationEndpoint, {
                method: "POST",
                headers: commonHeaders,
                body: JSON.stringify({
                    issue_type: "OTHER",
                    description: buildDescription(),
                }),
            });

            if (!response.ok) {
                const data = await response.json().catch(() => null);
                throw new Error(
                    data?.detail ||
                        "Unable to submit reservation issue report.",
                );
            }

            return;
        }

        const adminEndpoint = `${API_BASE_URL}/users/me/reports/admin`;

        const response = await fetch(adminEndpoint, {
            method: "POST",
            headers: commonHeaders,
            body: JSON.stringify({
                issue_type: "OTHER",
                description: buildDescription(),
            }),
        });

        if (!response.ok) {
            const data = await response.json().catch(() => null);
            throw new Error(
                data?.detail || "Unable to submit admin issue report.",
            );
        }
    };

    /**
     * Handles changes to any field in the form.
     */
    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));

        if (error) {
            setError(null);
        }

        if (success) {
            setSuccess(false);
        }
    };

    /**
     * Handles switching between issue types.
     * Clears state feedback so each report starts clean.
     */
    const handleIssueTypeChange = (value) => {
        setIssueType(value);
        setError(null);
        setSuccess(false);
    };

    /**
     * Handles submitting the report form.
     */
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setSuccess(false);

        try {
            await submitReport();
            setSuccess(true);
        } catch (err) {
            setError(
                err?.message || "Unable to submit report. Please try again.",
            );
        } finally {
            setLoading(false);
        }
    };

    /**
     * Dynamically renders given information fields.
     *
     * @param {Object[]} fields
     * @returns {JSX.Element[]} a set of FormInput elements
     */
    const renderFields = (fields) =>
        fields.map((field) => (
            <FormInput
                key={field.name}
                label={field.label}
                name={field.name}
                type={field.type}
                min={field.min}
                step={field.step}
                value={form[field.name]}
                onChange={handleChange}
                required={field.required}
                placeholder={field.placeholder}
            />
        ));

    return (
        <div className="max-w-xl mx-auto p-4 md:p-6">
            <Card>
                {error && (
                    <div className="text-center font-semibold bg-red-100 text-red-800 p-3 mb-4 rounded">
                        {error}
                    </div>
                )}

                {success && (
                    <div className="text-center font-semibold bg-green-100 text-green-800 p-3 mb-4 rounded">
                        Report submitted.
                    </div>
                )}

                <h1 className="text-3xl font-bold text-green-700 mb-6 text-center">
                    Report an Issue
                </h1>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {renderFields(ERROR_REPORT_FORM_FIELDS.common)}

                    <RoleSelect
                        label="Issue Type"
                        value={issueType}
                        onChange={(e) => handleIssueTypeChange(e.target.value)}
                        options={[
                            { value: "", label: "Select issue type" },
                            { value: "user", label: "User issue" },
                            { value: "bundle", label: "Bundle issue" },
                            {
                                value: "reservation",
                                label: "Reservation issue",
                            },
                        ]}
                    />

                    {issueType === "user" &&
                        renderFields(ERROR_REPORT_FORM_FIELDS.user)}
                    {issueType === "bundle" &&
                        renderFields(ERROR_REPORT_FORM_FIELDS.bundle)}
                    {issueType === "reservation" &&
                        renderFields(ERROR_REPORT_FORM_FIELDS.reservation)}

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">
                            Issue Details{" "}
                            <span className="text-red-500">*</span>
                        </label>
                        <textarea
                            name="description"
                            value={form.description}
                            onChange={handleChange}
                            required
                            rows={5}
                            placeholder="Describe what happened and include any useful context."
                            className="w-full rounded-md px-3 py-2 border focus:ring-2 focus:ring-green-500 focus:outline-none"
                        />
                    </div>

                    <SubmitButton>
                        {loading ? "Submitting report..." : "Submit Report"}
                    </SubmitButton>
                </form>
            </Card>
        </div>
    );
}
