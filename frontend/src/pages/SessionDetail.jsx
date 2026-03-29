import React, { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import ShotTimeline from "../components/ShotTimeline";
import {
  ArrowRightIcon
} from "@heroicons/react/outline";

const SESSION_FPS = 30;

function formatSessionDate(dateString) {
  if (!dateString) return "Unknown date";
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) return "Unknown date";

  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatTimeFromFrames(frameCount) {
  if (!Number.isFinite(frameCount) || frameCount < 0) return "0:00";
  const totalSeconds = Math.floor(frameCount / SESSION_FPS);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

export default function SessionDetail() {
  const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;
  const { id } = useParams();
  const navigate = useNavigate();
  const videoRef = useRef(null);

  const [sessionData, setSessionData] = useState(null);
  const [activeShotId, setActiveShotId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentFrame, setCurrentFrame] = useState(0);

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const response = await axios.get(`${BACKEND_BASE_URL}/sessions/${id}`, {
          withCredentials: true,
        });
        setSessionData(response.data);
      } catch (err) {
        if (err.response?.status === 401) {
          navigate("/signin");
          return;
        }
        setError("Failed to load session.");
      } finally {
        setLoading(false);
      }
    };

    fetchSession();
  }, [BACKEND_BASE_URL, id, navigate]);

  const handleTimelineShotClick = (shot) => {
    setActiveShotId(shot.id);

    if (videoRef.current) {
      videoRef.current.currentTime = shot.start_frame / SESSION_FPS;
      setCurrentFrame(shot.start_frame);
      videoRef.current.play().catch(() => {});
    }
  };

  const handleTimelineSeek = (frame) => {
    const safeFrame = Math.max(0, Math.min(frame, sessionData.total_frames || 0));
    setCurrentFrame(safeFrame);

    if (videoRef.current) {
      videoRef.current.currentTime = safeFrame / SESSION_FPS;
    }

    const matchingShot = shots.find(
      (shot) => safeFrame >= shot.start_frame && safeFrame <= shot.end_frame
    );

    setActiveShotId(matchingShot?.id || null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0B] text-white flex items-center justify-center">
        <div className="rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-zinc-300 backdrop-blur-xl">
          Loading session...
        </div>
      </div>
    );
  }

  if (error || !sessionData) {
    return (
      <div className="min-h-screen bg-[#0A0A0B] text-white flex items-center justify-center">
        <div className="rounded-2xl border border-red-400/20 bg-red-500/10 px-6 py-4 text-red-300 backdrop-blur-xl">
          {error || "Session not found"}
        </div>
      </div>
    );
  }

  const shots = sessionData.shots || [];
  const activeShot =
    shots.find((shot) => shot.id === activeShotId) || shots[0] || null;

  return (
    <div className="min-h-screen bg-[#0A0A0B] text-white relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.14),transparent_26%),radial-gradient(circle_at_bottom_right,rgba(99,102,241,0.10),transparent_22%)]" />

      <div className="relative mx-auto max-w-7xl px-6 py-10 lg:px-10">
        {/* Header */}
        <div className="mb-8 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-zinc-500">
              ShotSense
            </p>
            <h1 className="mt-3 text-4xl font-semibold tracking-tight md:text-5xl">
              Session Review
            </h1>
            <p className="mt-3 max-w-2xl text-zinc-400">
              Review a full uploaded training session, inspect automatically
              detected shot windows, and jump into individual shot analyses.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/5 px-5 py-4 backdrop-blur-xl">
              <p className="text-xs uppercase tracking-[0.18em] text-zinc-500">
                Shots
              </p>
              <p className="mt-2 text-white font-medium">{sessionData.shot_count}</p>
            </div>
            <div className="rounded-2xl border border-blue-400/20 bg-blue-500/10 px-5 py-4 backdrop-blur-xl">
              <p className="text-xs uppercase tracking-[0.18em] text-blue-300">
                Shooting Arm
              </p>
              <p className="mt-2 text-white font-medium">{sessionData.shooting_arm}</p>
            </div>
          </div>
        </div>

        {sessionData.processing_error && (
          <div className="mb-6 rounded-2xl border border-red-400/20 bg-red-500/10 px-5 py-4 text-sm text-red-300">
            {sessionData.processing_error}
          </div>
        )}

        {/* Main workspace */}
        <div className="grid grid-cols-1 gap-6">
          {/* Left */}
          <div className="space-y-6">
            <div className="rounded-[2rem] border border-white/10 bg-[#111214]/95 p-6 shadow-[0_10px_28px_rgba(0,0,0,0.24)]">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-white">
                    Full Session Video
                  </h2>
                  <p className="mt-1 text-sm text-zinc-400">
                    {formatSessionDate(sessionData.created_at)} ·{" "}
                    {formatTimeFromFrames(sessionData.total_frames || 0)}
                  </p>
                </div>

                <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-zinc-400">
                  Session Video
                </span>
              </div>

              {sessionData.original_video_url ? (
                <>
                  <div className="w-full">
                    <video
                      ref={videoRef}
                      src={sessionData.original_video_url}
                      controls
                      className="w-full rounded-[1.5rem] border border-white/10 bg-black shadow-[0_20px_50px_rgba(0,0,0,0.45)]"
                      onTimeUpdate={(e) => {
                        setCurrentFrame(Math.floor(e.target.currentTime * SESSION_FPS));
                      }}
                    />
                  </div>
                  <ShotTimeline
                    shots={shots}
                    totalFrames={sessionData.total_frames}
                    activeShotId={activeShotId}
                    currentFrame={currentFrame}
                    onShotClick={handleTimelineShotClick}
                    onSeek={handleTimelineSeek}
                  />

                </>
              ) : (
                <div className="flex h-72 items-center justify-center rounded-[1.5rem] border border-dashed border-white/10 bg-black/30 text-zinc-500">
                  No session video available.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Detected shots */}
        <div className="mt-6 rounded-[2rem] border border-white/10 bg-white/5 p-6 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-white">Detected Shots</h2>
              <p className="mt-1 text-sm text-zinc-400">
                Open any extracted shot to view full phase-level analysis.
              </p>
            </div>
          </div>

          {shots.length ? (
            <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
              {shots.map((shot) => {
                const score = shot.make_probability
                  ? (shot.make_probability / 10).toFixed(1)
                  : "0.0";

                return (
                  <div
                    key={shot.id}
                    className="rounded-[1.75rem] border border-white/10 bg-white/[0.03] p-5"
                  >
                    <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                      <div>
                        <div className="mb-3 inline-flex rounded-full border border-blue-400/20 bg-blue-500/10 px-3 py-1 text-[11px] uppercase tracking-[0.18em] text-blue-300">
                          Shot {shot.shot_index}
                        </div>

                        <h3 className="text-lg font-semibold text-white">
                          Shot Analysis Segment
                        </h3>
                        <p className="mt-2 text-sm text-zinc-400">
                          {formatTimeFromFrames(shot.start_frame)} –{" "}
                          {formatTimeFromFrames(shot.end_frame)} · Frames{" "}
                          {shot.start_frame}-{shot.end_frame}
                        </p>
                        <p className="mt-1 text-sm text-zinc-400">
                          Form score:{" "}
                          <span className="font-mono text-white">{score}/10</span>
                        </p>
                      </div>

                      <button
                        onClick={() => navigate(`/analysis/${shot.id}`)}
                        className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2.5 text-sm font-medium text-black transition hover:bg-zinc-200"
                      >
                        Open Analysis
                        <ArrowRightIcon className="h-4 w-4" />
                      </button>
                    </div>

                    {shot.video_url ? (
                      <div className="mt-5">
                        <video
                          src={shot.video_url}
                          controls
                          className="w-full rounded-[1.25rem] border border-white/10 bg-black"
                        />
                      </div>
                    ) : null}
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-sm text-zinc-400">No shots found for this session.</p>
          )}
        </div>
      </div>
    </div>
  );
}