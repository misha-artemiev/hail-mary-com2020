/**
 * TermsAndConditions.jsx
 * @Author Hail Mary Team
 */

import React from "react";

// Components
import Card from "../components/Card";

/**
 * Displays the platform's terms and conditions.
 *
 * @returns {JSX.Element} the terms and conditions page
 */
export default function TermsAndConditions() {
    return (
        <div className="max-w-5xl mx-auto p-4 md:p-6">
            <Card>
                <h1 className="text-3xl font-bold text-green-700 mb-2">
                    Terms and Conditions
                </h1>
                <p className="text-gray-600 mb-4">
                    <strong>
                        Rescue Market — Hail Mary Group | COMM2020 Team Project
                    </strong>
                    <br />
                    <strong>Last updated: March 2026</strong>
                </p>
                <p className="text-gray-700 italic mb-4">
                    By ticking the box at registration, you confirm that you
                    have read, understood, and agree to these Terms and
                    Conditions in full. If you do not agree, you must not use
                    this platform.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    1. About This Platform
                </h2>
                <p className="text-gray-700">
                    Rescue Market is a web-based food waste rescue marketplace
                    that connects <strong>sellers</strong> (restaurants, cafes,
                    and food retailers) offering surplus food bundles with{" "}
                    <strong>consumers</strong> willing to reserve and collect
                    them within defined pickup windows, at a reduced price.
                </p>
                <p className="text-gray-700 mt-3">
                    The platform is operated by Group Hail Mary as part of an
                    academic project (COMM2020 Team Project, University of
                    Exeter). It is deployed at{" "}
                    <a
                        href="https://hailmary.noxbound.com"
                        className="text-green-600 underline"
                    >
                        https://hailmary.noxbound.com
                    </a>
                    .
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    2. Acceptance of Terms
                </h2>
                <p className="text-gray-700">
                    By creating an account on Rescue Market, you agree to be
                    bound by these Terms and Conditions, our Privacy Policy, and
                    any additional guidelines communicated through the platform.
                    These terms apply to all users, including consumers,
                    sellers, and administrators.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    3. User Accounts
                </h2>
                <ul className="list-disc list-inside text-gray-700 space-y-2">
                    <li>
                        You must provide accurate and complete information when
                        registering.
                    </li>
                    <li>
                        You are responsible for maintaining the confidentiality
                        of your account credentials.
                    </li>
                    <li>
                        You must notify us immediately if you become aware of
                        any unauthorised use of your account.
                    </li>
                    <li>
                        One account per individual or business entity is
                        permitted.
                    </li>
                    <li>
                        We reserve the right to suspend or terminate accounts
                        that violate these terms.
                    </li>
                </ul>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    4. Food Safety Disclaimer
                </h2>
                <p className="text-gray-700 font-semibold">
                    Rescue Market operates strictly as an intermediary platform.
                </p>
                <p className="text-gray-700 mt-2">
                    By using this platform, you explicitly acknowledge and
                    accept the following:
                </p>
                <ul className="list-disc list-inside text-gray-700 space-y-2 mt-2">
                    <li>
                        <strong>All food is consumed at your own risk.</strong>{" "}
                        The platform makes no representations or warranties
                        regarding the safety, freshness, quality, or suitability
                        for consumption of any food bundle listed by sellers.
                    </li>
                    <li>
                        <strong>Rescue Market is not responsible</strong> for
                        any illness, injury, allergic reaction, food poisoning,
                        intoxication, or any other harm resulting from the
                        consumption of food reserved through this platform.
                    </li>
                    <li>
                        <strong>Sellers are solely responsible</strong> for the
                        accuracy of their listings, including descriptions,
                        pickup windows, pricing, and the safety of the food they
                        offer.
                    </li>
                    <li>
                        Pickup windows are provided to reduce the risk of food
                        being collected outside safe timeframes. Consumers are
                        strongly advised to collect food only within the
                        specified window.
                    </li>
                </ul>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    5. Allergen Information
                </h2>
                <ul className="list-disc list-inside text-gray-700 space-y-2">
                    <li>
                        Sellers are <strong>required</strong> to provide
                        allergen information for each bundle they post.
                    </li>
                    <li>
                        <strong>Rescue Market does not verify</strong> the
                        completeness or accuracy of allergen information
                        provided by sellers.
                    </li>
                    <li>
                        If you have a known food allergy or intolerance, you
                        must assess allergen information with care and contact
                        the seller directly before collecting a bundle.
                    </li>
                    <li>
                        <strong>Rescue Market accepts no liability</strong> for
                        allergic reactions or adverse health effects resulting
                        from inaccurate allergen information.
                    </li>
                </ul>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    6. Seller Responsibilities
                </h2>
                <p className="text-gray-700 mb-2">As a seller, you agree to:</p>
                <ul className="list-disc list-inside text-gray-700 space-y-2">
                    <li>
                        Provide accurate, honest, and complete descriptions of
                        all food bundles.
                    </li>
                    <li>
                        Only list food that is safe for consumption and complies
                        with applicable food safety regulations.
                    </li>
                    <li>
                        Honour confirmed reservations and mark collection
                        outcomes promptly.
                    </li>
                    <li>
                        Not misrepresent the origin, quality, or safety of any
                        food item.
                    </li>
                    <li>
                        Comply with all applicable local food hygiene and safety
                        laws.
                    </li>
                </ul>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    7. Consumer Responsibilities
                </h2>
                <p className="text-gray-700 mb-2">
                    As a consumer, you agree to:
                </p>
                <ul className="list-disc list-inside text-gray-700 space-y-2">
                    <li>
                        Reserve bundles only when you genuinely intend to
                        collect them within the stated pickup window.
                    </li>
                    <li>
                        Present your claim code at pickup and confirm collection
                        with the seller.
                    </li>
                    <li>
                        Assess the suitability of any food for your personal
                        dietary requirements before consuming it.
                    </li>
                    <li>
                        Not attempt to abuse the reservation system (e.g., by
                        making multiple conflicting reservations).
                    </li>
                </ul>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    8. Data Protection and Privacy
                </h2>
                <p className="text-gray-700 mb-3">
                    We take your privacy seriously. The following outlines how
                    we handle your personal data in accordance with the{" "}
                    <strong>
                        UK General Data Protection Regulation (UK GDPR)
                    </strong>{" "}
                    and the <strong>Data Protection Act 2018</strong>.
                </p>

                <h3 className="text-xl font-semibold text-green-600 mt-4 mb-2">
                    8.1 Data We Collect
                </h3>
                <div className="overflow-x-auto">
                    <table className="min-w-full border border-gray-300 text-sm">
                        <thead className="bg-gray-100">
                            <tr>
                                <th className="border border-gray-300 px-3 py-2 text-left">
                                    Data
                                </th>
                                <th className="border border-gray-300 px-3 py-2 text-left">
                                    Purpose
                                </th>
                                <th className="border border-gray-300 px-3 py-2 text-left">
                                    Basis
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td className="border border-gray-300 px-3 py-2">
                                    Full name
                                </td>
                                <td className="border border-gray-300 px-3 py-2">
                                    Account identification
                                </td>
                                <td className="border border-gray-300 px-3 py-2">
                                    Consent
                                </td>
                            </tr>
                            <tr>
                                <td className="border border-gray-300 px-3 py-2">
                                    Email address
                                </td>
                                <td className="border border-gray-300 px-3 py-2">
                                    Account login and communication
                                </td>
                                <td className="border border-gray-300 px-3 py-2">
                                    Consent
                                </td>
                            </tr>
                            <tr>
                                <td className="border border-gray-300 px-3 py-2">
                                    Hashed password
                                </td>
                                <td className="border border-gray-300 px-3 py-2">
                                    Secure authentication
                                </td>
                                <td className="border border-gray-300 px-3 py-2">
                                    Consent
                                </td>
                            </tr>
                            <tr>
                                <td className="border border-gray-300 px-3 py-2">
                                    Seller location
                                </td>
                                <td className="border border-gray-300 px-3 py-2">
                                    Enabling consumers to find nearby bundles
                                </td>
                                <td className="border border-gray-300 px-3 py-2">
                                    Consent
                                </td>
                            </tr>
                            <tr>
                                <td className="border border-gray-300 px-3 py-2">
                                    Reservation history
                                </td>
                                <td className="border border-gray-300 px-3 py-2">
                                    Platform functionality and streak tracking
                                </td>
                                <td className="border border-gray-300 px-3 py-2">
                                    Legitimate interest
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <h3 className="text-xl font-semibold text-green-600 mt-4 mb-2">
                    8.2 How We Use Your Data
                </h3>
                <p className="text-gray-700">
                    Your data is used solely to enable you to register, log in,
                    and use the marketplace, facilitate reservations, calculate
                    engagement metrics, and generate anonymised platform
                    analytics. Your data is{" "}
                    <strong>never sold, rented, or shared</strong> with third
                    parties for marketing.
                </p>

                <h3 className="text-xl font-semibold text-green-600 mt-4 mb-2">
                    8.3 Data Security
                </h3>
                <ul className="list-disc list-inside text-gray-700 space-y-1">
                    <li>Passwords are stored using secure one-way hashing.</li>
                    <li>
                        Access to personal data is restricted by role-based
                        access control.
                    </li>
                    <li>The platform is served over HTTPS.</li>
                    <li>
                        Session tokens are validated server-side and invalidated
                        on logout.
                    </li>
                </ul>

                <h3 className="text-xl font-semibold text-green-600 mt-4 mb-2">
                    8.4 Your Rights Under UK GDPR
                </h3>
                <ul className="list-disc list-inside text-gray-700 space-y-1">
                    <li>
                        <strong>Right to access</strong> — request a copy of
                        your data.
                    </li>
                    <li>
                        <strong>Right to rectification</strong> — request
                        correction of inaccurate data.
                    </li>
                    <li>
                        <strong>Right to erasure</strong> — request deletion of
                        your account.
                    </li>
                    <li>
                        <strong>Right to restriction</strong> — limit how we
                        process your data.
                    </li>
                    <li>
                        <strong>Right to object</strong> — object to processing
                        based on legitimate interests.
                    </li>
                    <li>
                        <strong>Right to data portability</strong> — request
                        your data in a machine-readable format.
                    </li>
                </ul>

                <h3 className="text-xl font-semibold text-green-600 mt-4 mb-2">
                    8.5 Data Retention
                </h3>
                <p className="text-gray-700">
                    Personal data is retained for as long as your account is
                    active. If you request account deletion, your personal data
                    will be removed from active records.
                </p>

                <h3 className="text-xl font-semibold text-green-600 mt-4 mb-2">
                    8.6 Cookies and Tokens
                </h3>
                <p className="text-gray-700">
                    The platform uses session tokens stored server-side to
                    maintain authenticated sessions. No third-party tracking
                    cookies are used.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    9. Limitation of Liability
                </h2>
                <p className="text-gray-700">
                    To the fullest extent permitted by applicable law,{" "}
                    <strong>
                        Rescue Market and its operators shall not be liable
                    </strong>{" "}
                    for any direct, indirect, incidental, consequential, or
                    special damages arising from your use of the platform. The
                    platform is provided <strong>&quot;as is&quot;</strong>{" "}
                    without warranties of any kind.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    10. Intellectual Property
                </h2>
                <p className="text-gray-700">
                    All original source code, documentation, and content created
                    by Group Hail Mary for the Rescue Market platform is
                    licensed under the <strong>MIT License</strong>. Third-party
                    libraries and frameworks used by the platform remain subject
                    to their own respective licences.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    11. Governing Law
                </h2>
                <p className="text-gray-700">
                    These Terms and Conditions are governed by and construed in
                    accordance with the laws of{" "}
                    <strong>England and Wales</strong>. Any disputes arising
                    from use of the platform shall be subject to the exclusive
                    jurisdiction of the courts of England and Wales.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    12. Changes to These Terms
                </h2>
                <p className="text-gray-700">
                    We reserve the right to update these Terms and Conditions at
                    any time. Registered users will be notified of material
                    changes via the platform. Continued use of the platform
                    following notification constitutes acceptance of the updated
                    terms.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    13. Contact
                </h2>
                <p className="text-gray-700">
                    For questions, data requests, or to report a concern, please
                    contact the project team at:{" "}
                    <strong>mjab202@exeter.ac.uk</strong>
                </p>
            </Card>
        </div>
    );
}
