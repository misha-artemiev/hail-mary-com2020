/**
 * OurTeam.jsx
 * @Author Noe Bouchard
 */

import React from "react";

// Components
import Card from "../components/Card";

/**
 * Displays team information and how we work.
 *
 * @returns {JSX.Element} the Our Team page
 */
export default function OurTeam() {
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
        <div className="max-w-5xl mx-auto p-4 md:p-6">
            <Card>
                <h1 className="text-3xl font-bold text-green-700 mb-2">
                    Our Team
                </h1>
                <p className="text-gray-700">
                    We are Group 8, a collaborative team of Computer Science
                    students working under industry-style roles and
                    responsibilities for COMM2020 Team Project delivery.
                </p>
                <p className="text-gray-700 mt-3">
                    COMM2020 - Team Project overview.
                </p>

                <h2 className="text-xl font-semibold text-green-700 mt-5 mb-2">
                    Core Team Members
                </h2>
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

                <h2 className="text-xl font-semibold text-green-700 mt-5 mb-2">
                    Agile Operating Principles
                </h2>
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

                <h2 className="text-xl font-semibold text-green-700 mt-5 mb-2">
                    Rotating Responsibilities
                </h2>
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

                <h2 className="text-xl font-semibold text-green-700 mt-5 mb-2">
                    Professional Engineering Practices
                </h2>
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
