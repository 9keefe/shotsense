import React from "react";
import { useLocation } from "react-router-dom";

export default function Analysis() {
  const location = useLocation();
  const { originalVideoUrl, metrics, make_probability, form_feedback } = location.state || {};

  if (!originalVideoUrl) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-700">
          No analysis data. Please upload a video first.
        </p>
      </div>
    );
  }

  // metrics might look like:
  // {
  //   S_avg_knee_bend: 120.5,
  //   S_max_body_lean: 45.2,
  //   R_avg_hip_angle: ...
  //   ...
  // }

  return (
    <div className="min-h-screen flex flex-col items-center pt-8 px-4">
      <h1 className="text-2xl font-bold mb-4">Analysis</h1>

      <video
        src={originalVideoUrl}
        controls
        className="w-full max-w-xl mb-4 bg-black"
      >
        Your browser does not support video.
      </video>

      {/* Prediction Probability */}

      <div className="max-w-xl bg-white p-4 rounded shadow mb-4 w-full">
        <h2 className="text-xl font-semibold mb-2">Shot Success Probability</h2>
        <p className="text-lg">
          {(make_probability * 100).toFixed(1)}% chance of making the shot
        </p>
      </div>
      

      {/* Form Feedback */}
      {form_feedback && (
        <div className="max-w-xl bg-white p-4 rounded shadow mb-4 w-full">
          <h2 className="text-xl font-semibold mb-2">Key Form Factors</h2>
          <ul className="space-y-2">
            {form_feedback.map((item, index) => (
              <li key={index} className="border-b pb-2">
                <div className="font-medium">{item.feature}</div>
                <div>Current Value: {item.value.toFixed(2)}</div>
                <div>Importance: {(item.importance * 100).toFixed(1)}%</div>
              </li>
            ))}
          </ul>
        </div>
      )}


      <div className="max-w-xl bg-white p-4 rounded shadow">
        <h2 className="text-xl font-semibold mb-2">Metrics</h2>
        <ul className="list-disc list-inside text-gray-800">
          {Object.entries(metrics).map(([key, value]) => (
            <li key={key}>
              <strong>{key}:</strong> {value}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
