import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Check, Sparkles } from "lucide-react";

const FEATURES = [
  "AI Itinerary",
  "Flight Search",
  "Train Search",
  "Hotel Suggestions",
  "PDF Export",
];

export const Home = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="home-page">
      <header className="hero-section">
        <div className="glow-bubble gb-1"></div>
        <div className="glow-bubble gb-2"></div>

        <div className="hero-content">
          <div className="badge animate-fade">
            <Sparkles size={14} className="badge-icon" />
            <span>AI Travel Planner</span>
          </div>
          <h1>TripPilot AI</h1>
          <p className="hero-subtext">Plan smarter with AI</p>

          <div className="hero-actions">
            <Link
              to={isAuthenticated ? "/dashboard" : "/register"}
              className="btn btn-primary btn-large"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      <section className="features-section">
        <h2>Features</h2>
        <ul className="features-list">
          {FEATURES.map((feature) => (
            <li key={feature} className="feature-item">
              <Check size={20} className="feature-check" />
              <span>{feature}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
};

export default Home;
