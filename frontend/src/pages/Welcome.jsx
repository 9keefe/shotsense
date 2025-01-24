import React from "react";
import { Link } from "react-router-dom";

export default function Welcome() {
  return (
    <div className="bg-orange-500 min-h-screen flex flex-col items-center">

      <div className="flex flex-col items-center mt-32">
        <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center">
          <span className="text-orange-500 font-bold text-3xl">SS</span> {/* Placeholder for Logo */}
        </div>
        <div>
          <h1 className="text-white text-2xl mt-4">SHOTSENSE</h1>
        </div>
      </div>

      <div className="w-full max-w-md px-8 mt-20">
        <h2 className="text-white text-3xl font-bold text-center mb-8">
          Welcome
        </h2>

        <Link
          to="/signin"
          className="block w-full py-3 mb-4 bg-transparent border-2 border-white text-white text-center rounded-full font-semibold hover:bg-orange-700"
        >
          SIGN IN
        </Link>

        <Link
          to="/signup"
          className="block w-full py-3 bg-white text-orange-500 text-center rounded-full font-semibold hover:bg-gray-200 hover:text-orange-500"
        >
          SIGN UP
        </Link>
      </div>
    </div>
  );
}
