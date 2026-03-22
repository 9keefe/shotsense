import React, { useEffect, useState } from "react";
import { useParams, useLocation } from "react-router-dom";
import axios from "axios";
import FeedbackItem from "../components/FeedbackItem";

export default function Analysis() {
  const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;
  const { id } = useParams();
  const location = useLocation();
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const initialData = location.state?.analysisData;

        if (initialData) {
          setAnalysisData(initialData);
        } else {
          const response = await axios.get(
            `${BACKEND_BASE_URL}/analyses/${id}`,
            { withCredentials: true }
          );
          setAnalysisData(response.data);
        }
      } catch (error) {
        console.error("Error loading analysis:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id, location.state, BACKEND_BASE_URL]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0B] text-white flex items-center justify-center">
        <div className="rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-zinc-300 backdrop-blur-xl">
          Loading analysis...
        </div>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="min-h-screen bg-[#0A0A0B] text-white flex items-center justify-center">
        <div className="rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-zinc-300 backdrop-blur-xl">
          Analysis not found
        </div>
      </div>
    );
  }

  const analysisVideoUrl = analysisData.video_url;
  const setupFrameUrl = analysisData.setup_frame_url;
  const releaseFrameUrl = analysisData.release_frame_url;
  const followFrameUrl = analysisData.follow_frame_url;
  const safeProbability = analysisData.make_probability || 0;

  const metrics = analysisData.metrics || {};
  const setupMetrics = Object.entries(metrics).filter(([key]) => key.startsWith("S "));
  const releaseMetrics = Object.entries(metrics).filter(([key]) => key.startsWith("R "));
  const followMetrics = Object.entries(metrics).filter(([key]) => key.startsWith("F "));

  const formScore = (safeProbability / 10).toFixed(1);

  const renderMetrics = (metricPairs) => {
    if (!metricPairs || metricPairs.length === 0) {
      return <p className="text-sm text-zinc-500">No metrics available</p>;
    }

    return (
      <div className="grid grid-cols-1 gap-3">
        {metricPairs.map(([key, value]) => (
          <div
            key={key}
            className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3"
          >
            <span className="text-sm text-zinc-400 tracking-wide">
              {key.substring(2)}
            </span>
            <span className="font-mono text-sm text-white">
              {typeof value === "number" ? value.toFixed(1) : value}
            </span>
          </div>
        ))}
      </div>
    );
  };

  const PhaseCard = ({ title, image, metricPairs }) => (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        <span className="rounded-full border border-blue-400/20 bg-blue-500/10 px-3 py-1 text-xs text-blue-300">
          Phase
        </span>
      </div>

      {image ? (
        <img
          src={image}
          alt={`${title} frame`}
          className="mb-4 h-56 w-full rounded-2xl object-cover border border-white/10"
        />
      ) : (
        <div className="mb-4 flex h-56 items-center justify-center rounded-2xl border border-dashed border-white/10 bg-white/[0.02] text-zinc-500">
          No frame available
        </div>
      )}

      {renderMetrics(metricPairs)}
    </div>
  );

  return (
    <div className="min-h-screen bg-[#0A0A0B] text-white relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.16),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(99,102,241,0.12),transparent_24%)]" />

      <div className="relative mx-auto max-w-7xl px-6 py-10 lg:px-10">
        <div className="mb-8 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="mb-3 text-sm uppercase tracking-[0.24em] text-zinc-500">
              ShotSense
            </p>
            <h1 className="text-4xl font-semibold tracking-tight md:text-5xl">
              Shot Analysis
            </h1>
            <p className="mt-3 max-w-2xl text-zinc-400">
              Review biomechanics, identify inconsistencies, and refine shooting form with phase-level feedback.
            </p>
          </div>

          <div className="w-full max-w-sm rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
            <p className="text-sm text-zinc-400">Overall Form Score</p>
            <div className="mt-3 flex items-end gap-3">
              <span className="text-6xl font-semibold tracking-tight">{formScore}</span>
              <span className="mb-2 text-lg text-zinc-400">/ 10</span>
            </div>
            <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-gradient-to-r from-blue-400 to-indigo-500"
                style={{ width: `${Math.min(Number(formScore) * 10, 100)}%` }}
              />
            </div>
            <div className="mt-4 flex gap-2">
              <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-zinc-300">
                Biomechanics
              </span>
              <span className="rounded-full border border-blue-400/20 bg-blue-500/10 px-3 py-1 text-xs text-blue-300">
                AI Feedback
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.35fr_0.95fr]">
          <div className="space-y-6">
            <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold">Shot Replay</h2>
                <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-zinc-400">
                  Session Video
                </span>
              </div>

              {analysisVideoUrl ? (
                <video
                  src={analysisVideoUrl}
                  controls
                  className="w-full rounded-2xl border border-white/10 bg-black"
                >
                  Your browser does not support video.
                </video>
              ) : (
                <div className="flex h-80 items-center justify-center rounded-2xl border border-dashed border-white/10 bg-black/30 text-zinc-500">
                  No video available
                </div>
              )}
            </div>

            <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
              <div className="mb-5 flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold">Coach Feedback</h2>
                  <p className="mt-1 text-sm text-zinc-400">
                    Priority form adjustments from the analysis pipeline
                  </p>
                </div>
              </div>

              {analysisData.form_feedback && analysisData.form_feedback.length > 0 ? (
                <div className="space-y-3">
                  {analysisData.form_feedback.map((item, index) => (
                    <FeedbackItem key={index} feedback={item} />
                  ))}
                </div>
              ) : (
                <p className="text-zinc-500">No feedback messages available.</p>
              )}
            </div>
          </div>

          <div className="space-y-6">
            <PhaseCard title="Setup" image={setupFrameUrl} metricPairs={setupMetrics} />
            <PhaseCard title="Release" image={releaseFrameUrl} metricPairs={releaseMetrics} />
            <PhaseCard title="Follow-through" image={followFrameUrl} metricPairs={followMetrics} />
          </div>
        </div>
      </div>
    </div>
  );
}