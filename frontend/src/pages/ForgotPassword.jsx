import React from "react";
import { Link } from "react-router-dom";

export default function ForgotPassword() {
  return (
    <div className="min-h-screen bg-[#0A0A0B] text-white relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.16),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(99,102,241,0.10),transparent_24%)]" />

      <div className="relative mx-auto flex min-h-screen max-w-7xl items-center px-6 py-12 lg:px-10">
        <div className="grid w-full grid-cols-1 gap-8 xl:grid-cols-[1.05fr_0.95fr]">
          <div className="flex flex-col justify-center">
            <p className="text-xs uppercase tracking-[0.24em] text-zinc-500">
              Shot Sense
            </p>
            <h1 className="mt-4 text-5xl font-semibold tracking-tight md:text-6xl">
              Reset access.
            </h1>
            <p className="mt-6 max-w-xl text-base leading-8 text-zinc-400">
              Enter your email and continue the password recovery flow.
            </p>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-white/5 p-8 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
            <p className="text-xs uppercase tracking-[0.24em] text-zinc-500">
              Forgot password
            </p>
            <h2 className="mt-3 text-3xl font-semibold">Reset your password.</h2>

            <p className="mt-4 text-sm leading-7 text-zinc-400">
              Enter your email and a reset code can be sent through your recovery flow.
            </p>

            <div className="mt-8 space-y-5">
              <div>
                <label className="mb-2 block text-sm text-zinc-400">Email</label>
                <input
                  type="email"
                  placeholder="name@example.com"
                  className="w-full rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-white placeholder:text-zinc-500 focus:outline-none focus:ring-1 focus:ring-blue-400/40"
                />
              </div>

              <button className="w-full rounded-full bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-zinc-200">
                Submit
              </button>

              <div className="pt-2 text-sm text-zinc-400">
                Back to{" "}
                <Link to="/signin" className="text-white hover:underline">
                  Sign in.
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}