import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

export default function Signup() {
  const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmpassword: "",
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmpassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      await axios.post(`${BACKEND_BASE_URL}/signup`, formData, {
        withCredentials: true,
      });
      navigate("/home");
    } catch (err) {
      console.error("Error response:", err.response);
      setError(
        err.response?.data?.error || "Something went wrong. Please try again."
      );
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0B] text-white relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.16),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(99,102,241,0.10),transparent_24%)]" />

      <div className="relative mx-auto flex min-h-screen max-w-7xl items-center px-6 py-12 lg:px-10">
        <div className="grid w-full grid-cols-1 gap-8 xl:grid-cols-[1.05fr_0.95fr]">
          <div className="flex flex-col justify-center">
            <p className="text-xs uppercase tracking-[0.24em] text-zinc-500">
              ShotSense
            </p>
            <h1 className="mt-4 text-5xl font-semibold tracking-tight md:text-6xl">
              Create account.
            </h1>
            <p className="mt-6 max-w-xl text-base leading-8 text-zinc-400">
              Set up a clean training workspace to start storing session uploads,
              analysis results and feedback all in one place.
            </p>
          </div>

          <form
            onSubmit={handleSubmit}
            className="rounded-[2rem] border border-white/10 bg-white/5 p-8 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]"
          >
            <p className="text-xs uppercase tracking-[0.24em] text-zinc-500">
              Sign up
            </p>
            <h2 className="mt-3 text-3xl font-semibold">Create an account.</h2>

            <div className="mt-8 space-y-5">
              <div>
                <label className="mb-2 block text-sm text-zinc-400">Name</label>
                <input
                  type="text"
                  name="name"
                  placeholder="john smith"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="w-full rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-white placeholder:text-zinc-500 focus:outline-none focus:ring-1 focus:ring-blue-400/40"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm text-zinc-400">Email</label>
                <input
                  type="email"
                  name="email"
                  placeholder="name@example.com"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-white placeholder:text-zinc-500 focus:outline-none focus:ring-1 focus:ring-blue-400/40"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm text-zinc-400">Password</label>
                <input
                  type="password"
                  name="password"
                  placeholder="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  className="w-full rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-white placeholder:text-zinc-500 focus:outline-none focus:ring-1 focus:ring-blue-400/40"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm text-zinc-400">
                  Confirm password
                </label>
                <input
                  type="password"
                  name="confirmpassword"
                  placeholder="confirm password"
                  value={formData.confirmpassword}
                  onChange={handleChange}
                  required
                  className="w-full rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-white placeholder:text-zinc-500 focus:outline-none focus:ring-1 focus:ring-blue-400/40"
                />
              </div>

              {error && (
                <div className="rounded-2xl border border-red-400/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                  {error}
                </div>
              )}

              <button
                type="submit"
                className="w-full rounded-full bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-zinc-200"
              >
                Create account
              </button>

              <div className="pt-2 text-sm text-zinc-400">
                Already have an account?{" "}
                <Link to="/signin" className="text-white hover:underline">
                  Sign in here.
                </Link>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}