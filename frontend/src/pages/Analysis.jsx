import React, { useEffect, useState } from "react";
import { useParams, useLocation } from "react-router-dom";
import axios from "axios";

export default function Analysis() {
  const { id } = useParams();
  const location = useLocation();
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Check both possible data sources
        const initialData = location.state?.analysisData;
        
        if (initialData) {
          setAnalysisData(initialData);
        } else {
          const response = await axios.get(
            `http://127.0.0.1:5000/analyses/${id}`,
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
  }, [id, location.state]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-700">Loading analysis...</p>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-700">Analysis not found</p>
      </div>
    );
  }

  // Unified video URL handling
  const originalVideoUrl = analysisData.original_video_url || analysisData.originalVideoUrl;
  const analysisVideoUrl = analysisData.video_url;
  const setupFrameUrl = analysisData.setup_frame_url;
  const releaseFrameUrl = analysisData.release_frame_url;
  const followFrameUrl = analysisData.follow_frame_url;
  const safeProbability = analysisData.make_probability || 0;

  const metrics = analysisData.metrics || {};
  const setupMetrics = Object.entries(metrics).filter(([key]) => key.startsWith("S_"));
  const releaseMetrics = Object.entries(metrics).filter(([key]) => key.startsWith("R_"));
  const followMetrics = Object.entries(metrics).filter(([key]) => key.startsWith("F_"));

  return (
    <div className="min-h-screen flex flex-col items-center pt-8 px-4 space-y-8 pb-40">
      <h1 className="text-2xl font-bold mb-4">Analysis</h1>

      {/* Original Video
      {originalVideoUrl && (
        <div className="w-full max-w-xl mb-4">
          <h2 className="text-xl font-semibold mb-2">Original Video</h2>
          <video src={originalVideoUrl} controls className="w-full bg-black">
            Your browser does not support video.
          </video>
        </div>
      )} */}

      {/* Analysis (Processed) Video */}
      {analysisVideoUrl && (
        <div className="w-full max-w-xl mb-4">
          <h2 className="text-xl font-semibold mb-2">Analysis Video</h2>
          <video src={analysisVideoUrl} controls className="w-full bg-black">
            Your browser does not support video.
          </video>
        </div>
      )}

      <div className="max-w-xl bg-white p-4 rounded shadow mb-4 w-full">
        <h2 className="text-xl font-semibold mb-2">Shot Success Probability</h2>
        <p className="text-lg">
          {(safeProbability * 100).toFixed(1)}% chance of making the shot
        </p>
      </div>

      {/* Setup Analysis */}
      <div className="max-w-xl bg-white p-4 rounded shadow w-full space-y-4">
        <h2 className="text-xl font-semibold mb-2">Setup Analysis</h2>
        {setupFrameUrl ? (
          <img src={setupFrameUrl} alt="Setup Phase Frame" className="w-full" />
        ) : (
          <p>No setup frame available</p>
        )}
        {setupMetrics.length > 0 ? (
          <ul className="list-disc list-inside text-gray-800">
            {setupMetrics.map(([key, value]) => (
              <li key={key}>
                <strong>{key}:</strong> {typeof value === "number" ? value.toFixed(2) : value}
              </li>
            ))}
          </ul>
        ) : (
          <p>No setup metrics available</p>
        )}
      </div>

      {/* Release Analysis */}
      <div className="max-w-xl bg-white p-4 rounded shadow w-full space-y-4">
        <h2 className="text-xl font-semibold mb-2">Release Analysis</h2>
        {releaseFrameUrl ? (
          <img src={releaseFrameUrl} alt="Release Phase Frame" className="w-full" />
        ) : (
          <p>No release frame available</p>
        )}
        {releaseMetrics.length > 0 ? (
          <ul className="list-disc list-inside text-gray-800">
            {releaseMetrics.map(([key, value]) => (
              <li key={key}>
                <strong>{key}:</strong> {typeof value === "number" ? value.toFixed(2) : value}
              </li>
            ))}
          </ul>
        ) : (
          <p>No release metrics available</p>
        )}
      </div>

      {/* Follow-through Analysis */}
      <div className="max-w-xl bg-white p-4 rounded shadow w-full space-y-4">
        <h2 className="text-xl font-semibold mb-2">Follow-Through Analysis</h2>
        {followFrameUrl ? (
          <img src={followFrameUrl} alt="Follow-Through Phase Frame" className="w-full" />
        ) : (
          <p>No follow-through frame available</p>
        )}
        {followMetrics.length > 0 ? (
          <ul className="list-disc list-inside text-gray-800">
            {followMetrics.map(([key, value]) => (
              <li key={key}>
                <strong>{key}:</strong> {typeof value === "number" ? value.toFixed(2) : value}
              </li>
            ))}
          </ul>
        ) : (
          <p>No follow-through metrics available</p>
        )}
      </div>
    </div>
  );
}