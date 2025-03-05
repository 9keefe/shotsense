import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

export default function Signin() {
  const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState("");

  // handle input changes
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try { 
      const response = await axios.post(`${BACKEND_BASE_URL}/signin`, formData, {
        withCredentials: true,
      });
      console.log("Response:", response.data);
      navigate("/home")
    } catch (err) {
      console.error("Error response", err.response);
      setError(err.response?.data?.error || "Something went wrong. Please try again.");
    }
  }

  return (
    <div className="bg-orange-500 min-h-screen flex flex-col items-center">

      <div className="w-full max-w-md px-8 py-8">
        <h1 className="text-3xl font-bold text-white leading-none">Hello.</h1>
        <p className="text-3xl text-white">Welcome to ShotSense!</p>
        <p className="text-3xl text-white mt-5">Sign in.</p>
      </div>

      <form
        className="flex-1 w-full max-w-lg bg-white rounded-t-3xl shadow-lg p-8 pt-16"
        onSubmit={handleSubmit}
      >
        <div className="space-y-4">

          <div>
            <label
              htmlFor="email"
              className="block text-sm font-semibold text-gray-600"
            >
              Email
            </label>
            <input
              type="email"
              id="email"
              placeholder="name@example.com"
              className="w-full border-b-2 border-gray-300 bg-transparent focus:outline-none focus:border-orange-500 text-gray-800 py-2"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-semibold text-gray-600"
            >
              Password
            </label>
            <input
              type="password"
              id="password"
              placeholder="password"
              className="w-full border-b-2 border-gray-300 bg-transparent focus:outline-none focus:border-orange-500 text-gray-800 py-2"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          <div className="text-right">
            <Link
              to="/forgot-password"
              className="text-sm text-orange-500 hover:underline"
            >
              Forgot password?
            </Link>
          </div>

          {/* Display error message */}
          {error && <p className="text-red-500 text-sm">{error}</p>}

          <div className="py-8">
            <button
              type="submit"
              className="w-full py-3 bg-orange-500 text-white rounded-full font-semibold hover:bg-orange-600 shadow-md"
            >
              SIGN IN
            </button>
          </div>

          <div className="text-right">
            <p className="text-sm text-gray-400">Don't have an account?</p>
            <Link
              to="/signup"
              className="text-md font-semibold text-gray-600 hover:underline"
            >
              Sign up
            </Link>
          </div>
        </div>
      </form>
    </div>
  );
}
