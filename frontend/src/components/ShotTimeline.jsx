import React, { useRef, useState } from "react";

const SESSION_FPS = 30;

function formatTimeFromFrames(frameCount) {
  if (!Number.isFinite(frameCount) || frameCount < 0) {
    return "0:00";
  }

  const totalSeconds = Math.floor(frameCount / SESSION_FPS);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;

  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

export default function ShotTimeline({
  shots = [],
  totalFrames,
  onShotClick,
  activeShotId,
  currentFrame = 0,
  onSeek,
}) {
  const timelineRef = useRef(null);
  const [isScrubbing, setIsScrubbing] = useState(false);

  if (!shots.length || !Number.isFinite(totalFrames) || totalFrames <= 0) {
    return null;
  }

  const playheadPercent = Math.min(
    Math.max((currentFrame / totalFrames) * 100, 0),
    100
  );

  const getFrameFromClientX = (clientX) => {
    if (!timelineRef.current) return 0;

    const rect = timelineRef.current.getBoundingClientRect();
    const x = Math.min(Math.max(clientX - rect.left, 0), rect.width);
    const percent = x / rect.width;
    return Math.round(percent * totalFrames);
  };

  const seekFromClientX = (clientX) => {
    const frame = getFrameFromClientX(clientX);
    onSeek?.(frame);
  };

  const handleMouseDown = (e) => {
    setIsScrubbing(true);
    seekFromClientX(e.clientX);
  };

  const handleMouseMove = (e) => {
    if (!isScrubbing) return;
    seekFromClientX(e.clientX);
  };

  const handleMouseUp = () => {
    setIsScrubbing(false);
  };

  const handleMouseLeave = () => {
    if (isScrubbing) {
      setIsScrubbing(false);
    }
  };

  return (
    <div className="mt-5 rounded-2xl border border-zinc-800 bg-zinc-950/70 p-5">
      <div className="mb-4 flex items-center justify-between text-xs">
        <span className="uppercase tracking-[0.18em] text-zinc-500">
          Session Timeline
        </span>
        <span className="text-zinc-400">{shots.length} detected shots</span>
      </div>

      <div
        ref={timelineRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseLeave}
        style={{
          position: "relative",
          width: "100%",
          height: "96px",
          borderRadius: "18px",
          overflow: "hidden",
          border: "1px solid rgba(255,255,255,0.08)",
          background: "rgba(20,20,23,0.96)",
          cursor: isScrubbing ? "grabbing" : "pointer",
          userSelect: "none",
        }}
      >
        {/* faux video strip blocks */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "grid",
            gridTemplateColumns: "repeat(16, 1fr)",
          }}
        >
          {Array.from({ length: 16 }).map((_, i) => (
            <div
              key={i}
              style={{
                borderRight: "1px solid rgba(255,255,255,0.03)",
                background:
                  i % 2 === 0
                    ? "rgba(255,255,255,0.04)"
                    : "rgba(255,255,255,0.025)",
              }}
            />
          ))}
        </div>

        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "rgba(0,0,0,0.55)",
          }}
        />

        {shots.map((shot) => {
          const rawLeft = (Number(shot.start_frame) / totalFrames) * 100;
          const rawWidth =
            ((Number(shot.end_frame) - Number(shot.start_frame) + 1) / totalFrames) * 100;

          const left = Math.min(Math.max(rawLeft, 0), 100);
          const width = Math.max(Math.min(rawWidth, 100 - left), 2);
          const isActive = shot.id === activeShotId;

          return (
            <button
              key={shot.id}
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onShotClick?.(shot);
              }}
              title={`Shot ${shot.shot_index} · ${formatTimeFromFrames(Number(shot.start_frame))}`}
              style={{
                position: "absolute",
                top: "8px",
                bottom: "8px",
                left: `${left}%`,
                width: `${width}%`,
                borderRadius: "12px",
                border: isActive
                  ? "1px solid rgba(147,197,253,0.8)"
                  : "1px solid rgba(255,255,255,0.16)",
                background: isActive
                  ? "rgba(59,130,246,0.35)"
                  : "rgba(255,255,255,0.16)",
                boxShadow: "none",
                cursor: "pointer",
              }}
            >
              {width > 8 && (
                <div
                  style={{
                    position: "absolute",
                    left: "8px",
                    right: "8px",
                    bottom: "6px",
                    display: "flex",
                    justifyContent: "space-between",
                    fontSize: "10px",
                    color: "rgba(255,255,255,0.9)",
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                  }}
                >
                  <span>{`Shot ${shot.shot_index}`}</span>
                  <span>{formatTimeFromFrames(Number(shot.start_frame))}</span>
                </div>
              )}
            </button>
          );
        })}

        <div
          style={{
            position: "absolute",
            top: 0,
            bottom: 0,
            left: `${playheadPercent}%`,
            width: "2px",
            background: "rgba(255,255,255,0.92)",
            pointerEvents: "none",
          }}
        >
          <div
            style={{
              position: "absolute",
              top: "-2px",
              left: "50%",
              transform: "translateX(-50%)",
              width: "10px",
              height: "10px",
              borderRadius: "999px",
              background: "white",
            }}
          />
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between text-[11px] text-zinc-500">
        <span>0:00</span>
        <span>Click or drag anywhere on the timeline to seek</span>
        <span>{formatTimeFromFrames(totalFrames)}</span>
      </div>
    </div>
  );
}