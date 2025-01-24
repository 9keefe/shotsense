import React from "react";

function ToggleView({ viewMode, toggleViewMode }) {
  return (
    <div className="fixed bottom-4 left-4">
      <button
        onClick={toggleViewMode}
        className="px-4 py-2 rounded text-slate-50 bg-blue-600 hover:bg-blue-700 focus:outline-none"
      >
        Switch to {viewMode === "web" ? "Mobile" : "Web"}
      </button>
    </div>
  );
}

export default ToggleViewModeButton;