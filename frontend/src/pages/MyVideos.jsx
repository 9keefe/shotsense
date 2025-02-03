 import React, { useEffect, useState } from 'react';
 import { useNavigate } from 'react-router-dom';
 import axios from 'axios';

 export default function MyVideos() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // check if user is logged in
        const userRes = await axios.get('http://127.0.0.1:5000/user', {
          withCredentials: true
        });

        // fetch analysis videos
        const analysesRes = await axios.get('http://127.0.0.1:5000/get-analyses', {
          withCredentials: true
        });

        setAnalyses(analysesRes.data);
      } catch (err) {
        if (err.response?.status === 401) {
          navigate('/signin');
        } else {
          setError('Failed to load analysis videos. Please try again later.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-700">Loading videos...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Analysis History</h1>

      {analyses.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600 mb-4">No videos found.</p>
          <button 
            onClick={() => navigate('/record')}
            className="bg-orange-500 text-white px-6 py-2 rounded-lg hover:bg-orange-600"
          >
            Upload Your First Video
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {analyses.map((analysis) => (
            <div 
              key={analysis.id} 
              className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
              onClick={() => navigate(`/analysis/${analysis.id}`)}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">
                    {new Date(analysis.created_at).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric'
                    })}
                  </h3>
                </div>
                <div className="relative w-32 h-20">
                  <video
                    src={analysis.video_url}
                    className="w-full h-full object-cover rounded-lg"
                    muted
                    onMouseOver={e => e.target.play()}
                    onMouseOut={e => {
                      e.target.pause();
                      e.target.currentTime = 0;
                    }}
                  />
                  <div className="absolute inset-0 bg-black/20 rounded-lg" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
 } 