import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import {
  HomeIcon,
  VideoCameraIcon,
  BookmarkIcon,
  UserCircleIcon,
  LoginIcon,
} from "@heroicons/react/outline";

export default function NavBar() {
  const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;
  const location = useLocation();
  const navigate = useNavigate();

  const items = [
    { label: "Home", path: "/home", icon: HomeIcon },
    { label: "Upload", path: "/record", icon: VideoCameraIcon },
    { label: "Library", path: "/my-videos", icon: BookmarkIcon },
    { label: "Profile", path: "/profile", icon: UserCircleIcon },
  ];

  const handleSignOut = async () => {
    try {
      await axios.post(
        `${BACKEND_BASE_URL}/signout`,
        {},
        { withCredentials: true }
      );
    } catch (error) {
      console.error("Sign out failed:", error.response?.data || error.message);
    } finally {
      navigate("/");
    }
  };

  return (
    <div className="sticky top-0 z-50 border-b border-white/10 bg-black/40 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-10">
        <button onClick={() => navigate("/home")} className="text-left">
          <p className="text-xs uppercase tracking-[0.24em] text-zinc-500">
            ShotSense
          </p>
          <p className="text-lg font-semibold text-white">Training Intelligence Coach</p>
        </button>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] p-1">
            {items.map(({ label, path, icon: Icon }) => {
              const active = location.pathname === path;
              return (
                <button
                  key={path}
                  onClick={() => navigate(path)}
                  className={`flex items-center gap-2 rounded-full px-4 py-2 text-sm transition ${
                    active
                      ? "bg-white text-black"
                      : "text-zinc-300 hover:bg-white/[0.05] hover:text-white"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </button>
              );
            })}
          </div>

          <button
            onClick={handleSignOut}
            className="flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-zinc-300 transition hover:bg-white/[0.08] hover:text-white"
          >
            <LoginIcon className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </div>
    </div>
  );
}