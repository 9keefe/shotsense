import React, { useState } from "react";

/**
 * Tailwind color references for easy adjustments:
 *  - slate-50, slate-100, slate-200, ..., slate-900
 *  - accent color: text-blue-500, bg-blue-500, etc.
 */

function LoginPage() {
  // Either "web" or "mobile"
  const [viewMode, setViewMode] = useState("web");

  // Helper to toggle the layout mode
  const toggleViewMode = () => {
    setViewMode(viewMode === "web" ? "mobile" : "web");
  };

  /**
   * Outer container classes:
   *  - If "web" => fill the entire width with a slate background.
   *  - If "mobile" => center a narrower container in a black “viewport”.
   */
  const outerContainerClasses =
    viewMode === "web"
      ? // Web layout => entire width
        "bg-slate-800 min-h-screen w-full flex flex-col items-center"
      : // Mobile layout => black background + center a mobile container
        "bg-black min-h-screen w-full flex flex-col items-center";

  /**
   * Inner container classes:
   *  - If "web", you might want a max width and center it, or just fill up.
   *  - If "mobile", fix a narrower “phone” width (e.g. 375px).
   */
  const innerContainerClasses =
    viewMode === "web"
      ? // For “web” mode, you might want a typical container approach:
        "w-full max-w-sm sm:max-w-md md:max-w-lg lg:max-w-xl px-6 py-8 bg-slate-900 rounded-md shadow-lg"
      : // For “mobile” mode, fix a typical phone width, e.g. 375px
        // plus some margin for top/bottom
        "w-[390px] min-h-screen bg-slate-900 px-4 py-8";

  return (
    <div className={outerContainerClasses}>
      {/* Toggle Button — bottom-left corner, but for simplicity here 
          we can put it top-left. You can absolutely-position it if you prefer. */}
      <div className="fixed bottom-4 left-4">
        <button
          onClick={toggleViewMode}
          className="px-4 py-2 rounded text-slate-50 bg-blue-600 hover:bg-blue-700 focus:outline-none"
        >
          Switch to {viewMode === "web" ? "Mobile" : "Web"}
        </button>
      </div>

      {/* The actual login UI container */}
      <div className={innerContainerClasses}>
        {/* Logo */}
        <div className="flex justify-center mb-6">
          {/* This is just an example placeholder — replace with an <img> or <svg> of your logo */}
          <div className="w-16 h-16 rounded-full bg-slate-700 flex items-center justify-center">
            <span className="text-blue-400 text-2xl font-bold">SS</span>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-2xl text-slate-100 font-bold text-center mb-8">
          Welcome!
        </h1>

        {/* Form fields */}
        <div className="mb-4">
          <label className="block text-slate-400 mb-2" htmlFor="username">
            Username
          </label>
          <input
            type="text"
            id="username"
            className="w-full px-3 py-2 rounded bg-slate-700 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="mb-6">
          <label className="block text-slate-400 mb-2" htmlFor="password">
            Password
          </label>
          <input
            type="password"
            id="password"
            className="w-full px-3 py-2 rounded bg-slate-700 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Login button */}
        <button className="w-full py-2 mb-3 rounded bg-blue-600 text-slate-100 hover:bg-blue-700 focus:outline-none">
          Log In
        </button>

        {/* Forgot password */}
        <div className="text-right text-blue-400 hover:underline cursor-pointer mb-6">
          Forgot password?
        </div>

        {/* Create account */}
        <button className="w-full py-2 rounded bg-slate-700 text-blue-400 hover:bg-slate-600 focus:outline-none">
          Create Account
        </button>
      </div>
    </div>
  );
}

export default LoginPage;
