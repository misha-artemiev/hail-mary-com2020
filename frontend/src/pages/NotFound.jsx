/**
 * NotFound.jsx
 * @author Thomas Noakes
 */

import React from "react";

/**
 * Catches all unknown UI routes (*i.e.* `/*`) and displays a 404 error page.
 *
 * @returns {JSX.Element} a 404 page
 */
export default function NotFound() {
    return <h1>404 - Page not found!</h1>;
}
