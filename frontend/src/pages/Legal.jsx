/**
 * LegalAndEthical.jsx
 * @Author Thomas Noakes
 */

import React from "react";

// Components
import Card from "../components/Card";

/**
 * Displays the platform's legal and ethical commitments.
 *
 * @returns {JSX.Element} the legal and ethical page
 */
export default function Legal() {
    return (
        <div className="max-w-5xl mx-auto p-4 md:p-6">
            <Card>
                <h1 className="text-3xl font-bold text-green-700 mb-2">
                    Legal & Ethical Commitment
                </h1>
                <p className="text-gray-700">
                    At <strong>Hail Mary - Rescue Market</strong>, we believe
                    that technology designed to reduce food waste must also be
                    built responsibly. Our platform aims to connect sellers with
                    consumers to redistribute surplus food while respecting
                    ethical principles, legal standards, and the wellbeing of
                    our users.
                </p>
                <p className="text-gray-700 mt-3">
                    We design our system to be transparent, safe, and
                    accountable. Our goal is not only to reduce food waste, but
                    to ensure that the technology enabling this process operates
                    in a fair and responsible manner.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    Food Safety and Transparency
                </h2>
                <p className="text-gray-700">
                    Because our platform facilitates the redistribution of
                    surplus food, clear communication about food safety is
                    essential.
                </p>
                <p className="text-gray-700 mt-2">
                    Rescue Market provides detailed bundle descriptions that may
                    include:
                </p>
                <ul className="list-disc list-inside text-gray-700 space-y-1 mt-2">
                    <li>Ingredients and product categories</li>
                    <li>Known allergens when provided by sellers</li>
                    <li>Pickup time windows and handling information</li>
                </ul>
                <p className="text-gray-700 mt-3">
                    However, users must understand that rescued food may have
                    limited shelf life. Sellers remain responsible for the
                    accuracy of the information provided, and consumers are
                    advised to assess products before consumption.
                </p>
                <p className="text-gray-700 mt-2">
                    For this reason, the platform includes clear food safety
                    disclaimers and encourages responsible handling of rescued
                    food.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    Privacy and Data Protection
                </h2>
                <p className="text-gray-700">
                    User privacy is a fundamental principle of the system&apos;s
                    design.
                </p>
                <p className="text-gray-700 mt-2">
                    Rescue Market intentionally collects{" "}
                    <strong>minimal personal information</strong>. Consumer
                    profiles use pseudonymous display names rather than
                    identifiable personal data whenever possible. Sensitive data
                    such as payment information is not collected through the
                    platform.
                </p>
                <p className="text-gray-700 mt-2">We also ensure that:</p>
                <ul className="list-disc list-inside text-gray-700 space-y-1 mt-2">
                    <li>Personal data is stored securely</li>
                    <li>Only necessary information is collected</li>
                    <li>
                        Data is not shared with third parties without
                        justification
                    </li>
                </ul>
                <p className="text-gray-700 mt-3">
                    These measures help protect users while maintaining the
                    functionality required for reservations and marketplace
                    activity.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    Fairness and Accessibility
                </h2>
                <p className="text-gray-700">
                    Our platform is designed to be{" "}
                    <strong>inclusive and accessible</strong>. We aim to ensure
                    that everyone can benefit from food rescue initiatives
                    regardless of their technical ability or device.
                </p>
                <p className="text-gray-700 mt-2">
                    To support accessibility, the system includes:
                </p>
                <ul className="list-disc list-inside text-gray-700 space-y-1 mt-2">
                    <li>Mobile-friendly interfaces</li>
                    <li>Readable text and high-contrast layouts</li>
                    <li>Keyboard-accessible navigation for core features</li>
                </ul>
                <p className="text-gray-700 mt-3">
                    These design choices allow a broader range of users to
                    participate in food waste reduction efforts.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    Transparency in Analytics and Forecasting
                </h2>
                <p className="text-gray-700">
                    Rescue Market includes a demand forecasting component
                    designed to help sellers reduce overproduction. To maintain
                    ethical standards in data-driven systems, all forecasting
                    methods used in the project are{" "}
                    <strong>transparent and explainable</strong>.
                </p>
                <p className="text-gray-700 mt-2">
                    Instead of relying on opaque &quot;black-box&quot;
                    predictions, the system compares forecasting methods against
                    clear baselines and explains the assumptions used in the
                    models. This approach ensures that sellers understand the
                    reasoning behind production recommendations.
                </p>
                <p className="text-gray-700 mt-3">
                    Transparent analytics help maintain trust while improving
                    operational decisions.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    Intellectual Property and Open Development
                </h2>
                <p className="text-gray-700">
                    The software developed for Rescue Market respects
                    intellectual property and licensing requirements. All
                    external libraries, tools, and datasets used in the project
                    are documented along with their licenses.
                </p>
                <p className="text-gray-700 mt-2">
                    Maintaining a clear software and data inventory ensures
                    compliance with legal obligations and supports
                    reproducibility of the system.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    Ethical Impact
                </h2>
                <p className="text-gray-700">
                    Food waste has significant environmental, economic, and
                    social consequences. By enabling surplus redistribution,
                    Rescue Market contributes to:
                </p>
                <ul className="list-disc list-inside text-gray-700 space-y-1 mt-2">
                    <li>Reducing unnecessary food disposal</li>
                    <li>
                        Lowering environmental impact associated with food waste
                    </li>
                    <li>Providing affordable food access to consumers</li>
                </ul>
                <p className="text-gray-700 mt-3">
                    At the same time, we continuously evaluate potential
                    unintended consequences, such as inequitable access or
                    misuse of the system, and work to minimise these risks.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    Our Commitment
                </h2>
                <p className="text-gray-700 mb-2">
                    The development of Rescue Market follows responsible
                    engineering principles that prioritise:
                </p>
                <div className="grid grid-cols-2 gap-3 mt-3">
                    <div className="bg-green-50 rounded-md px-4 py-3 border border-green-200 text-center">
                        <span className="text-green-700 font-semibold">
                            Safety
                        </span>
                    </div>
                    <div className="bg-green-50 rounded-md px-4 py-3 border border-green-200 text-center">
                        <span className="text-green-700 font-semibold">
                            Transparency
                        </span>
                    </div>
                    <div className="bg-green-50 rounded-md px-4 py-3 border border-green-200 text-center">
                        <span className="text-green-700 font-semibold">
                            Inclusivity
                        </span>
                    </div>
                    <div className="bg-green-50 rounded-md px-4 py-3 border border-green-200 text-center">
                        <span className="text-green-700 font-semibold">
                            Accountability
                        </span>
                    </div>
                </div>
                <p className="text-gray-700 mt-4">
                    We believe technology should not only solve problems but do
                    so in a way that respects people, communities, and the
                    environment.
                </p>
            </Card>
        </div>
    );
}
