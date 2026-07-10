import React, { useState, useEffect } from "react";
import { useParams, Link, useLocation, useNavigate } from "react-router-dom";
import { api } from "../services/api";
import {
  Calendar,
  MapPin,
  CreditCard,
  Download,
  Plane,
  Train,
  Hotel,
  AlertTriangle,
  Users,
  Save,
  CheckCircle,
} from "lucide-react";

const formatDate = (value) =>
  new Date(value).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });

const formatTime = (value) => {
  if (!value || value === "Unknown") return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
};

const getFlightDuration = (departure, arrival) => {
  const dep = new Date(departure);
  const arr = new Date(arrival);
  if (Number.isNaN(dep.getTime()) || Number.isNaN(arr.getTime())) return "—";
  const minutes = Math.max(Math.round((arr - dep) / 60000), 0);
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
};

const EmptySection = ({ message }) => (
  <p className="trip-section-empty">{message}</p>
);

const TripSection = ({ id, title, icon: Icon, children }) => (
  <section className="trip-section" id={id}>
    <div className="trip-section-header">
      {Icon && <Icon size={20} />}
      <h2>{title}</h2>
    </div>
    <div className="trip-section-body">{children}</div>
  </section>
);

export const TripDetails = () => {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const isPreview = id === "preview";
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");
  const [pdfMessage, setPdfMessage] = useState("");
  const [error, setError] = useState("");

  const isSaved = Boolean(trip?.id);

  useEffect(() => {
    const loadTrip = async () => {
      if (isPreview) {
        const previewTrip = location.state?.trip;
        if (!previewTrip) {
          setError("No trip data found. Please generate a new trip.");
        } else {
          setTrip(previewTrip);
        }
        setLoading(false);
        return;
      }

      try {
        const data = await api.get(`/trip/${id}`);
        setTrip(data);
      } catch (err) {
        setError(err.message || "Failed to load trip details.");
      } finally {
        setLoading(false);
      }
    };

    loadTrip();
  }, [id, isPreview, location.state]);

  const handleSaveTrip = async () => {
    setSaveLoading(true);
    setSaveMessage("");
    try {
      const response = await api.post("/save-trip", {
        source: trip.source,
        destination: trip.destination,
        start_date: trip.start_date,
        end_date: trip.end_date,
        budget: trip.budget,
        travelers: trip.travelers || trip.details?.travelers || 1,
        trip_type: trip.trip_type || trip.details?.trip_type || "Family Trip",
        prompt: trip.prompt || "",
        details: trip.details,
      });
      navigate(`/trip/${response.trip_id}`, { replace: true });
    } catch (err) {
      setSaveMessage(err.message || "Failed to save trip.");
    } finally {
      setSaveLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!isSaved) return;
    setPdfLoading(true);
    setPdfMessage("");
    try {
      const blob = await api.post("/generate-pdf", { trip_id: trip.id });
      const filename = `trippilot_${trip.source}_to_${trip.destination}.pdf`
        .toLowerCase()
        .replace(/\s+/g, "_")
        .replace(/[^\w.-]/g, "");
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
      setPdfMessage("PDF downloaded successfully. You can also find it under Downloaded PDFs on your dashboard.");
    } catch (err) {
      setPdfMessage(err.message || "Failed to generate PDF.");
    } finally {
      setPdfLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loader-container">
        <div className="loader"></div>
      </div>
    );
  }

  if (error || !trip) {
    return (
      <div className="error-container">
        <h3>Trip Not Found</h3>
        <p>{error || "The requested itinerary could not be retrieved."}</p>
        <Link to="/dashboard" className="btn btn-primary">
          Back to Dashboard
        </Link>
      </div>
    );
  }

  const { details } = trip;
  const flights = details.flights || [];
  const trains = details.trains || [];
  const hotels = details.hotels || [];
  const budgetAnalysis = details.budget_analysis || {};
  const itinerary = details.itinerary || [];

  return (
    <div className="trip-details-container">
      <header className="trip-header-hero">
        <div className="header-meta-row">
          <h1>
            {trip.source} → {trip.destination}
          </h1>
          <p className="trip-dates-vibe">
            {formatDate(trip.start_date)} – {formatDate(trip.end_date)}
          </p>
        </div>
        <div className="header-actions">
          {isPreview ? (
            <button
              onClick={handleSaveTrip}
              className="btn btn-primary btn-icon"
              disabled={saveLoading}
            >
              <Save size={18} />
              <span>{saveLoading ? "Saving..." : "Save Trip"}</span>
            </button>
          ) : (
            <span className="saved-badge">
              <CheckCircle size={16} />
              <span>Saved</span>
            </span>
          )}
          <button
            onClick={handleDownloadPDF}
            className="btn btn-secondary btn-icon"
            disabled={pdfLoading || !isSaved}
            title={!isSaved ? "Save the trip before downloading PDF" : ""}
          >
            <Download size={18} />
            <span>{pdfLoading ? "Generating PDF..." : "Download PDF"}</span>
          </button>
        </div>
      </header>

      {isPreview && (
        <div className="trip-unsaved-banner">
          <p>This trip is not saved yet. Click <strong>Save Trip</strong> to store it in your account.</p>
          {saveMessage && <p className="save-error">{saveMessage}</p>}
        </div>
      )}

      {pdfMessage && (
        <div className={`trip-pdf-banner ${pdfMessage.includes("successfully") ? "success" : "error"}`}>
          <p>{pdfMessage}</p>
        </div>
      )}

      <TripSection title="Trip Summary">
        <div className="trip-summary-grid">
          <div className="summary-item">
            <MapPin size={16} />
            <span>
              {trip.source} → {trip.destination}
            </span>
          </div>
          <div className="summary-item">
            <Calendar size={16} />
            <span>
              {formatDate(trip.start_date)} – {formatDate(trip.end_date)}
            </span>
          </div>
          <div className="summary-item">
            <CreditCard size={16} />
            <span>Budget: ₹{trip.budget?.toLocaleString()}</span>
          </div>
          {details.travelers && (
            <div className="summary-item">
              <Users size={16} />
              <span>
                {details.travelers} traveler{details.travelers > 1 ? "s" : ""}
              </span>
            </div>
          )}
          {!details.travelers && trip.travelers && (
            <div className="summary-item">
              <Users size={16} />
              <span>
                {trip.travelers} traveler{trip.travelers > 1 ? "s" : ""}
              </span>
            </div>
          )}
          {details.trip_type && (
            <div className="summary-item">
              <span className="summary-label">Travel type:</span>
              <span>{details.trip_type}</span>
            </div>
          )}
          {!details.trip_type && trip.trip_type && (
            <div className="summary-item">
              <span className="summary-label">Travel type:</span>
              <span>{trip.trip_type}</span>
            </div>
          )}
        </div>
        {details.summary && <p className="trip-summary-text">{details.summary}</p>}
      </TripSection>

      <TripSection title="Flights" icon={Plane}>
        {flights.length === 0 ? (
          <EmptySection message="No flights were recommended for this trip." />
        ) : (
          <div className="result-card-list">
            {flights.map((flight, i) => (
              <div key={i} className="card-transit">
                <div className="transit-header">
                  <Plane size={16} />
                  <h5>
                    {flight.airline} — {flight.flight_number}
                  </h5>
                </div>
                <div className="transit-details">
                  <p>
                    <strong>Route:</strong> {flight.departure?.iata} → {flight.arrival?.iata}
                  </p>
                  <p>
                    <strong>Departure:</strong> {flight.departure?.airport} at{" "}
                    {formatTime(flight.departure?.scheduled)}
                  </p>
                  <p>
                    <strong>Arrival:</strong> {flight.arrival?.airport} at{" "}
                    {formatTime(flight.arrival?.scheduled)}
                  </p>
                  <p>
                    <strong>Duration:</strong>{" "}
                    {flight.duration ||
                      getFlightDuration(
                        flight.departure?.scheduled,
                        flight.arrival?.scheduled
                      )}
                  </p>
                  <p>
                    <strong>Stops:</strong> {flight.stops ?? "Non-stop"}
                  </p>
                  <p>
                    <strong>Approx. price:</strong>{" "}
                    {flight.approx_price
                      ? `₹${Number(flight.approx_price).toLocaleString()}`
                      : flight.price
                        ? `₹${Number(flight.price).toLocaleString()}`
                        : "₹6,500 (estimated)"}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </TripSection>

      <TripSection title="Trains" icon={Train}>
        {trains.length === 0 ? (
          <EmptySection message="No trains were recommended for this trip." />
        ) : (
          <div className="result-card-list">
            {trains.map((train, i) => (
              <div key={i} className="card-transit">
                <div className="transit-header">
                  <Train size={16} />
                  <h5>
                    {train.train_name} ({train.train_number})
                  </h5>
                </div>
                <div className="transit-details">
                  <p>
                    <strong>Route:</strong> {train.from_station} → {train.to_station}
                  </p>
                  <p>
                    <strong>Duration:</strong> {train.duration}
                  </p>
                  <p>
                    <strong>Class:</strong> {(train.classes || []).join(", ")}
                  </p>
                  <p>
                    <strong>Timing:</strong> Dep {train.departure} | Arr {train.arrival}
                  </p>
                  <p>
                    <strong>Fare:</strong>{" "}
                    {Object.entries(train.fares || {})
                      .map(([cls, fare]) => `${cls}: ₹${fare}`)
                      .join(" · ")}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </TripSection>

      <TripSection title="Hotels" icon={Hotel}>
        {hotels.length === 0 ? (
          <EmptySection message="No hotel suggestions were generated for this trip." />
        ) : (
          <div className="result-card-list">
            {hotels.map((hotel, i) => (
              <div key={i} className="card-hotel">
                <div className="hotel-card-header">
                  <h4>{hotel.name}</h4>
                  <span className="rating-badge">{hotel.rating}</span>
                </div>
                <p className="price-tag">₹{hotel.price_per_night?.toLocaleString()} / night</p>
                <p className="hotel-desc">{hotel.description}</p>
                {hotel.link && (
                  <a
                    href={hotel.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-secondary btn-sm"
                  >
                    View Details
                  </a>
                )}
              </div>
            ))}
          </div>
        )}
      </TripSection>

      <TripSection title="Budget" icon={CreditCard}>
        <div className="budget-tab-grid">
          <div className="budget-breakdown-card">
            <div className="cost-breakdown-row">
              <span>Flights / Transport</span>
              <strong>₹{budgetAnalysis.transportation_est?.toLocaleString() ?? "—"}</strong>
            </div>
            <div className="cost-breakdown-row">
              <span>Hotels</span>
              <strong>₹{budgetAnalysis.accommodation_est?.toLocaleString() ?? "—"}</strong>
            </div>
            <div className="cost-breakdown-row">
              <span>Food</span>
              <strong>₹{budgetAnalysis.food_misc_est?.toLocaleString() ?? "—"}</strong>
            </div>
            <div className="cost-breakdown-row">
              <span>Activities</span>
              <strong>₹{budgetAnalysis.sightseeing_est?.toLocaleString() ?? "—"}</strong>
            </div>
            <hr />
            <div className="cost-breakdown-row total-row">
              <span>Total Budget</span>
              <strong
                className={
                  budgetAnalysis.status === "Exceeds Budget" ? "price-alert" : "price-ok"
                }
              >
                ₹{budgetAnalysis.total_estimated?.toLocaleString() ?? "—"}
              </strong>
            </div>
            <div className="cost-breakdown-row">
              <span>Your limit</span>
              <strong>₹{trip.budget?.toLocaleString()}</strong>
            </div>
            {budgetAnalysis.status && (
              <div className="budget-status-badge">
                Status:{" "}
                <strong
                  className={
                    budgetAnalysis.status === "Exceeds Budget"
                      ? "badge-danger"
                      : "badge-success"
                  }
                >
                  {budgetAnalysis.status}
                </strong>
              </div>
            )}
          </div>

          {budgetAnalysis.saving_tips?.length > 0 && (
            <div className="budget-recommendations-card">
              <div className="recommendations-header">
                <AlertTriangle size={18} className="warn-icon" />
                <h3>Recommendations</h3>
              </div>
              <ul className="tips-list">
                {budgetAnalysis.saving_tips.map((tip, index) => (
                  <li key={index}>{tip}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </TripSection>

      <TripSection title="Itinerary" icon={Calendar}>
        {itinerary.length === 0 ? (
          <EmptySection message="No day-by-day itinerary was generated." />
        ) : (
          <div className="itinerary-tab">
            {itinerary.map((day) => (
              <div key={day.day} className="itinerary-day-card">
                <div className="day-card-header">
                  <span className="day-number">Day {day.day}</span>
                  <h4>{day.theme}</h4>
                </div>
                <div className="day-activities">
                  {day.activities?.map((act, index) => (
                    <div key={index} className="activity-item">
                      <div className="activity-time">{act.time}</div>
                      <div className="activity-details">
                        <h5>{act.title}</h5>
                        <p>{act.description}</p>
                        <span className="activity-loc">
                          <MapPin size={12} />
                          <span>{act.location}</span>
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </TripSection>

      <section className="trip-section trip-download-section">
        {isPreview ? (
          <button
            onClick={handleSaveTrip}
            className="btn btn-primary btn-large"
            disabled={saveLoading}
          >
            <Save size={18} />
            <span>{saveLoading ? "Saving..." : "Save Trip"}</span>
          </button>
        ) : (
          <button
            onClick={handleDownloadPDF}
            className="btn btn-primary btn-large"
            disabled={pdfLoading}
          >
            <Download size={18} />
            <span>{pdfLoading ? "Generating PDF..." : "Download PDF"}</span>
          </button>
        )}
      </section>
    </div>
  );
};

export default TripDetails;
