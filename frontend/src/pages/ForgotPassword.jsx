import React from "react";
import { Link } from "react-router-dom";

export default function ForgotPassword() {
  return (
    <div className="bg-orange-500 min-h-screen flex flex-col items-center">

      <div className="w-full max-w-md px-8 py-8">
        <h1 className="text-3xl font-bold text-white leading-none">Hello.</h1>
        <p className="text-3xl text-white">Welcome to ShotSense!</p>
        <p className="text-3xl text-white mt-5">Forgot password.</p>
      </div>

      <div className="flex-1 w-full max-w-lg bg-white rounded-t-3xl shadow-lg p-8 pt-16">
        <div className="space-y-4">

          <div className="mb-12">
            <p className="text-sm text-gray-400">Enter your email and we'll send a code to reset your password.</p>
          </div>

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
            />
          </div>

          <div className="py-8">
            <button className="w-full py-3 bg-orange-500 text-white rounded-full font-semibold hover:bg-orange-600">
              SUBMIT
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
      </div>
    </div>
  );
}
