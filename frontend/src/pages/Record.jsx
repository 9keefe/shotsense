import React, { useState } from "react";
import { PlusIcon } from "@heroicons/react/solid";
import { useNavigate } from "react-router-dom";

export default function Record() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

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

    const formData = new FormData();
    formData.append("video", selectedFile);

    try {
      const res = await fetch("/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const { error } = await res.json();
        alert("Upload error: " + error);
        return;
      }

      // retrieve JSON data
      const data = await res.json();
      const { release_angle, processed_url } = data;

      navigate("/analysis", {
        state: {
          releaseAngle: release_angle,
          processed_url: processed_url
        },
      });
    } catch (err) {
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
    </div>
  );
}
