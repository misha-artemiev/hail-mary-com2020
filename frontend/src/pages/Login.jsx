import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() { //Basic login page
    const [form, setForm] = useState({
        email: "",
        password: "",
    });

    const navigate = useNavigate();

    const handleChange = (e) => { //handles changes to form
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));
    };

    const handleLogin = (e) => { //handles login submission
        e.preventDefault();
        alert("Login submitted"); // REPLACE WITH ACTUAL LOGIN LOGIC
    };

    const handleSignupRedirect = () => { // Redirect to signup page
        navigate("/signup");
    };

    return (
        <div className="max-w-md mx-auto p-6">
            {/* Login card container */}
            <div className="bg-white shadow-md rounded-lg p-6">
                {/* Header */}
                <h1 className="text-3xl font-bold text-green-700 mb-6 text-center">
                    Sign In
                </h1>

                {/* Login Form */}
                <form onSubmit={handleLogin} className="space-y-4">
                    {/* Email field */}
                    <div>
                        <label className="block font-semibold text-gray-700">
                            Email
                        </label>
                        <input
                            type="email"
                            name="email"
                            required
                            value={form.email}
                            onChange={handleChange}
                            className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                        />
                    </div>

                    {/* Password field */}
                    <div>
                        <label className="block font-semibold text-gray-700">
                            Password
                        </label>
                        <input
                            type="password"
                            name="password"
                            required
                            value={form.password}
                            onChange={handleChange}
                            className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                        />
                    </div>

                    {/* Sign In button */}
                    <button
                        type="submit"
                        className="w-full bg-green-600 text-white px-4 py-3 rounded-md font-semibold 
                                   hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 mt-2"
                    >
                        Sign In
                    </button>
                </form>

                {/* Divider line */}
                <div className="flex items-center my-6">
                    <div className="flex-grow border-t border-gray-300" />
                    <span className="px-3 text-gray-500 text-sm">or</span>
                    <div className="flex-grow border-t border-gray-300" />
                </div>

                {/* Create Account Button */}
                <button
                    onClick={handleSignupRedirect}
                    className="w-full border border-green-600 text-green-700 px-4 py-3 rounded-md font-semibold 
                               hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                    Create an Account
                </button>
            </div>
        </div>
    );
}