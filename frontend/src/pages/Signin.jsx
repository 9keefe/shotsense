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

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await axios.post(`${BACKEND_BASE_URL}/signin`, formData, {
        withCredentials: true,
      });
      navigate("/home");
    } catch (err) {
      console.error("Error response", err.response);
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
              Welcome back.
            </h1>
            <p className="mt-6 max-w-xl text-base leading-8 text-zinc-400">
              Sign in to access your training workspace, review previous sessions,
              and continue refining your shot mechanics.
            </p>
          </div>

          <form
            onSubmit={handleSubmit}
            className="rounded-[2rem] border border-white/10 bg-white/5 p-8 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]"
          >
            <p className="text-xs uppercase tracking-[0.24em] text-zinc-500">
              Sign in
            </p>
            <h2 className="mt-3 text-3xl font-semibold">Welcome back.</h2>

            <div className="mt-8 space-y-5">
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

              <div className="text-right">
                <Link
                  to="/forgot-password"
                  className="text-sm text-zinc-400 transition hover:text-white"
                >
                  Forgot password?
                </Link>
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
                Sign in
              </button>

              <div className="pt-2 text-sm text-zinc-400">
                No account yet?{" "}
                <Link to="/signup" className="text-white hover:underline">
                  Create one.
                </Link>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}