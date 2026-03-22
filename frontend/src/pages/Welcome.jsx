import React from "react";
import { Link } from "react-router-dom";

export default function Welcome() {
  return (
    <div className="min-h-screen bg-[#0A0A0B] text-white relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.18),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(99,102,241,0.10),transparent_24%)]" />

      <div className="relative mx-auto flex min-h-screen max-w-7xl items-center px-6 py-12 lg:px-10">
        <div className="grid w-full grid-cols-1 gap-8 xl:grid-cols-[1.15fr_0.85fr]">
          <div className="flex flex-col justify-center">
            <div className="mb-6 inline-flex h-16 w-16 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.05] text-xl font-semibold text-blue-300">
              SS
            </div>

            <p className="text-xs uppercase tracking-[0.24em] text-zinc-500">
              ShotSense
            </p>
            <h1 className="mt-4 text-5xl font-semibold tracking-tight md:text-6xl">
              AI-led
              <br />
              basketball training.
            </h1>

            <p className="mt-6 max-w-2xl text-base leading-8 text-zinc-400">
              Upload a shooting clip, break it down phase by phase, and review
              cleaner biomechanical feedback in a polished training workflow.
            </p>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-white/5 p-8 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
            <p className="text-xs uppercase tracking-[0.24em] text-zinc-500">
              Access
            </p>
            <h2 className="mt-3 text-3xl font-semibold">Welcome</h2>
            <p className="mt-3 text-sm leading-7 text-zinc-400">
              Sign in to continue reviewing sessions, or create an account to
              start building your private analysis library.
            </p>

            <div className="mt-10 space-y-4">
              <Link
                to="/signin"
                className="block w-full rounded-full border border-white/10 bg-white/[0.04] px-5 py-3 text-center text-sm font-medium text-white transition hover:bg-white/[0.08]"
              >
                Sign in
              </Link>

              <Link
                to="/signup"
                className="block w-full rounded-full bg-white px-5 py-3 text-center text-sm font-medium text-black transition hover:bg-zinc-200"
              >
                Create account
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}