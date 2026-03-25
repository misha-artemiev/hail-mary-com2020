/**
 * Environmental.jsx
 * @Author Thomas Noakes
 */

import React from "react";

// Components
import Card from "../components/Card";

/**
 * Displays the platform's environmental mission and impact information.
 *
 * @returns {JSX.Element} the environmental page
 */
export default function Environmental() {
    return (
        <div className="max-w-5xl mx-auto p-4 md:p-6">
            <Card>
                <h1 className="text-3xl font-bold text-green-700 mb-2">
                    Our Environmental Mission
                </h1>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    The Problem
                </h2>
                <p className="text-gray-700">
                    Every year, an estimated{" "}
                    <strong>
                        20% of all food produced in the European Union is lost
                        or wasted
                    </strong>
                    , amounting to approximately{" "}
                    <strong>88 million tonnes</strong> of food that never
                    reaches a plate. This is not just an economic issue. It is
                    an environmental crisis hiding in plain sight.
                </p>

                <h3 className="text-xl font-semibold text-green-600 mt-4 mb-2">
                    The Carbon Cost
                </h3>
                <p className="text-gray-700">
                    Food production is one of the most carbon-intensive
                    industries on the planet. When food is wasted, every
                    kilogram of CO2 emitted to grow, transport, and refrigerate
                    it is emitted for nothing. Food waste in the EU alone
                    generates between{" "}
                    <strong>
                        252 and 254 million tonnes of CO2-equivalent emissions
                        every year
                    </strong>
                    . To put that into perspective, if EU food waste were its
                    own country, it would rank as the{" "}
                    <strong>5th largest greenhouse gas emitter</strong> in the
                    entire European Union (Sala et al., 2023).
                </p>
                <p className="text-gray-700 mt-3">
                    Some foods carry a far heavier carbon footprint than others.
                    A single kilogram of beef wasted represents up to{" "}
                    <strong>60 kg of CO2-equivalent emissions</strong> lost.
                    Even a kilogram of wasted dairy carries around{" "}
                    <strong>21 kg of CO2e</strong>. These are not abstract
                    numbers. They are the cost of production that disappears
                    when food is thrown away.
                </p>

                <h3 className="text-xl font-semibold text-green-600 mt-4 mb-2">
                    The Water Cost
                </h3>
                <p className="text-gray-700">
                    Food waste also means water waste. Growing crops, raising
                    livestock, and processing food all consume enormous volumes
                    of fresh water. The{" "}
                    <strong>
                        blue water footprint of avoidable food waste in Europe
                        is approximately 27 litres per person per day
                    </strong>{" "}
                    (Vanham et al., 2015). That is water extracted from rivers,
                    lakes, and aquifers, used to produce food that ends up in
                    the bin.
                </p>

                <h3 className="text-xl font-semibold text-green-600 mt-4 mb-2">
                    The Human Cost
                </h3>
                <p className="text-gray-700">
                    At the same time as this waste occurs,{" "}
                    <strong>
                        around 733 million people faced hunger in 2023
                    </strong>{" "}
                    (FAO, 2024). The contrast is stark. We are producing more
                    food than we need in some parts of the world, wasting a
                    fifth of it, and still failing to feed everyone.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    What We Do About It
                </h2>
                <p className="text-gray-700">
                    Rescue Market was built to address this problem directly. We
                    connect <strong>sellers</strong> (restaurants, cafes, and
                    food retailers) who have surplus food at the end of the day
                    with <strong>consumers</strong> willing to collect it at a
                    reduced price, before it gets thrown away.
                </p>
                <p className="text-gray-700 mt-3">
                    Every bundle rescued through our platform is food that
                    avoids landfill. Every collection is a small but real
                    reduction in the carbon, water, and resources that went into
                    producing it.
                </p>

                <h3 className="text-xl font-semibold text-green-600 mt-4 mb-2">
                    Measuring the Impact
                </h3>
                <p className="text-gray-700">
                    We do not just rescue food. We track it. Every time a
                    reservation is collected on Rescue Market, our platform
                    estimates the CO2 equivalent emissions saved based on the
                    food category and weight of the bundle. Our emission factors
                    are derived from Poore and Nemecek (2018), one of the most
                    comprehensive peer-reviewed studies of food&apos;s
                    environmental impact, published in <em>Science</em>.
                </p>
                <p className="text-gray-700 mt-3">
                    For example, rescuing a 1 kg bundle of mixed prepared meals
                    saves an estimated <strong>4 kg of CO2e</strong> from being
                    emitted pointlessly. Rescuing a beef-based bundle of the
                    same weight saves up to <strong>60 kg of CO2e</strong>.
                    These estimates are conservative approximations, not
                    certified figures, but they give users a genuine sense of
                    the difference their choices make.
                </p>

                <h3 className="text-xl font-semibold text-green-600 mt-4 mb-2">
                    Empowering Sellers (Not Just Consumers)
                </h3>
                <p className="text-gray-700">
                    Most food rescue platforms stop at connecting sellers and
                    consumers. We go further. Rescue Market gives sellers access
                    to <strong>analytics and demand forecasting tools</strong>{" "}
                    so they can understand what sells, when it sells, and how
                    much to prepare. The goal is to help sellers reduce surplus
                    at source, not just redistribute it after the fact.
                </p>
                <p className="text-gray-700 mt-3">
                    This is the gap we fill. Reducing waste before it happens is
                    always more effective than rescuing it afterwards.
                </p>
            </Card>

            <Card>
                <h2 className="text-2xl font-bold text-green-700 mb-3">
                    The Bigger Picture
                </h2>
                <p className="text-gray-700">
                    We are under no illusion that a single platform solves the
                    food waste crisis. But the infrastructure for change exists
                    at the local level, in every restaurant, cafe, and retailer
                    that produces more than it sells each day. Rescue Market
                    gives that surplus somewhere to go, gives consumers an
                    affordable and sustainable choice, and gives sellers the
                    data to do better tomorrow than they did today.
                </p>
                <p className="mt-3 font-semibold text-green-700">
                    Every bundle rescued is a vote for a food system that wastes
                    less, emits less, and feeds more.
                </p>
            </Card>

            <Card>
                <p className="text-gray-600 text-sm italic">
                    <em>
                        Emission factors sourced from Poore, J. and Nemecek, T.
                        (2018). &quot;Reducing food&apos;s environmental impacts
                        through producers and consumers.&quot; Science,
                        360(6392), 987-992. Water footprint data from Vanham, D.
                        et al. (2015). CO2 statistics from Sala, S. et al.
                        (2023). Hunger data from FAO (2024).
                    </em>
                </p>
            </Card>
        </div>
    );
}
