/**
 * createBundleFormFields.js
 * @author Thomas Noakes
 */

/**
 * Used to dynamically render form fields for CreateBundle page.
 */
export const CREATE_BUNDLE_FORM_FIELDS = {
    top: [
        {
            name: "bundle_name",
            label: "Bundle Name",
            required: true,
            placeholder: "e.g., Evening Surprise Bag",
        },
        {
            name: "total_qty",
            label: "Total Quantity",
            type: "number",
            min: "1",
            step: "1",
            required: true,
        },
    ],

    grid: [
        {
            name: "price",
            label: "Original Price (£)",
            type: "number",
            min: "0",
            step: "0.5",
            required: true,
            placeholder: "£10.00",
        },
        {
            name: "discount_percentage",
            label: "Discount (%)",
            type: "number",
            min: "0",
            max: "100",
            required: true,
            placeholder: "20%",
        },
        {
            name: "window_end",
            label: "Pickup Window: available from",
            type: "datetime-local",
            required: true,
        },
        {
            name: "window_start",
            label: "Pickup Window: available until",
            type: "datetime-local",
            required: true,
        },
    ],
};
