import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";


export default function Home() {
  const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;
  const [name, setName] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get(`${BACKEND_BASE_URL}/user`, {
          withCredentials: true,
        });
        setName(response.data.name);
      } catch (error) {
        console.error("Failed to fetch profile:", error.response?.data?.error || error.message);
        navigate("/signin");
      }
    };

    fetchProfile();
  }, [navigate]);


  return (
    <div className="bg-orange-500 min-h-screen flex flex-col">

      <div className="flex items-start justify-between p-8">
        <div>
          <h1 className="text-3xl font-bold text-white leading-none">
            Welcome,
          </h1>
          <p className="text-3xl text-white">{name}</p>
        </div>

        <div className="w-16 h-16 bg-white rounded-full"/>
      </div>

      <div className="flex-1 bg-white rounded-t-3xl drop-shadow pt-4">
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
          <div 
            className="bg-orange-500 p-8 rounded-3xl hover:bg-orange-600 shadow-md cursor-pointer"
            onClick={() => navigate('/my-videos')}
          >
            <h3 className="text-white font-semibold mb-10">PAST SESSIONS</h3>
          </div>
        </div>
      </div>
    </div>
  );
}
