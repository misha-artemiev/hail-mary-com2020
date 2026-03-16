/**
 * errorReportFormFields.js
 * @author GitHub Copilot
 */

/**
 * Used to dynamically render form fields for ReportError page.
 */
export const ERROR_REPORT_FORM_FIELDS = {
    common: [
        {
            name: "title",
            label: "Issue Title",
            required: true,
            placeholder: "Short summary of the problem",
        },
        {
            name: "email",
            label: "Contact Email",
            type: "email",
            required: true,
            placeholder: "you@example.com",
        },
    ],

    user: [
        {
            name: "affected_username",
            label: "Affected Username",
            required: true,
            placeholder: "e.g., user0001",
        },
    ],

    bundle: [
        {
            name: "bundle_id",
            label: "Bundle ID",
            type: "number",
            min: "1",
            step: "1",
            required: true,
            placeholder: "e.g., 42",
        },
        {
            name: "seller_username",
            label: "Seller Username",
            required: false,
            placeholder: "Optional",
        },
    ],

    reservation: [
        {
            name: "reservation_id",
            label: "Reservation ID",
            type: "number",
            min: "1",
            step: "1",
            required: true,
            placeholder: "e.g., 1001",
        },
        {
            name: "bundle_id",
            label: "Related Bundle ID",
            type: "number",
            min: "1",
            step: "1",
            required: false,
            placeholder: "Optional",
        },
    ],
};
