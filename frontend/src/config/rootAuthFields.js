/**
 * rootAuthFields.js
 * @author Thomas Noakes
 */

/**
 * Array of field configurations for the root authentication form.
 * Each field defines the input name, label, type, and placeholder.
 *
 * @type {Array<{name: string, label: string, type: string, placeholder: string}>}
 */
export const ROOT_AUTH_FIELDS = [
    {
        name: "username",
        label: "Root Username",
        type: "text",
        placeholder: "Enter root username",
    },
    {
        name: "password",
        label: "Root Password",
        type: "password",
        placeholder: "Enter root password",
    },
];
