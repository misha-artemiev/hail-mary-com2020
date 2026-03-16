/**
 * AboutUs.jsx
 * @Author Noe Bouchard
 */

import React from "react";

// Components
import Card from "../components/Card";

/**
 * Displays project background and platform information.
 *
 * @returns {JSX.Element} the About Us page
 */
export default function AboutUs() {
    const visionPoints = [
        "A surplus food marketplace",
        "Transparent reservation and claim systems",
        "Seller analytics and demand forecasting",
        "Gamified rescue to encourage sustainable habits",
    ];

    const teamRoles = [
        "Product leadership – defining vision, priorities, and value",
        "Technical development – backend, frontend, devops",
        "Data & forecasting – demand modelling and evaluation",
        "Testing & quality assurance – reliability and edge-case handling",
        "Documentation & compliance – ensuring professional standards",
    ];

    const differentiators = [
        "Seller analytics (sell-through rates, waste proxies, pricing insights)",
        "Explainable demand forecasting with baseline comparisons",
        "Gamification mechanics like Rescue Streaks and badges",
    ];

    const engineeringPhases = [
        "Problem clarification and feasibility",
        "Requirements and architecture design",
        "Incremental implementation",
        "Monitoring and quality control",
        "Evaluation against measurable success criteria",
    ];

    const successMetrics = [
        "Zero overselling",
        "Accurate handling of no-shows and expiries",
        "Forecast performance vs baselines",
        "Measurable waste reduction estimates",
    ];

    const commitments = [
        "Professional software practices (GitHub commits, issue tracking, testing suites)",
        "Accessibility considerations (keyboard navigation, readable contrast, mobile-friendly design)",
        "Security best practices (role-based access, environment variables for secrets)",
        "Responsible computing principles",
    ];

    return (
        <div className="max-w-5xl mx-auto p-4 md:p-6">
            <Card>
                <h1 className="text-3xl font-bold text-green-700 mb-2">
                    About Us
                </h1>
                <p className="text-gray-700">
                    Hail Mary is a student-led product team created as part of
                    the <strong>University of Exeter</strong>{" "}
                    <strong>COMM2020</strong> Team Project. We are building a
                    data-driven marketplace that tackles one of the most urgent
                    everyday problems: preventable food waste. Our mission is
                    simple:
                </p>
                <p className="text-gray-700 mt-3 font-semibold">
                    Rescue surplus food. Reduce waste.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    Our Vision
                </h2>
                <p className="text-gray-700">
                    Food waste is costly, financially, socially, and
                    environmentally. Sellers often over-produce due to
                    uncertainty in demand, while consumers miss opportunities to
                    access affordable surplus food.
                </p>
                <p className="text-gray-700 mt-3">
                    Hail Mary bridges that gap by combining:
                </p>
                <ul className="space-y-2 text-gray-700 mt-2">
                    {visionPoints.map((point) => (
                        <li
                            key={point}
                            className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100"
                        >
                            {point}
                        </li>
                    ))}
                </ul>
                <p className="text-gray-700 mt-3">
                    Our goal is not just to redistribute surplus food, but to
                    make waste reduction measurable, predictable, and engaging.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    How We Work
                </h2>
                <p className="text-gray-700">
                    We operate as a structured, cross-functional Scrum team,
                    following Agile principles taught in COMM2020.
                </p>
                <p className="text-gray-700 mt-3">Our team includes:</p>
                <ul className="space-y-2 text-gray-700 mt-2">
                    {teamRoles.map((role) => (
                        <li
                            key={role}
                            className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100"
                        >
                            {role}
                        </li>
                    ))}
                </ul>
                <p className="text-gray-700 mt-3">We work in sprints, with:</p>
                <ul className="space-y-2 text-gray-700 mt-2">
                    <li className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100">
                        Clear backlog prioritisation
                    </li>
                    <li className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100">
                        Biweekly reviews and retrospectives
                    </li>
                    <li className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100">
                        Defined success measures
                    </li>
                    <li className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100">
                        Continuous testing and iteration
                    </li>
                </ul>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    What Makes Hail Mary Different
                </h2>
                <p className="text-gray-700">
                    Hail Mary is not just a marketplace.
                </p>
                <p className="text-gray-700 mt-3">It integrates:</p>
                <ul className="space-y-2 text-gray-700 mt-2">
                    {differentiators.map((item) => (
                        <li
                            key={item}
                            className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100"
                        >
                            {item}
                        </li>
                    ))}
                </ul>
                <p className="text-gray-700 mt-3">
                    All forecasting is transparent and explainable, in line with
                    the project specification.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    Our Approach to Building
                </h2>
                <p className="text-gray-700">
                    We follow structured engineering phases:
                </p>
                <ul className="space-y-2 text-gray-700 mt-2">
                    {engineeringPhases.map((phase, index) => (
                        <li
                            key={phase}
                            className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100"
                        >
                            {index + 1}. {phase}
                        </li>
                    ))}
                </ul>
                <p className="text-gray-700 mt-3">
                    This aligns with the software engineering lifecycle outlined
                    in our module materials. COMM2020 - Team Project overview.
                </p>
                <p className="text-gray-700 mt-3">
                    We measure success through:
                </p>
                <ul className="space-y-2 text-gray-700 mt-2">
                    {successMetrics.map((metric) => (
                        <li
                            key={metric}
                            className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100"
                        >
                            {metric}
                        </li>
                    ))}
                </ul>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    Our Commitment
                </h2>
                <p className="text-gray-700">Hail Mary is built with:</p>
                <ul className="space-y-2 text-gray-700 mt-2">
                    {commitments.map((commitment) => (
                        <li
                            key={commitment}
                            className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100"
                        >
                            {commitment}
                        </li>
                    ))}
                </ul>
                <p className="text-gray-700 mt-3">
                    We are not just building a prototype, we are building a
                    system that demonstrates teamwork, technical integration,
                    environmental awareness, and ethical responsibility.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    The Bigger Picture
                </h2>
                <p className="text-gray-700">
                    Hail Mary reflects what we believe technology should do:
                </p>
                <p className="text-gray-700 mt-3 font-semibold">
                    Turn uncertainty into insight.
                </p>
                <p className="text-gray-700 font-semibold">
                    Turn surplus into opportunity.
                </p>
                <p className="text-gray-700 font-semibold">
                    Turn small weekly actions into long-term impact.
                </p>
                <p className="text-gray-700 mt-3">
                    We are a student team, but we are building with the mindset
                    of a real product organisation.
                </p>
                <p className="text-green-700 mt-3  font-semibold">
                    And this is just version 1.5
                </p>
            </Card>
        </div>
    );
}
