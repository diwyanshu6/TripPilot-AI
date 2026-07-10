import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";
import { MapPin, Calendar, CreditCard, Users, Compass } from "lucide-react";

const TRAVEL_TYPES = [
  "Family Trip",
  "Solo Trip",
  "Honeymoon",
  "Adventure",
  "Friends Trip",
  "Business",
];

export const TripPlanner = () => {
  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [budget, setBudget] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [travelers, setTravelers] = useState("1");
  const [travelType, setTravelType] = useState("Family Trip");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [loadingStep, setLoadingStep] = useState(0);
  const navigate = useNavigate();

  const loadingSteps = [
    "Supervisor: Reviewing your trip details...",
    "Flight Agent: Searching flight options...",
    "Train Agent: Checking train routes...",
    "Hotel Agent: Finding hotel suggestions...",
    "Attraction Agent: Discovering places to visit...",
    "Budget Agent: Calculating estimated costs...",
    "Itinerary Agent: Building your day-by-day plan...",
    "Finalizing your trip...",
  ];

  useEffect(() => {
    let interval;
    if (loading) {
      setLoadingStep(0);
      interval = setInterval(() => {
        setLoadingStep((prev) => (prev < loadingSteps.length - 1 ? prev + 1 : prev));
      }, 1800);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (endDate < startDate) {
      setError("End date must be on or after the start date.");
      return;
    }

    setLoading(true);

    try {
      const response = await api.post("/plan-trip", {
        source: source.trim(),
        destination: destination.trim(),
        budget: parseFloat(budget),
        start_date: startDate,
        end_date: endDate,
        travelers: parseInt(travelers, 10),
        trip_type: travelType,
      });

      navigate("/trip/preview", { state: { trip: response } });
    } catch (err) {
      setError(err.message || "Failed to generate trip. Please try again.");
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="planner-loading-overlay">
        <div className="planner-loading-card">
          <div className="agent-radar">
            <Compass size={64} className="radar-compass animate-spin" />
            <div className="radar-circle rc-1"></div>
            <div className="radar-circle rc-2"></div>
          </div>
          <h3>Generating Your Trip</h3>
          <p className="loading-step-text">{loadingSteps[loadingStep]}</p>

          <div className="loading-progress-bar">
            <div
              className="loading-progress-fill"
              style={{ width: `${((loadingStep + 1) / loadingSteps.length) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="planner-container">
      <div className="planner-card">
        <div className="planner-header">
          <h2>Create New Trip</h2>
          <p>Fill in your trip details to generate an AI-powered itinerary</p>
        </div>

        {error && (
          <div className="alert alert-error">
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="planner-form">
          <div className="form-row">
            <div className="input-group">
              <label>Source</label>
              <div className="input-wrapper">
                <MapPin className="input-icon" size={16} />
                <input
                  type="text"
                  required
                  placeholder="e.g. Delhi"
                  value={source}
                  onChange={(e) => setSource(e.target.value)}
                />
              </div>
            </div>

            <div className="input-group">
              <label>Destination</label>
              <div className="input-wrapper">
                <MapPin className="input-icon" size={16} />
                <input
                  type="text"
                  required
                  placeholder="e.g. Goa"
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                />
              </div>
            </div>
          </div>

          <div className="form-row">
            <div className="input-group">
              <label>Budget (INR)</label>
              <div className="input-wrapper">
                <CreditCard className="input-icon" size={16} />
                <input
                  type="number"
                  required
                  min="1000"
                  placeholder="e.g. 30000"
                  value={budget}
                  onChange={(e) => setBudget(e.target.value)}
                />
              </div>
            </div>

            <div className="input-group">
              <label>Travelers</label>
              <div className="input-wrapper">
                <Users className="input-icon" size={16} />
                <input
                  type="number"
                  required
                  min="1"
                  max="20"
                  placeholder="e.g. 2"
                  value={travelers}
                  onChange={(e) => setTravelers(e.target.value)}
                />
              </div>
            </div>
          </div>

          <div className="form-row">
            <div className="input-group">
              <label>Start Date</label>
              <div className="input-wrapper">
                <Calendar className="input-icon" size={16} />
                <input
                  type="date"
                  required
                  value={startDate}
                  min={new Date().toISOString().split("T")[0]}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
            </div>

            <div className="input-group">
              <label>End Date</label>
              <div className="input-wrapper">
                <Calendar className="input-icon" size={16} />
                <input
                  type="date"
                  required
                  value={endDate}
                  min={startDate || new Date().toISOString().split("T")[0]}
                  onChange={(e) => setEndDate(e.target.value)}
                />
              </div>
            </div>
          </div>

          <div className="input-group">
            <label>Travel Type</label>
            <div className="input-wrapper">
              <Users className="input-icon" size={16} />
              <select value={travelType} onChange={(e) => setTravelType(e.target.value)}>
                {TRAVEL_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button type="submit" className="btn btn-primary btn-block btn-large">
            Generate Trip
          </button>
        </form>
      </div>
    </div>
  );
};

export default TripPlanner;
