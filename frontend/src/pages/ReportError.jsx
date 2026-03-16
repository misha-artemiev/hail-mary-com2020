/**
 * ReportError.jsx
 * @author Ed Brown
 */

import React, { useState } from "react";

// Components
import Card from "../components/Card";
import FormInput from "../components/forms/FormInput";
import RoleSelect from "../components/forms/RoleSelect";
import SubmitButton from "../components/forms/SubmitButton";

// Config
import { ERROR_REPORT_FORM_FIELDS } from "../config/errorReportFormFields";

/**
 * The error reporting page.
 * Users can switch between user, bundle, and reservation issue forms.
 *
 * @returns {JSX.Element} the report error page
 */
export default function ReportError() {
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
            const payload = {
                issue_type: issueType,
                ...form,
            };

            // TODO: Replace this stub with API call to backend endpoint.
            // TODO: Persist issue report payload into database.
            console.log("Issue report payload (temporary):", payload);

            await new Promise((resolve) => setTimeout(resolve, 300));

            setSuccess(true);
        } catch (err) {
            setError(err?.message || "Unable to submit report. Please try again.");
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
                            Issue Details <span className="text-red-500">*</span>
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
