import React, { useState } from "react";
import { ChevronDownIcon, ChevronUpIcon } from "@heroicons/react/outline";

function FeedbackItem({ feedback }) {
  const [expanded, setExpanded] = useState(false);
  const shortMessage = feedback.short || "No short message";
  const detailedMessage = feedback.detailed || "No detailed message";

  return (
    <button
      onClick={() => setExpanded(!expanded)}
      className="w-full rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-left transition hover:bg-white/[0.05]"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="mb-2 inline-flex rounded-full border border-blue-400/20 bg-blue-500/10 px-2.5 py-1 text-[11px] uppercase tracking-[0.18em] text-blue-300">
            Insight
          </div>
          <p className="text-sm font-medium text-white">{shortMessage}</p>
        </div>

        <div className="mt-1 text-zinc-400">
          {expanded ? (
            <ChevronUpIcon className="h-5 w-5" />
          ) : (
            <ChevronDownIcon className="h-5 w-5" />
          )}
        </div>
      </div>

      {expanded && (
        <p className="mt-4 border-t border-white/10 pt-4 text-sm leading-6 text-zinc-300 whitespace-pre-wrap">
          {detailedMessage}
        </p>
      )}
    </button>
  );
}

export default FeedbackItem;