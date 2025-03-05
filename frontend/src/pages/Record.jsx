import React, { useState } from "react";
import { PlusIcon } from "@heroicons/react/solid";
import { useNavigate } from "react-router-dom";

export default function Record() {
  const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [shootingArm, setShootingArm] = useState("RIGHT");
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();

  // toggle modal
  const toggleModal = () => setIsModalOpen(!isModalOpen);

  // file selection
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  // send to flask
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
        credentials: 'include' // Add this line
      });

      if (!res.ok) {
        setIsLoading(false);
        const { error } = await res.json();
        alert("Upload error: " + error);
        return;
      }

      // retrieve JSON data
      const data = await res.json();
      setIsLoading(false);

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
      console.err(err);
      alert("Upload failed, check console for details.");
    }
  };

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center">
      {/* Camera View */}
      <div className="w-full h-[50vh] bg-black mb-6 flex items-center justify-center">
        <p className="text-white">Camera View (Placeholder)</p>
      </div>

      {/* Plus Button */}
      <button
        onClick={toggleModal}
        className="w-16 h-16 bg-orange-500 text-white rounded-full shadow-lg flex items-center justify-center hover:bg-orange-600 focus:outline-none"
      >
        <PlusIcon className="w-8 h-8" />
      </button>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white w-[90%] max-w-md rounded-3xl p-8">
            <button
              onClick={toggleModal}
              className="absolute top-3 right-3 text-gray-700 hover:text-gray-300"
            >
              ✕
            </button>

            <h2 className="text-lg font-bold text-gray-800 mb-4">Upload a Video</h2>
            
            {/* Shooting Arm Toggle */}
            <div className="flex items-center mb-4">
              <label className="mr-2 text-gray-700">Shooting Arm:</label>
              <div className="space-x-4">
                <label>
                  <input
                    type="radio"
                    name="shootingArm"
                    value="RIGHT"
                    checked={shootingArm === "RIGHT"}
                    onChange={(e) => setShootingArm(e.target.value)}
                  />
                  <span className="ml-1">Right</span>
                </label>
                <label>
                  <input
                    type="radio"
                    name="shootingArm"
                    value="LEFT"
                    checked={shootingArm === "LEFT"}
                    onChange={(e) => setShootingArm(e.target.value)}
                  />
                  <span className="ml-1">Left</span>
                </label>
              </div>
            </div>
            
            {/* file input */}
            <div className="flex flex-col items-center">
              <input
                type="file"
                accept="video/*"
                className="mb-4 block w-full p-2 text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                onChange={handleFileChange}
              />
              <button
                onClick={handleUpload}
                className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 focus:outline-none"
              >
                Upload
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded shadow-lg">
            <p className="text-gray-700">Processing... Please wait</p>
          </div>
        </div>
      )}
    </div>
  );
}
