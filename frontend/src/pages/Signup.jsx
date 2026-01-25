import React, {useState} from "react";
import { useNavigate } from "react-router-dom";

//Renders singup form for new consumers and sellers based on RBAC

export default function Signup() {
    const navigate = useNavigate();
    
    //Centralised object that holds all fields for the form
    const [role, setRole] = useState("");
    const [form, setForm] = useState({
        email: "",
        password: "",
        confirmPassword: "",
        firstName: "",
        lastName: "",
        sellerName: "",
        address1: "",
        address2: "",
        city: "",
        postCode: "",
        region: "",
        country: "",
    });

    const handleChange = (e) => { //Handles changes to form fields
        const {name, value} = e.target;
        setForm((prev) => ({...prev, [name]: value}));
    };

    const handleSubmit = (e) => { //Handles form submission with basic validation. IMPROVE VALIDATION LATER!!!
        e.preventDefault();

        if (form.password !== form.confirmPassword) { //Ensures passwords match
            alert("Please ensure that passwords match");
            return;
        }

        // SUBMIT SIGNUP DATA TO BACKEND HERE
        alert("Signup submitted");

        navigate("/login");
    };

    return ( // Page design
        <div className="max-w-xl mx-auto p-6">
            <div className="bg-white shadow-md rounded-lg p-6">
                <h1 className="text-3xl font-bold text-green-700 mb-6">
                    Create Account
                </h1>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {/* Email */}
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

                    {/* Password */}
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

                    {/* Confirm Password */}
                    <div>
                        <label className="block font-semibold text-gray-700">
                            Re-enter Password
                        </label>
                        <input
                            type="password"
                            name="confirmPassword"
                            required
                            value={form.confirmPassword}
                            onChange={handleChange}
                            className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                        />
                    </div>

                    {/* Role */}
                    <div>
                        <label className="block font-semibold text-gray-700">
                            Role
                        </label>
                        <select
                            required
                            value={role}
                            onChange={(e) => setRole(e.target.value)}
                            className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                        >
                            <option value="">Select role</option>
                            <option value="consumer">Consumer</option>
                            <option value="seller">Seller</option>
                        </select>
                    </div>

                    {/* Consumer fields */}
                    {role === "consumer" && (
                        <>
                            <div>
                                <label className="block font-semibold text-gray-700">
                                    First Name
                                </label>
                                <input
                                    type="text"
                                    name="firstName"
                                    required
                                    value={form.firstName}
                                    onChange={handleChange}
                                    className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                                />
                            </div>

                            <div>
                                <label className="block font-semibold text-gray-700">
                                    Last Name
                                </label>
                                <input
                                    type="text"
                                    name="lastName"
                                    required
                                    value={form.lastName}
                                    onChange={handleChange}
                                    className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                                />
                            </div>
                        </>
                    )}

                    {/* Seller fields */}
                    {role === "seller" && (
                        <>
                            <div>
                                <label className="block font-semibold text-gray-700">
                                    Seller Name
                                </label>
                                <input
                                    type="text"
                                    name="sellerName"
                                    required
                                    value={form.sellerName}
                                    onChange={handleChange}
                                    className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                                />
                            </div>

                            <div>
                                <label className="block font-semibold text-gray-700">
                                    Address Line 1
                                </label>
                                <input
                                    type="text"
                                    name="address1"
                                    required
                                    value={form.address1}
                                    onChange={handleChange}
                                    className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                                />
                            </div>

                            <div>
                                <label className="block font-semibold text-gray-700">
                                    Address Line 2
                                </label>
                                <input
                                    type="text"
                                    name="address2"
                                    value={form.address2}
                                    onChange={handleChange}
                                    className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                                />
                            </div>

                            <div>
                                <label className="block font-semibold text-gray-700">
                                    City
                                </label>
                                <input
                                    type="text"
                                    name="city"
                                    required
                                    value={form.city}
                                    onChange={handleChange}
                                    className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                                />
                            </div>

                            <div>
                                <label className="block font-semibold text-gray-700">
                                    Post Code
                                </label>
                                <input
                                    type="text"
                                    name="postCode"
                                    required
                                    value={form.postCode}
                                    onChange={handleChange}
                                    className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                                />
                            </div>

                            <div>
                                <label className="block font-semibold text-gray-700">
                                    Region
                                </label>
                                <input
                                    type="text"
                                    name="region"
                                    value={form.region}
                                    onChange={handleChange}
                                    className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                                />
                            </div>

                            <div>
                                <label className="block font-semibold text-gray-700">
                                    Country
                                </label>
                                <input
                                    type="text"
                                    name="country"
                                    required
                                    value={form.country}
                                    onChange={handleChange}
                                    className="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-green-500"
                                />
                            </div>
                        </>
                    )}

                    {/* Submit */}
                    <button
                        type="submit"
                        className="w-full bg-green-600 text-white px-4 py-3 rounded-md font-semibold
                                   hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 mt-4"
                    >
                        Sign Up
                    </button>
                </form>

                {/* Divider */}
                <div className="flex items-center my-6">
                    <div className="flex-grow border-t border-gray-300" />
                    <span className="px-3 text-gray-500 text-sm">or</span>
                    <div className="flex-grow border-t border-gray-300" />
                </div>

                {/* Login Redirect */}
                <button
                    onClick={() => navigate("/login")}
                    className="w-full border border-green-600 text-green-700 px-4 py-3 rounded-md font-semibold
                               hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                    Already have an account? Sign In
                </button>                
            </div>
        </div>
    );
}