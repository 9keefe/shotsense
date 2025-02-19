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
  const videoUrl = analysisData.video_url || analysisData.originalVideoUrl;
  const safeProbability = analysisData.make_probability || 0;

  if (!videoUrl) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-700">Video URL missing</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center pt-8 px-4">
      <h1 className="text-2xl font-bold mb-4">Analysis</h1>

      <video
        src={videoUrl}
        controls
        className="w-full max-w-xl mb-4 bg-black"
      >
        Your browser does not support video.
      </video>

      <div className="max-w-xl bg-white p-4 rounded shadow mb-4 w-full">
        <h2 className="text-xl font-semibold mb-2">Shot Success Probability</h2>
        <p className="text-lg">
          {(safeProbability * 100).toFixed(1)}% chance of making the shot
        </p>
      </div>

      {/* Key Form Factors (Updated Structure) */}
      {analysisData.form_feedback && analysisData.form_feedback.length > 0 && (
        <div className="max-w-xl bg-white p-4 rounded shadow mb-4 w-full">
          <h2 className="text-xl font-semibold mb-2">Key Form Insights</h2>
          <ul className="space-y-2">
            {analysisData.form_feedback.map((item, index) => (
              <li key={index} className="border-b pb-2">
                <div className="font-medium text-gray-800">{item.feature}</div>
                <div className="text-gray-600">
                  Score: {item.score?.toFixed(2)}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {analysisData.metrics && (
        <div className="max-w-xl bg-white p-4 rounded shadow w-full">
          <h2 className="text-xl font-semibold mb-2">Metrics</h2>
          <ul className="list-disc list-inside text-gray-800">
            {Object.entries(analysisData.metrics).map(([key, value]) => (
              <li key={key} className="mb-1">
                <strong>{key}:</strong> {typeof value === 'number' ? value.toFixed(2) : value}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}