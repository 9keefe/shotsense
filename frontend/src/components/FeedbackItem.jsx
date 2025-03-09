import React, { useState } from "react";
import { ChevronDownIcon, ChevronUpIcon } from "@heroicons/react/solid";

function FeedbackItem({ feedback }) {
  const [expanded, setExpanded] = useState(false);
  const shortMessage = feedback.short || "No short message";
  const detailedMessage = feedback.detailed || "No detailed message";

  return (
    <div
      className="border border-gray-300 p-3 rounded-2xl text-gray-800 cursor-pointer"
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex justify-between items-center">
        <p>{shortMessage}</p>
        {expanded ? (
          <ChevronUpIcon className="w-6 h-6" />
        ) : (
          <ChevronDownIcon className="w-6 h-6" />
        )}
      </div>
      {expanded && <p className="mt-5 whitespace-pre-wrap">{detailedMessage}</p>}
    </div>
  );
}

export default FeedbackItem;
