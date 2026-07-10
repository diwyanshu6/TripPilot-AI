import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import { User, Mail, Shield, BarChart2, CheckCircle } from "lucide-react";

export const Profile = () => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState({ total_trips: 0, upcoming_trips: 0, total_budget: 0, generated_pdfs: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const statsData = await api.get("/profile/stats");
        setStats(statsData);
      } catch (err) {
        console.error("Error loading profile stats", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return <div className="loader-container"><div className="loader"></div></div>;
  }

  return (
    <div className="profile-container">
      <div className="profile-card">
        <div className="profile-header-card">
          <div className="avatar-large">
            <User size={48} />
          </div>
          <h2>{user?.name}</h2>
          <span className="profile-role">Explorer Account</span>
        </div>

        <div className="profile-details-list">
          <div className="detail-item">
            <Mail size={16} />
            <div className="detail-info">
              <span className="detail-label">Email Address</span>
              <span className="detail-value">{user?.email}</span>
            </div>
          </div>

          <div className="detail-item">
            <Shield size={16} />
            <div className="detail-info">
              <span className="detail-label">Account Verification</span>
              <span className="detail-value verified">Verified <CheckCircle size={12} /></span>
            </div>
          </div>
        </div>

        <hr className="profile-divider" />

        <div className="profile-stats-section">
          <h3>Trip Summary Metrics</h3>
          <div className="stats-metric-grid">
            <div className="metric-box">
              <BarChart2 size={16} className="metric-icon" />
              <span className="metric-val">{stats.total_trips}</span>
              <span className="metric-lbl">Plans Created</span>
            </div>
            
            <div className="metric-box">
              <BarChart2 size={16} className="metric-icon" />
              <span className="metric-val">₹{stats.total_budget?.toLocaleString()}</span>
              <span className="metric-lbl">Total Budget</span>
            </div>
          </div>
        </div>

        <button onClick={logout} className="btn btn-secondary btn-block">
          Log Out
        </button>
      </div>
    </div>
  );
};
export default Profile;
