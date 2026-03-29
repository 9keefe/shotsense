import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import {
  ArrowRightIcon,
  FilmIcon,
  PlusIcon,
} from "@heroicons/react/outline";

export default function MyVideos() {
  const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        await axios.get(`${BACKEND_BASE_URL}/user`, {
          withCredentials: true,
        });

        const sessionsRes = await axios.get(`${BACKEND_BASE_URL}/sessions`, {
          withCredentials: true,
        });

        setSessions(sessionsRes.data);
      } catch (err) {
        if (err.response?.status === 401) {
          navigate("/signin");
        } else {
          setError("Failed to load sessions. Please try again later.");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate, BACKEND_BASE_URL]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0B] text-white flex items-center justify-center">
        <div className="rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-zinc-300 backdrop-blur-xl">
          Loading session library...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#0A0A0B] text-white flex items-center justify-center">
        <div className="rounded-2xl border border-red-400/20 bg-red-500/10 px-6 py-4 text-red-300 backdrop-blur-xl">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0A0A0B] text-white relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.14),transparent_26%),radial-gradient(circle_at_bottom_right,rgba(99,102,241,0.10),transparent_22%)]" />

      <div className="relative mx-auto max-w-7xl px-6 py-10 lg:px-10">
        <div className="mb-8 flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-zinc-500">
              ShotSense
            </p>
            <h1 className="mt-3 text-4xl font-semibold tracking-tight md:text-5xl">
              Session Library
            </h1>
            <p className="mt-3 max-w-2xl text-zinc-400">
              Revisit previous uploads, inspect analysis results, and keep a
              clean archive of training sessions.
            </p>
          </div>

          <button
            onClick={() => navigate("/record")}
            className="inline-flex items-center gap-2 rounded-full bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-zinc-200"
          >
            <PlusIcon className="h-4 w-4" />
            New Upload
          </button>
        </div>

        {sessions.length === 0 ? (
          <div className="rounded-[2rem] border border-white/10 bg-white/5 p-10 text-center backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04]">
              <FilmIcon className="h-7 w-7 text-zinc-300" />
            </div>

            <h2 className="mt-6 text-2xl font-semibold text-white">
              No sessions yet
            </h2>
            <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-zinc-400">
              Upload the first shooting clip to start building a private library
              of analysed sessions.
            </p>

            <button
              onClick={() => navigate("/record")}
              className="mt-8 rounded-full bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-zinc-200"
            >
              Upload First Video
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
            {sessions.map((session, index) => (
              <button
                key={session.id}
                onClick={() => navigate(`/sessions/${session.id}`)}
                className="group rounded-[2rem] border border-white/10 bg-white/5 p-5 text-left backdrop-blur-xl transition hover:bg-white/[0.07] hover:-translate-y-0.5"
              >
                <div className="grid grid-cols-1 gap-5 md:grid-cols-[1fr_220px]">
                  <div className="flex min-w-0 flex-col justify-between">
                    <div>
                      <div className="mb-3 inline-flex rounded-full border border-blue-400/20 bg-blue-500/10 px-3 py-1 text-[11px] uppercase tracking-[0.18em] text-blue-300">
                        Session {String(index + 1).padStart(2, "0")}
                      </div>

                      <h3 className="text-xl font-semibold text-white">
                        {new Date(session.created_at).toLocaleDateString(
                          "en-US",
                          {
                            month: "short",
                            day: "numeric",
                            year: "numeric",
                          }
                        )}
                      </h3>

                      <p className="mt-2 text-sm text-zinc-400">
                        Status: {session.status} · Shots: {session.shot_count}
                      </p>

                      {/* <p className="mt-2 text-sm leading-6 text-zinc-400">
                        Open the full breakdown to review video replay, coaching
                        feedback, and phase-level shooting metrics.
                      </p> */}
                    </div>

                    <div className="mt-6 flex items-center gap-2 text-sm text-zinc-400 group-hover:text-white">
                      View session
                      <ArrowRightIcon className="h-4 w-4" />
                    </div>
                  </div>

                  <div className="relative h-48 overflow-hidden rounded-3xl border border-white/10 bg-black">
                    {session.preview_video_url ? (
                      <video
                        src={session.preview_video_url}
                        className="h-full w-full object-cover"
                        muted
                        onMouseOver={(e) => e.target.play()}
                        onMouseOut={(e) => {
                          e.target.pause();
                          e.target.currentTime = 0;
                        }}
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center text-sm text-zinc-500">
                        No preview yet
                      </div>
                    )}
                    <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent" />
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}