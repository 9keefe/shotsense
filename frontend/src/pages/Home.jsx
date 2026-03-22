import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import {
  ArrowRightIcon,
  SparklesIcon,
  LightBulbIcon,
  ChartBarIcon,
  VideoCameraIcon,
} from "@heroicons/react/outline";

export default function Home() {
  const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;
  const [name, setName] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get(`${BACKEND_BASE_URL}/user`, {
          withCredentials: true,
        });
        setName(response.data.name);
      } catch (error) {
        console.error(
          "Failed to fetch profile:",
          error.response?.data?.error || error.message
        );
        navigate("/signin");
      }
    };

    fetchProfile();
  }, [navigate, BACKEND_BASE_URL]);

  const ActionCard = ({ title, description, icon: Icon, onClick, accent = "blue" }) => {
    const accentStyles =
      accent === "blue"
        ? "border-blue-400/20 bg-blue-500/10 text-blue-300"
        : accent === "emerald"
        ? "border-emerald-400/20 bg-emerald-500/10 text-emerald-300"
        : "border-white/10 bg-white/[0.06] text-zinc-300";

    return (
      <button
        onClick={onClick}
        className="group w-full rounded-3xl border border-white/10 bg-white/5 p-6 text-left backdrop-blur-xl transition hover:bg-white/[0.07] hover:-translate-y-0.5"
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <div
              className={`mb-4 inline-flex rounded-full border px-3 py-1 text-[11px] uppercase tracking-[0.18em] ${accentStyles}`}
            >
              {title}
            </div>
            <h3 className="text-xl font-semibold text-white">{title}</h3>
            <p className="mt-2 max-w-sm text-sm leading-6 text-zinc-400">
              {description}
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-3 text-zinc-300 transition group-hover:text-white">
            <Icon className="h-6 w-6" />
          </div>
        </div>

        <div className="mt-8 flex items-center gap-2 text-sm text-zinc-400 group-hover:text-white">
          Open
          <ArrowRightIcon className="h-4 w-4" />
        </div>
      </button>
    );
  };

  return (
    <div className="min-h-screen bg-[#0A0A0B] text-white relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.16),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(99,102,241,0.10),transparent_24%)]" />

      <div className="relative mx-auto max-w-7xl px-6 py-10 lg:px-10">
        {/* Hero */}
        <div className="mb-8 grid grid-cols-1 gap-6 xl:grid-cols-[1.25fr_0.75fr]">
          <div className="rounded-[2rem] border border-white/10 bg-white/5 p-8 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
            <p className="text-xs uppercase tracking-[0.24em] text-zinc-500">
              ShotSense
            </p>

            <div className="mt-6 flex items-start justify-between gap-6">
              <div>
                <h1 className="text-4xl font-semibold tracking-tight md:text-5xl">
                  Welcome back,
                </h1>
                <p className="mt-2 text-4xl font-semibold tracking-tight text-blue-300 md:text-5xl">
                  {name}
                </p>

                <p className="mt-5 max-w-2xl text-sm leading-7 text-zinc-400 md:text-base">
                  Review shooting mechanics, track form consistency, and refine
                  training with a cleaner phase-by-phase analytics workflow.
                </p>
              </div>
            </div>

            <div className="mt-8 flex flex-wrap gap-3">
              <button
                onClick={() => navigate("/record")}
                className="rounded-full bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-zinc-200"
              >
                Start New Analysis
              </button>
              <button
                onClick={() => navigate("/my-videos")}
                className="rounded-full border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]"
              >
                View Session Library
              </button>
            </div>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-white/5 p-8 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
            <p className="text-sm text-zinc-400">System Overview</p>

            <div className="mt-6 space-y-4">
              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">
                  Workflow
                </p>
                <p className="mt-2 text-lg font-medium text-white">
                  Upload → Analyse → Review → Improve
                </p>
              </div>

              <div className="rounded-2xl border border-blue-400/20 bg-blue-500/10 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-blue-300">
                  Core Focus
                </p>
                <p className="mt-2 text-lg font-medium text-white">
                  Mechanics, consistency, and usable training feedback
                </p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">
                  Product Tone
                </p>
                <p className="mt-2 text-lg font-medium text-white">
                  Precision-led, premium, and athlete-focused
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Main cards */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
          <ActionCard
            title="Quick Fixes"
            description="Review the highest-priority mechanical issues and focus on the most impactful adjustments first."
            icon={SparklesIcon}
            accent="blue"
            onClick={() => navigate("/my-videos")}
          />

          <ActionCard
            title="Quick Tips"
            // description="Surface concise coaching cues and reminders that can be applied immediately in the next session."
            description="NOT LIVE YET"
            icon={LightBulbIcon}
            accent="neutral"
            onClick={() => navigate("/my-videos")}
          />

          <ActionCard
            title="Analytics"
            // description="Inspect phase-level metrics, replay sessions, and evaluate form quality with structured feedback."
            description="NOT LIVE YET"
            icon={ChartBarIcon}
            accent="emerald"
            onClick={() => navigate("/my-videos")}
          />

          <ActionCard
            title="Past Sessions"
            description="Browse previous uploads, revisit analysis results, and compare sessions over time."
            icon={VideoCameraIcon}
            accent="blue"
            onClick={() => navigate("/my-videos")}
          />
        </div>
      </div>
    </div>
  );
}