import React from "react";

export default function Home() {
  return (
    <div className="bg-orange-500 min-h-screen flex flex-col">

      <div className="flex items-start justify-between p-8">
        <div>
          <h1 className="text-3xl font-bold text-white leading-none">
            Welcome,
          </h1>
          <p className="text-3xl text-white">Keefe</p>
        </div>

        <div className="w-16 h-16 bg-white rounded-full"/>
      </div>

      <div className="flex-1 bg-white rounded-t-3xl drop-shadow pt-4">
      {/* Two Cards: Quick Fixes & Quick Tips */}
        <div className="flex space-x-4 px-4 mb-4 mt-10 mx-2">
          <div className="flex-1 bg-orange-500 rounded-3xl p-8 flex flex-col hover:bg-orange-600 shadow-md">
            <h3 className="text-white font-semibold mb-10">QUICK FIXES</h3>
            {/* Could be a button or icon for navigation */}
          </div>
          <div className="flex-1 bg-orange-500 rounded-3xl p-8 flex flex-col hover:bg-orange-600 shadow-md">
            <h3 className="text-white font-semibold mb-10">QUICK TIPS</h3>
          </div>
        </div>

        {/* Analytics Section */}
        <div className="px-4 mb-4 mx-2">
          <div className="bg-orange-500 p-8 rounded-3xl hover:bg-orange-600 shadow-md">
            <h3 className="text-white font-semibold mb-10">ANALYTICS</h3>
          </div>
        </div>

        <div className="px-4 mb-4 mx-2">
          <div className="bg-orange-500 p-8 rounded-3xl hover:bg-orange-600 shadow-md">
            <h3 className="text-white font-semibold mb-10">PAST SESSIONS</h3>
          </div>
        </div>
      </div>
    </div>
  );
}
