import React, { useState } from "react";
import { PlusIcon, UploadIcon } from "@heroicons/react/outline";
import { useNavigate } from "react-router-dom";

export default function Record() {
  const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [shootingArm, setShootingArm] = useState("RIGHT");
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();

  const toggleModal = () => setIsModalOpen(!isModalOpen);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsLoading(true);

    const formData = new FormData();
    formData.append("video", selectedFile);
    formData.append("shootingArm", shootingArm);

    try {
      const res = await fetch(`${BACKEND_BASE_URL}/upload`, {
        method: "POST",
        body: formData,
        credentials: "include",
      });

      if (!res.ok) {
        setIsLoading(false);
        const { error } = await res.json();
        alert("Upload error: " + error);
        return;
      }

      const data = await res.json();
      setIsLoading(false);
      setIsModalOpen(false);

      navigate(`/analysis/${data.analysis_id}`, {
        state: {
          video_url: data.originalVideoUrl,
          metrics: data.metrics,
          make_probability: data.make_probability,
          form_feedback: data.form_feedback
        },
      });

    } catch (err) {
      setIsLoading(false);
      console.error(err);
      alert("Upload failed, check console for details.");
    }
  };

  const TogglePill = ({ value, label }) => {
    const active = shootingArm === value;

    return (
      <button
        type="button"
        onClick={() => setShootingArm(value)}
        className={`rounded-full px-4 py-2 text-sm font-medium transition ${
          active
            ? "bg-white text-black"
            : "bg-white/[0.05] text-zinc-300 hover:bg-white/[0.08]"
        }`}
      >
        {label}
      </button>
    );
  };

  return (
    <div className="min-h-screen bg-[#0A0A0B] text-white relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.14),transparent_26%),radial-gradient(circle_at_bottom_right,rgba(99,102,241,0.10),transparent_22%)]" />

      <div className="relative mx-auto max-w-7xl px-6 py-10 lg:px-10">
        <div className="mb-8">
          <p className="text-xs uppercase tracking-[0.24em] text-zinc-500">
            ShotSense
          </p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight md:text-5xl">
            New Analysis
          </h1>
          <p className="mt-3 max-w-2xl text-zinc-400">
            Upload a shooting clip, select the shooting arm, and generate a full
            mechanical breakdown across setup, release, and follow-through.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-[2rem] border border-white/10 bg-white/5 p-6 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-white">
                Upload Workspace
              </h2>
              <span className="rounded-full border border-blue-400/20 bg-blue-500/10 px-3 py-1 text-xs text-blue-300">
                Desktop Flow
              </span>
            </div>

            <div className="flex h-[480px] items-center justify-center rounded-[1.75rem] border border-dashed border-white/10 bg-black/30">
              <div className="text-center">
                <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-3xl border border-white/10 bg-white/[0.04]">
                  <UploadIcon className="h-10 w-10 text-zinc-300" />
                </div>

                <h3 className="mt-6 text-2xl font-semibold text-white">
                  Upload a shooting clip
                </h3>
                <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-zinc-400">
                  Use a clean side-on recording where the shooter and full motion
                  are clearly visible for more reliable pose analysis.
                </p>

                <button
                  onClick={toggleModal}
                  className="mt-8 inline-flex items-center gap-2 rounded-full bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-zinc-200"
                >
                  <PlusIcon className="h-4 w-4" />
                  Select Video
                </button>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-[2rem] border border-white/10 bg-white/5 p-6 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
              <p className="text-sm text-zinc-400">Recommended Setup</p>

              <div className="mt-5 space-y-4">
                <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">
                    Camera angle
                  </p>
                  <p className="mt-2 text-white">Side-on view preferred</p>
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">
                    Frame quality
                  </p>
                  <p className="mt-2 text-white">
                    Full body visible with clear joint motion
                  </p>
                </div>

                <div className="rounded-2xl border border-blue-400/20 bg-blue-500/10 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-blue-300">
                    Output
                  </p>
                  <p className="mt-2 text-white">
                    Video replay, phase frames, metrics, and coaching feedback
                  </p>
                </div>
              </div>
            </div>

            {/* <div className="rounded-[2rem] border border-white/10 bg-white/5 p-6 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
              <p className="text-sm text-zinc-400">Current Selection</p>
              <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">
                  File
                </p>
                <p className="mt-2 truncate text-white">
                  {selectedFile ? selectedFile.name : "No file selected"}
                </p>
              </div>

              <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">
                  Shooting arm
                </p>
                <p className="mt-2 text-white">
                  {shootingArm === "RIGHT" ? "Right-handed shot" : "Left-handed shot"}
                </p>
              </div>
            </div> */}
          </div>
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4 backdrop-blur-sm">
          <div className="relative w-full max-w-xl rounded-[2rem] border border-white/10 bg-[#111214] p-8 text-white shadow-[0_20px_80px_rgba(0,0,0,0.55)]">
            <button
              onClick={toggleModal}
              className="absolute right-5 top-5 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-sm text-zinc-300 transition hover:bg-white/[0.08] hover:text-white"
            >
              ✕
            </button>

            <p className="text-xs uppercase tracking-[0.24em] text-zinc-500">
              Upload Session
            </p>
            <h2 className="mt-3 text-2xl font-semibold text-white">
              Add a new shooting video
            </h2>
            <p className="mt-2 text-sm leading-6 text-zinc-400">
              Select the video file and confirm the shooting arm before starting
              analysis.
            </p>

            <div className="mt-8">
              <label className="mb-3 block text-sm text-zinc-400">
                Shooting Arm
              </label>
              <div className="inline-flex rounded-full border border-white/10 bg-white/[0.04] p-1">
                <TogglePill value="RIGHT" label="Right" />
                <TogglePill value="LEFT" label="Left" />
              </div>
            </div>

            <div className="mt-8">
              <label className="mb-3 block text-sm text-zinc-400">
                Video File
              </label>
              <input
                type="file"
                accept="video/*"
                onChange={handleFileChange}
                className="block w-full rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-zinc-300 file:mr-4 file:rounded-full file:border-0 file:bg-white file:px-4 file:py-2 file:text-sm file:font-medium file:text-black hover:file:bg-zinc-200"
              />
            </div>

            <div className="mt-8 flex items-center justify-between gap-4">
              <div className="text-sm text-zinc-500">
                {selectedFile ? selectedFile.name : "No file selected"}
              </div>

              <button
                onClick={handleUpload}
                disabled={!selectedFile}
                className="rounded-full bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Start Analysis
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
          <div className="rounded-[2rem] border border-white/10 bg-[#111214] px-8 py-6 text-center shadow-[0_20px_80px_rgba(0,0,0,0.55)]">
            <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-white/20 border-t-white" />
            <p className="mt-4 text-sm text-zinc-300">
              Processing video and generating analysis...
            </p>
          </div>
        </div>
      )}
    </div>
  );
}