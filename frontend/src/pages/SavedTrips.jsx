import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import { Compass, Trash2, Calendar, MapPin, Search, Users, ArrowRight } from "lucide-react";

const formatDate = (value) =>
  new Date(value).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });

export const SavedTrips = () => {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  const fetchTrips = async () => {
    setError("");
    try {
      const data = await api.get("/trips");
      setTrips(data);
    } catch (err) {
      setError(err.message || "Failed to load previous trips.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrips();
  }, []);

  const handleDelete = async (tripId, e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this trip?")) return;

    try {
      await api.delete(`/trip/${tripId}`);
      setTrips(trips.filter((t) => t.id !== tripId));
    } catch (err) {
      alert("Error deleting trip: " + err.message);
    }
  };

  const filteredTrips = trips.filter(
    (t) =>
      t.destination.toLowerCase().includes(search.toLowerCase()) ||
      t.source.toLowerCase().includes(search.toLowerCase()) ||
      (t.trip_type || "").toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <div className="loader-container">
        <div className="loader"></div>
      </div>
    );
  }

  return (
    <div className="saved-trips-container">
      <header className="page-header">
        <div>
          <h2>Previous Trips</h2>
          <p>View your saved itineraries — click any trip to see the full plan</p>
        </div>
        <div className="search-bar-wrapper">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search by city or travel type..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </header>

      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
        </div>
      )}

      {filteredTrips.length === 0 ? (
        <div className="empty-state">
          <Compass className="empty-icon" size={48} />
          <h4>No trips found</h4>
          <p>
            {search
              ? "No saved trips match your search."
              : "Save a trip after generating it to see it here."}
          </p>
          {!search && (
            <Link to="/planner" className="btn btn-primary btn-sm">
              Create Trip
            </Link>
          )}
        </div>
      ) : (
        <div className="saved-trips-grid">
          {filteredTrips.map((trip) => (
            <Link key={trip.id} to={`/trip/${trip.id}`} className="trip-grid-card trip-grid-card-link">
              <div className="card-top">
                <MapPin size={18} className="card-pin" />
                <h3>
                  {trip.source} → {trip.destination}
                </h3>
              </div>
              <div className="card-middle">
                <div className="meta-item">
                  <Calendar size={14} />
                  <span>
                    {formatDate(trip.start_date)} – {formatDate(trip.end_date)}
                  </span>
                </div>
                <div className="meta-item">
                  <strong className="budget-tag">₹{trip.budget?.toLocaleString()}</strong>
                </div>
                {trip.travelers && (
                  <div className="meta-item">
                    <Users size={14} />
                    <span>
                      {trip.travelers} traveler{trip.travelers > 1 ? "s" : ""}
                    </span>
                  </div>
                )}
                {trip.trip_type && (
                  <span className="trip-type-tag">{trip.trip_type}</span>
                )}
                <p className="card-summary-snippet">
                  {trip.summary || "AI-generated travel itinerary"}
                </p>
              </div>
              <div className="card-actions">
                <span className="btn btn-secondary btn-sm">
                  View Itinerary <ArrowRight size={14} />
                </span>
                <button
                  onClick={(e) => handleDelete(trip.id, e)}
                  className="btn-delete"
                  title="Delete trip"
                  type="button"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default SavedTrips;
