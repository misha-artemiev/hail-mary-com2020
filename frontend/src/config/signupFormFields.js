export const SIGNUP_FORM_FIELDS = {
    common: [
        {
            name: "email",
            label: "Email",
            type: "email",
            required: true,
        },
        {
            name: "password",
            label: "Password",
            type: "password",
            required: true,
        },
        {
            name: "confirmPassword",
            label: "Confirm Password",
            type: "password",
            required: true,
        },
    ],

    consumer: [
        {
            name: "firstName",
            label: "First Name",
            required: true,
        },
        {
            name: "lastName",
            label: "Last Name",
            required: true,
        },
    ],

    seller: [
        {
            name: "sellerName",
            label: "Seller Name",
            required: true,
        },
        {
            name: "address1",
            label: "Address Line 1",
            required: true,
        },
        {
            name: "address2",
            label: "Address Line 2",
        },
        {
            name: "city",
            label: "City",
            required: true,
        },
        {
            name: "postCode",
            label: "Postcode",
            required: true,
        },
        {
            name: "county",
            label: "County",
        },
        {
            name: "country",
            label: "Country",
            required: true,
        },
    ],
};
