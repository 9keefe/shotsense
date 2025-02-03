import React from "react";
import { BrowserRouter as Router, Routes, Route, useLocation } from "react-router-dom";
import NavBar from "./components/NavBar";
import Signin from "./pages/Signin";
import Home from "./pages/Home";
import Record from "./pages/Record";
import Analysis from "./pages/Analysis";
import Profile from "./pages/Profile";
import Welcome from "./pages/Welcome";
import Signup from "./pages/Signup";
import ForgotPassword from "./pages/ForgotPassword";
import MyVideos from "./pages/MyVideos";

function App() {
  return (
    <Router>
      <DisplayNavBar />
      
      <Routes>
        <Route path="/" element={<Welcome />} />
        <Route path="/home" element={<Home />} />
        <Route path="/record" element={<Record />} />
        <Route path="/analysis/:id" element={<Analysis />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/signin" element={<Signin />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/my-videos" element={<MyVideos/>} />
      </Routes>
    </Router>
  );
}

function DisplayNavBar() {
  const location = useLocation();

  const excludedRoutes = ["/", "/signin", "/signup", "/forgot-password"];

  // Check if the current route is in the excluded routes
  if (excludedRoutes.includes(location.pathname)) {
    return null; // Do not render NavBar
  }

  return <NavBar />;
}

export default App;
