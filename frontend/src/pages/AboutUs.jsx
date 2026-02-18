/**
 * AboutUs.jsx
 * @Author Noe Bouchard
 */

import React from "react";

// Components
import Card from "../components/Card";

/**
 * Displays project background and team overview.
 *
 * @returns {JSX.Element} the About Us page
 */
export default function AboutUs() {
    const missionGoals = [
        "Make surplus food visible and accessible to consumers.",
        "Prevent overselling through robust inventory and reservation management.",
        "Deliver explainable forecasting recommendations compared against baseline models.",
    ];

    const sellerAnalytics = [
        "Sell-through rates",
        "Waste avoided estimates",
        "Pricing effectiveness",
        "Optimal pickup windows",
    ];

    const coreTeamMembers = [
        "Massimo Belmonte",
        "Furkan Yalcintepe",
        "Thomas Noakes",
        "Ed Brown",
        "Misha Artemiev",
        "Noe Bouchard",
        "Muhammed Panjwani",
    ];

    const agilePrinciples = [
        "Short development sprints",
        "Weekly reviews and retrospectives",
        "Shared ownership with clearly defined responsibilities",
        "Evidence-based decision making",
    ];

    const rotatingResponsibilities = [
        "Project coordination",
        "Backend and database architecture",
        "Frontend and user experience",
        "Data analytics and forecasting",
        "Testing and quality assurance",
        "Documentation and deployment",
    ];

    const engineeringPractices = [
        "Version control with GitHub",
        "Automated and manual testing",
        "Risk tracking",
        "Ethical and licensing documentation",
        "Clear deployment and handover processes",
    ];

    return (
        <div className="max-w-5xl mx-auto p-6">
            <Card>
                <h1 className="text-3xl font-bold text-green-700 mb-2">
                    About Us
                </h1>
                <p className="text-gray-700">
                    Hail Mary is a student-built food waste rescue platform
                    developed as part of the COMM2020 Team Project at the
                    University of Exeter.
                </p>
                <p className="text-gray-700 mt-3">
                    We are a multidisciplinary team working like a mini product
                    startup, combining software engineering, data analytics,
                    forecasting, and user experience design to tackle a
                    real-world sustainability problem: preventable food waste.
                </p>
                <p className="text-gray-700 mt-3">
                    Each year, millions of tonnes of edible food are discarded
                    because of demand uncertainty and operational
                    inefficiencies. Sellers often overproduce to avoid
                    stock-outs, while consumers lack visibility into surplus
                    availability. Hail Mary connects these two sides.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    Platform Capabilities
                </h2>
                <ul className="space-y-2 text-gray-700">
                    <li className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100">
                        Sellers can post surplus food bundles with clear pickup
                        windows.
                    </li>
                    <li className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100">
                        Consumers can reserve bundles and receive secure claim
                        codes.
                    </li>
                    <li className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100">
                        Sellers can access analytics and demand forecasting to
                        improve production planning.
                    </li>
                    <li className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100">
                        Consumers can track personal environmental impact
                        through rescue streaks and badges.
                    </li>
                </ul>
                <p className="text-gray-700 mt-3">
                    We built this system using an iterative, agile development
                    process, delivering working increments while continuously
                    testing, evaluating, and improving the product.
                </p>
                <p className="text-gray-700 mt-3">
                    Hail Mary is not just a marketplace. It is a data-driven
                    decision support tool designed to reduce waste at its
                    source.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    Our Mission
                </h2>
                <p className="text-gray-700 mb-3">
                    Reduce preventable food waste by combining marketplace
                    access with transparent, explainable forecasting.
                </p>
                <ul className="space-y-2 text-gray-700">
                    {missionGoals.map((value) => (
                        <li
                            key={value}
                            className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100"
                        >
                            {value}
                        </li>
                    ))}
                </ul>

                <h3 className="text-xl font-semibold text-green-700 mt-5 mb-2">
                    Seller Analytics Focus
                </h3>
                <ul className="space-y-2 text-gray-700">
                    {sellerAnalytics.map((item) => (
                        <li
                            key={item}
                            className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100"
                        >
                            {item}
                        </li>
                    ))}
                </ul>

                <p className="text-gray-700 mt-3">
                    We believe sustainable impact requires transparency in how
                    predictions are generated, responsible computing, ethical
                    design, accessibility, inclusivity, and secure
                    privacy-conscious systems.
                </p>
                <p className="text-gray-700 mt-3">
                    Hail Mary encourages behavioural change through gamification
                    features such as Rescue Streaks and impact summaries,
                    helping users see the measurable environmental difference
                    they make.
                </p>
                <p className="text-gray-700 mt-3">
                    Our long-term vision is to help businesses shift from
                    reactive waste management to proactive demand planning.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    Group 8 and How We Work
                </h2>
                <p className="text-gray-700">
                    We are Group 8, a collaborative team of Computer Science
                    students working under industry-style roles and
                    responsibilities for COMM2020 Team Project delivery.
                </p>
                <p className="text-gray-700 mt-3">
                    COMM2020 - Team Project overview.
                </p>

                <h3 className="text-xl font-semibold text-green-700 mt-5 mb-2">
                    Core Team Members
                </h3>
                <ul className="space-y-2 text-gray-700">
                    {coreTeamMembers.map((member) => (
                        <li
                            key={member}
                            className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100"
                        >
                            {member}
                        </li>
                    ))}
                </ul>

                <h3 className="text-xl font-semibold text-green-700 mt-5 mb-2">
                    Agile Operating Principles
                </h3>
                <ul className="space-y-2 text-gray-700">
                    {agilePrinciples.map((principle) => (
                        <li
                            key={principle}
                            className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100"
                        >
                            {principle}
                        </li>
                    ))}
                </ul>

                <h3 className="text-xl font-semibold text-green-700 mt-5 mb-2">
                    Rotating Responsibilities
                </h3>
                <ul className="space-y-2 text-gray-700">
                    {rotatingResponsibilities.map((responsibility) => (
                        <li
                            key={responsibility}
                            className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100"
                        >
                            {responsibility}
                        </li>
                    ))}
                </ul>

                <h3 className="text-xl font-semibold text-green-700 mt-5 mb-2">
                    Professional Engineering Practices
                </h3>
                <ul className="space-y-2 text-gray-700">
                    {engineeringPractices.map((practice) => (
                        <li
                            key={practice}
                            className="bg-gray-50 rounded-md px-3 py-2 border border-gray-100"
                        >
                            {practice}
                        </li>
                    ))}
                </ul>

                <p className="text-gray-700 mt-3">CW1_Requirements.</p>
                <p className="text-gray-700 mt-3">
                    We built Hail Mary as both a technical solution and a
                    demonstration of collaborative engineering in practice.
                </p>
            </Card>
        </div>
    );
}
