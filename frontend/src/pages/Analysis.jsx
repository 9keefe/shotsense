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
        // Check both possible data sources
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
  const analysisVideoUrl = analysisData.video_url;
  const setupFrameUrl = analysisData.setup_frame_url;
  const releaseFrameUrl = analysisData.release_frame_url;
  const followFrameUrl = analysisData.follow_frame_url;
  const safeProbability = analysisData.make_probability || 0;

  const metrics = analysisData.metrics || {};
  const setupMetrics = Object.entries(metrics).filter(([key]) => key.startsWith("S "));
  const releaseMetrics = Object.entries(metrics).filter(([key]) => key.startsWith("R "));
  const followMetrics = Object.entries(metrics).filter(([key]) => key.startsWith("F "));

  const renderMetrics = (metricPairs) => {
    if (!metricPairs || metricPairs.length === 0) {
      return <p className="text-gray-500">No metrics available</p>;
    }
    return (
      <div>
        {metricPairs.map(([key, value]) => (
          <div
            key={key}
            className="rounded-md px-2 py-0.5 text-sm text-gray-700"
          >
            {key.substring(2)}:{" "}
            {typeof value === "number" ? value.toFixed(1) : value}
          </div>
        ))}
      </div>
    );
  };

return (
    <div className="min-h-screen flex flex-col bg-orange-500 ">
      {/* Top Header Section */}
      <div className="p-6">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-5xl font-bold text-white py-5 mt-3">Analysis</h1>
          {analysisVideoUrl && (
            <div className="mb-6 -mt-2">
              <video src={analysisVideoUrl} controls className="w-full bg-black rounded-xl shadow-lg">
                Your browser does not support video.
              </video>
            </div>
          )}
          <p className="text-white mt-5 text-2xl">
            <strong>Form Score:</strong> {(safeProbability / 10).toFixed(1)}/10
          </p>
        </div>
      </div>

      {/* Main Content Container */}
      <div className="mt-8 flex-1 rounded-t-3xl bg-white p-6 max-w-2xl mx-auto shadow-md pb-40">
        {/* Optional: Analysis Video */}
        

        {/* Feedback */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold mb-4 mt-2">Feedback</h2>
          {analysisData.form_feedback && analysisData.form_feedback.length > 0 ? (
            <div className="space-y-3">
              {analysisData.form_feedback.map((item, index) => (
                <FeedbackItem key={index} feedback={item} />
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No feedback messages available.</p>
          )}
        </div>

        {/* Setup Section */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-4">Setup Analysis</h2>
          {setupFrameUrl ? (
            <img
              src={setupFrameUrl}
              alt="Setup Phase Frame"
              className="w-full rounded-md mb-4"
            />
          ) : (
            <p className="text-gray-500 mb-4">No setup frame available</p>
          )}
          {renderMetrics(setupMetrics)}
        </div>

        {/* Release Section */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-4">Release Analysis</h2>
          {releaseFrameUrl ? (
            <img
              src={releaseFrameUrl}
              alt="Release Phase Frame"
              className="w-full rounded-md mb-4"
            />
          ) : (
            <p className="text-gray-500 mb-4">No release frame available</p>
          )}
          {renderMetrics(releaseMetrics)}
        </div>

        {/* Follow-Through Section */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-4">Follow-Through Analysis</h2>
          {followFrameUrl ? (
            <img
              src={followFrameUrl}
              alt="Follow-Through Phase Frame"
              className="w-full rounded-md mb-4"
            />
          ) : (
            <p className="text-gray-500 mb-4">No follow-through frame available</p>
          )}
          {renderMetrics(followMetrics)}
        </div>
      </div>
    </div>
  );
}