import { useState, useEffect } from 'react';
import { users } from '../../services/userService';
import { useToast } from '../ui/Toast';
import PasswordChangeModal from './PasswordChangeModal';
import Skeleton from './Skeleton';
import { User, FileText, ClipboardList, Shield, Activity, Key } from 'lucide-react';
import './UserProfile.css';

export default function UserProfile({ onClose }) {
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const toast = useToast();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [profileData, statsData] = await Promise.all([
        users.getProfile(),
        users.getStatistics()
      ]);
      setProfile(profileData);
      setStats(statsData);
    } catch (err) {
      toast.error(err.message || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content profile-modal" onClick={e => e.stopPropagation()}>
          <div className="modal-header">
            <h2>Profile</h2>
            <button className="modal-close" onClick={onClose}>×</button>
          </div>
          <div className="modal-body">
            {/* Loading skeleton - shows structure while loading */}
            <div className="profile-section">
              <Skeleton type="circle" />
              <div style={{ flex: 1 }}>
                <Skeleton type="text" width="60%" />
                <Skeleton type="text" width="40%" />
              </div>
            </div>
            <div className="stats-grid">
              <Skeleton type="stat" count={4} />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content profile-modal" onClick={e => e.stopPropagation()}>
          <div className="modal-header">
            <h2>Profile</h2>
            <button className="modal-close" onClick={onClose}>×</button>
          </div>

          <div className="modal-body">
            {/* User Info */}
            <div className="profile-section">
              <div className="profile-avatar">
                <User size={48} />
              </div>
              <div className="profile-info">
                <h3>{profile?.email}</h3>
                <p className="profile-joined">
                  Joined {new Date(profile?.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>

            {/* Statistics Grid */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">
                  <FileText size={24} />
                </div>
                <div className="stat-content">
                  <div className="stat-value">{stats?.total_documents || 0}</div>
                  <div className="stat-label">Documents</div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">
                  <ClipboardList size={24} />
                </div>
                <div className="stat-content">
                  <div className="stat-value">{stats?.total_assignments || 0}</div>
                  <div className="stat-label">Assignments</div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">
                  <Shield size={24} />
                </div>
                <div className="stat-content">
                  <div className="stat-value">{stats?.plagiarism_checks_run || 0}</div>
                  <div className="stat-label">Plagiarism Checks</div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">
                  <Activity size={24} />
                </div>
                <div className="stat-content">
                  <div className="stat-value">{stats?.recent_activity_count || 0}</div>
                  <div className="stat-label">Recent Activity</div>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="profile-actions">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowPasswordModal(true)}
              >
                <Key size={18} />
                Change Password
              </button>
            </div>
          </div>
        </div>
      </div>

      {showPasswordModal && (
        <PasswordChangeModal onClose={() => setShowPasswordModal(false)} />
      )}
    </>
  );
}
