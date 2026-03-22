import React, { useEffect, useState } from "react";
import axios from "axios";

export default function Profile() {
  const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;
  const [user, setUser] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get(`${BACKEND_BASE_URL}/user`, {
          withCredentials: true,
        });
        setUser(response.data);
      } catch (error) {
        console.error("Failed to fetch profile:", error.response?.data || error.message);
      }
    };

    fetchProfile();
  }, [BACKEND_BASE_URL]);

  return (
    <div className="min-h-screen bg-[#0A0A0B] text-white relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.14),transparent_26%),radial-gradient(circle_at_bottom_right,rgba(99,102,241,0.08),transparent_22%)]" />

      <div className="relative mx-auto max-w-7xl px-6 py-10 lg:px-10">
        <div className="mb-8">
          <p className="text-xs uppercase tracking-[0.24em] text-zinc-500">
            ShotSense
          </p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight md:text-5xl">
            Profile
          </h1>
          <p className="mt-3 text-zinc-400">
            Basic account details for the current user.
          </p>
        </div>

        <div className="max-w-2xl rounded-[2rem] border border-white/10 bg-white/5 p-8 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
          <div className="mb-8 flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04] text-xl font-semibold text-blue-300">
              {user?.name ? user.name.charAt(0).toUpperCase() : "U"}
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-white">
                {user?.name || "User"}
              </h2>
              <p className="text-zinc-400">{user?.email || "No email available"}</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">Name</p>
              <p className="mt-2 text-white">{user?.name || "-"}</p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">Email</p>
              <p className="mt-2 text-white">{user?.email || "-"}</p>
            </div>

            <div className="rounded-2xl border border-blue-400/20 bg-blue-500/10 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-blue-300">Status</p>
              <p className="mt-2 text-white">Active account</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}