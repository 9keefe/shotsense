import React, { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    axios.get("http://127.0.0.1:5000/api/test")
      .then((response) => setMessage(response.data.message))
      .catch((error) => console.error(error));
  }, []);

  return (
    <div className="h-screen w-screen bg-black flex justify-center items-center">

        <button className="text-white px-4 py-2 text-xl rounded font-medium focus:ring ring-black ring-opacity-10">{message}</button>
    </div>
  );
}

export default App;
