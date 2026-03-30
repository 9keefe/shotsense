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

  const [openPhases, setOpenPhases] = useState({
    Setup: true,
    Release: false,
    "Follow-through": false,
  });
  const [activeMetrics, setActiveMetrics] = useState({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        const initialData = location.state?.analysisData;

        if (initialData) {
          setAnalysisData(initialData);
        } else {
          const shotResponse = await axios.get(
            `${BACKEND_BASE_URL}/shots/${id}`,
            { withCredentials: true }
          );
          setAnalysisData(shotResponse.data);
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
  const formScore = (safeProbability / 10).toFixed(1);
  const metrics = analysisData.metrics || {};
  const metricExplanations = analysisData.metric_explanations || {};
  const metricRanges = analysisData.metric_ranges || {};
  const setupMetrics = Object.entries(metrics).filter(([key]) =>
    key.startsWith("S ")
  );
  const releaseMetrics = Object.entries(metrics).filter(([key]) =>
    key.startsWith("R ")
  );
  const followMetrics = Object.entries(metrics).filter(([key]) =>
    key.startsWith("F ")
  );

  const formatMetricValue = (value) =>
    typeof value === "number" ? value.toFixed(1) : value;

  const getRangeVisualData = (metricKey, value) => {
    const range = metricRanges[metricKey];

    if (
      !range ||
      !range.has_range ||
      typeof value !== "number" ||
      typeof range.min !== "number" ||
      typeof range.max !== "number"
    ) {
      return null;
    }

    const span = Math.max(range.max - range.min, 1);
    const padding = Math.max(span * 0.5, 1);
    const domainMin = range.min - padding;
    const domainMax = range.max + padding;
    const domainSpan = domainMax - domainMin;
    const clampedValue = Math.min(Math.max(value, domainMin), domainMax);

    return {
      min: range.min,
      max: range.max,
      optimalStart: ((range.min - domainMin) / domainSpan) * 100,
      optimalEnd: ((range.max - domainMin) / domainSpan) * 100,
      optimalWidth: ((range.max - range.min) / domainSpan) * 100,
      markerPosition: ((clampedValue - domainMin) / domainSpan) * 100,
    };
  };

  const renderMetrics = (phaseTitle, metricPairs) => {
    if (!metricPairs || metricPairs.length === 0) {
      return <p className="text-sm text-zinc-500">No metrics available</p>;
    }

    return (
      <div className="grid grid-cols-1 gap-3">
        {metricPairs.map(([key, value]) => {
          const metricId = `${phaseTitle}-${key}`;
          const isMetricOpen = activeMetrics[metricId];
          const explanation = metricExplanations[key]?.explanation;
          const rangeVisual = getRangeVisualData(key, value);

          return (
            <button
              key={key}
              type="button"
              onClick={() => setActiveMetrics((prev) => ({
                ...prev,
                [metricId]: !prev[metricId]
              }))}
              className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-left transition hover:border-white/20"
            >
              <div className="flex items-center justify-between gap-4">
                <span className="text-sm text-zinc-400 tracking-wide">
                  {key.substring(2)}
                </span>
                <span className="font-mono text-sm text-white">
                  {typeof value === "number" ? value.toFixed(1) : value}
                </span>
              </div>

              {isMetricOpen && (
                <div className="mt-3 border-t border-white/10 pt-3 text-sm text-zinc-300">
                  <p>{explanation || "No explanation available yet."}</p>

                  {rangeVisual && (
                    <div className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-3">
                      <div className="mb-2 flex items-center justify-between text-xs text-zinc-400">
                        <span>Optimal range</span>
                        <span>
                          {formatMetricValue(rangeVisual.min)} - {formatMetricValue(rangeVisual.max)}
                        </span>
                      </div>

                      <div className="relative pt-6">
                        <div className="h-2 rounded-full bg-white/10">
                          <div
                            className="h-full rounded-full bg-emerald-400/80"
                            style={{
                              marginLeft: `${rangeVisual.optimalStart}%`,
                              width: `${rangeVisual.optimalWidth}%`,
                            }}
                          />
                        </div>

                        <div
                          className="absolute top-0 -translate-x-1/2 text-xs text-blue-300"
                          style={{ left: `${rangeVisual.markerPosition}%` }}
                        >
                          ▼
                        </div>

                        <div
                          className="absolute top-4 -translate-x-1/2 rounded-full border border-blue-400/20 bg-blue-500/10 px-2 py-0.5 text-[11px] text-blue-200"
                          style={{ left: `${rangeVisual.markerPosition}%` }}
                        >
                          {formatMetricValue(value)}
                        </div>
                      </div>

                      <div className="relative mt-5 h-4 text-[11px] text-zinc-500">
                        <span
                          className="absolute -translate-x-1/2"
                          style={{ left: `${rangeVisual.optimalStart}%` }}
                        >
                          {formatMetricValue(rangeVisual.min)}
                        </span>
                        <span
                          className="absolute -translate-x-1/2"
                          style={{ left: `${rangeVisual.optimalEnd}%` }}
                        >
                          {formatMetricValue(rangeVisual.max)}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </button>
          );
        })}
      </div>
    );
  };

  const PhaseCard = ({ title, image, metricPairs }) => {
    const isOpen = !!openPhases[title];

    return (
      <div
        className={`group rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)] transition-all duration-300 ${
          isOpen ? "ring-1 ring-blue-400/30" : "hover:border-white/20"
        }`}
      >
        {/* Header */}
        <button
          type="button"
          onClick={() =>
            setOpenPhases((prev) => ({
              ...prev,
              [title]: !prev[title],
            }))
          }
          className="mb-4 flex w-full items-center justify-between text-left"
        >
          <h3 className="text-lg font-semibold text-white">{title}</h3>

          <div className="flex items-center gap-2">
            <span className="rounded-full border border-blue-400/20 bg-blue-500/10 px-3 py-1 text-xs text-blue-300">
              Phase
            </span>

            {/* Chevron */}
            <span
              className={`text-zinc-500 transition-transform duration-300 ${
                isOpen ? "rotate-180" : ""
              }`}
            >
              ▾
            </span>
          </div>
        </button>

        {/* Image */}
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

        {/* Expandable metrics */}
        <div
          className={`transition-all duration-500 ${
            isOpen ? "opacity-100 mt-2" : "opacity-0 h-0 overflow-hidden"
          }`}
        >
          <div className="pt-2">{renderMetrics(title, metricPairs)}</div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[#0A0A0B] text-white relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.16),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(99,102,241,0.12),transparent_24%)]" />

      <div className="relative mx-auto max-w-7xl px-6 py-10 lg:px-10">
        {/* HEADER */}
        <div className="mb-8 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="mb-3 text-sm uppercase tracking-[0.24em] text-zinc-500">
              ShotSense
            </p>
            <h1 className="text-4xl font-semibold tracking-tight md:text-5xl">
              Shot Analysis
            </h1>
            <p className="mt-3 max-w-2xl text-zinc-400">
              Review biomechanics, identify inconsistencies, and refine shooting
              form with phase-level feedback.
            </p>
          </div>

          {/* SCORE CARD */}
          <div className="w-full max-w-sm rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
            <p className="text-sm text-zinc-400">Overall Form Score</p>

            <div className="mt-3 flex items-end gap-3">
              <span className="text-6xl font-semibold tracking-tight">
                {formScore}
              </span>
              <span className="mb-2 text-lg text-zinc-400">/ 10</span>
            </div>

            <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-gradient-to-r from-blue-400 to-indigo-500"
                style={{
                  width: `${Math.min(Number(formScore) * 10, 100)}%`,
                }}
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

        {/* MAIN GRID */}
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.35fr_0.95fr]">
          {/* LEFT */}
          <div className="space-y-6">
            {/* VIDEO */}
            <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold">Shot Replay</h2>
                <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-zinc-400">
                  Shot Video
                </span>
              </div>

              {analysisVideoUrl ? (
                <video
                  src={analysisVideoUrl}
                  controls
                  className="w-full rounded-2xl border border-white/10 bg-black"
                />
              ) : (
                <div className="flex h-80 items-center justify-center rounded-2xl border border-dashed border-white/10 bg-black/30 text-zinc-500">
                  No video available
                </div>
              )}
            </div>

            {/* FEEDBACK */}
            <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
              <h2 className="text-xl font-semibold">Coach Feedback</h2>

              {analysisData.form_feedback?.length > 0 ? (
                <div className="mt-4 space-y-3">
                  {analysisData.form_feedback.map((item, index) => (
                    <FeedbackItem key={index} feedback={item} />
                  ))}
                </div>
              ) : (
                <p className="mt-3 text-zinc-500">
                  No feedback messages available.
                </p>
              )}
            </div>
          </div>

          {/* RIGHT */}
          <div className="space-y-6">
            <PhaseCard
              title="Setup"
              image={setupFrameUrl}
              metricPairs={setupMetrics}
            />
            <PhaseCard
              title="Release"
              image={releaseFrameUrl}
              metricPairs={releaseMetrics}
            />
            <PhaseCard
              title="Follow-through"
              image={followFrameUrl}
              metricPairs={followMetrics}
            />
          </div>
        </div>
      </div>
    </div>
  );
}