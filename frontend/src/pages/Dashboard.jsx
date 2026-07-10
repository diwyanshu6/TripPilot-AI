import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";
import {
  Plus,
  MapPin,
  FileText,
  User,
  ArrowRight,
  Compass,
} from "lucide-react";

const ACTION_CARDS = [
  {
    title: "Create Trip",
    description: "Plan a new journey with AI",
    to: "/planner",
    icon: Plus,
    accent: "ac-1",
  },
  {
    title: "Previous Trips",
    description: "View your saved itineraries",
    to: "/saved-trips",
    icon: MapPin,
    accent: "ac-2",
  },
  {
    title: "Downloaded PDFs",
    description: "Access exported trip plans",
    to: "#pdfs",
    icon: FileText,
    accent: "ac-3",
  },
  {
    title: "Profile",
    description: "Manage your account",
    to: "/profile",
    icon: User,
    accent: "ac-4",
  },
];

export const Dashboard = () => {
  const { user } = useAuth();
  const [trips, setTrips] = useState([]);
  const [pdfs, setPdfs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [tripsData, pdfsData] = await Promise.all([
          api.get("/trips"),
          api.get("/pdfs"),
        ]);
        setTrips(tripsData);
        setPdfs(pdfsData);
      } catch (err) {
        console.error("Error loading dashboard data", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="loader-container">
        <div className="loader"></div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h2>Welcome {user?.name}</h2>
      </header>

      <section className="dashboard-actions">
        {ACTION_CARDS.map(({ title, description, to, icon: Icon, accent }) =>
          to.startsWith("#") ? (
            <a key={title} href={to} className={`dashboard-action-card ${accent}`}>
              <div className="dashboard-action-icon">
                <Icon size={24} />
              </div>
              <div>
                <h3>{title}</h3>
                <p>{description}</p>
              </div>
            </a>
          ) : (
            <Link key={title} to={to} className={`dashboard-action-card ${accent}`}>
              <div className="dashboard-action-icon">
                <Icon size={24} />
              </div>
              <div>
                <h3>{title}</h3>
                <p>{description}</p>
              </div>
            </Link>
          )
        )}
      </section>

      <section className="dashboard-content">
        <div className="content-card">
          <div className="card-header">
            <h3>Previous Trips</h3>
            <Link to="/saved-trips" className="card-header-link">
              View All <ArrowRight size={14} />
            </Link>
          </div>

          {trips.length === 0 ? (
            <div className="empty-state">
              <Compass className="empty-icon" size={48} />
              <h4>No trips yet</h4>
              <p>Create your first AI-powered itinerary to get started.</p>
              <Link to="/planner" className="btn btn-primary btn-sm">
                Create Trip
              </Link>
            </div>
          ) : (
            <div className="trips-list">
              {trips.slice(0, 4).map((trip) => (
                <Link key={trip.id} to={`/trip/${trip.id}`} className="trip-item trip-item-link">
                  <div className="trip-item-info">
                    <h4 className="trip-item-dest">
                      {trip.source} → {trip.destination}
                    </h4>
                    <span className="trip-item-dates">
                      {new Date(trip.start_date).toLocaleDateString()} –{" "}
                      {new Date(trip.end_date).toLocaleDateString()}
                    </span>
                    {trip.summary && (
                      <span className="trip-item-summary">
                        {trip.summary.length > 80
                          ? `${trip.summary.slice(0, 80)}…`
                          : trip.summary}
                      </span>
                    )}
                  </div>
                  <div className="trip-item-budget">
                    <span>₹{trip.budget?.toLocaleString()}</span>
                  </div>
                  <div className="trip-item-actions">
                    <span className="btn btn-secondary btn-sm">View</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="dashboard-content" id="pdfs">
        <div className="content-card">
          <div className="card-header">
            <h3>Downloaded PDFs</h3>
          </div>

          {pdfs.length === 0 ? (
            <div className="empty-state">
              <FileText className="empty-icon" size={48} />
              <h4>No PDFs yet</h4>
              <p>Generate a trip plan and download it as a PDF.</p>
            </div>
          ) : (
            <div className="trips-list">
              {pdfs.slice(0, 5).map((pdf) => (
                <div key={pdf.id} className="trip-item">
                  <div className="trip-item-info">
                    <h4 className="trip-item-dest">
                      {pdf.source} → {pdf.destination}
                    </h4>
                    <span className="trip-item-dates">
                      {pdf.file_name} ·{" "}
                      {new Date(pdf.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="trip-item-actions">
                    <Link to={`/trip/${pdf.trip_id}`} className="btn btn-secondary btn-sm">
                      View Trip
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
