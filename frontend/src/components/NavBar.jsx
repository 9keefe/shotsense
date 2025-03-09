// frontend/src/components/NavBar.jsx
import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { HomeIcon, VideoCameraIcon, BookmarkIcon } from "@heroicons/react/solid"

export default function NavBar() {
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (path) => location.pathname === path;

  const CircleButton = ({ path, children }) => (
    <button
      onClick={() => navigate(path)}
      className={`
        w-20 h-20 
        rounded-full 
        flex items-center justify-center 
        cursor-pointer
        text-sm font-medium
        ${
          isActive(path)
            ? "bg-orange-500 text-white shadow-md"
            : "bg-white text-gray-600 hover:bg-gray-100"
        }
      `}
    >
      {children}
    </button>
  );

  return (
    <div
      className="
        fixed bottom-4 left-1/2 
        transform -translate-x-1/2
        w-[90%] max-w-md
        bg-white
        border border-gray-300
        rounded-full
        px-4 py-2
        flex
        justify-around
        items-center
        mb-5
        shadow-md
        z-50
      "
    >
      <CircleButton path="/home">
        <HomeIcon className="w-14 h-14"/>
      </CircleButton>
      <CircleButton path="/record">
        <VideoCameraIcon className="w-14 h-14"/>
      </CircleButton>
      <CircleButton path="/my-videos">
        <BookmarkIcon className="w-14 h-14"/>
      </CircleButton>
    </div>
  );
}
