import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Compass, LogOut, LayoutDashboard, User, MapPin } from "lucide-react";

export const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to={isAuthenticated ? "/dashboard" : "/"} className="logo-section">
          <Compass className="nav-logo-icon" />
          <span className="logo-text">TripPilot <span className="logo-tag">AI</span></span>
        </Link>
        
        <div className="nav-links">
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="nav-link">
                <LayoutDashboard size={18} />
                <span>Dashboard</span>
              </Link>
              <Link to="/planner" className="nav-link">
                <MapPin size={18} />
                <span>Planner</span>
              </Link>
              <Link to="/saved-trips" className="nav-link">
                <span>Saved Trips</span>
              </Link>
              <div className="user-section">
                <Link to="/profile" className="profile-link">
                  <User size={18} />
                  <span>{user?.name || "Profile"}</span>
                </Link>
                <button onClick={handleLogout} className="logout-btn" title="Logout">
                  <LogOut size={16} />
                </button>
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">Login</Link>
              <Link to="/register" className="btn btn-primary">Sign Up</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};
export default Navbar;
