import { useState } from 'react';
import { users } from '../../services/userService';
import { useToast } from '../ui/Toast';
import { Lock } from 'lucide-react';
import Button from './Button';
import './PasswordChangeModal.css';

export default function PasswordChangeModal({ onClose }) {
  const [formData, setFormData] = useState({
    currentPassword: '',
    newPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const validatePassword = (password) => {
    if (password.length < 8) {
      return 'Password must be at least 8 characters';
    }
    if (!/\d/.test(password)) {
      return 'Password must contain at least one digit';
    }
    if (!/[a-zA-Z]/.test(password)) {
      return 'Password must contain at least one letter';
    }
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate
    const newErrors = {};
    if (!formData.currentPassword) {
      newErrors.currentPassword = 'Current password is required';
    }
    if (!formData.newPassword) {
      newErrors.newPassword = 'New password is required';
    } else {
      const validationError = validatePassword(formData.newPassword);
      if (validationError) {
        newErrors.newPassword = validationError;
      }
    }
    if (formData.currentPassword && formData.newPassword && 
        formData.currentPassword === formData.newPassword) {
      newErrors.newPassword = 'New password must be different';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setLoading(true);
    try {
      await users.changePassword(formData.currentPassword, formData.newPassword);
      toast.success('Password changed successfully');
      onClose();
    } catch (err) {
      if (err.status === 401) {
        setErrors({ currentPassword: 'Current password is incorrect' });
      } else if (err.status === 400) {
        setErrors({ newPassword: err.message });
      } else {
        toast.error(err.message || 'Failed to change password');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content password-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Change Password</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Current Password</label>
              <div className="input-wrapper">
                <Lock size={18} />
                <input
                  type="password"
                  value={formData.currentPassword}
                  onChange={(e) => {
                    setFormData({ ...formData, currentPassword: e.target.value });
                    setErrors({ ...errors, currentPassword: null });
                  }}
                  placeholder="Enter current password"
                  disabled={loading}
                />
              </div>
              {errors.currentPassword && (
                <div className="error-message">{errors.currentPassword}</div>
              )}
            </div>

            <div className="form-group">
              <label>New Password</label>
              <div className="input-wrapper">
                <Lock size={18} />
                <input
                  type="password"
                  value={formData.newPassword}
                  onChange={(e) => {
                    setFormData({ ...formData, newPassword: e.target.value });
                    setErrors({ ...errors, newPassword: null });
                  }}
                  placeholder="Enter new password"
                  disabled={loading}
                />
              </div>
              {errors.newPassword && (
                <div className="error-message">{errors.newPassword}</div>
              )}
              <div className="password-requirements">
                <small>• At least 8 characters</small>
                <small>• Contains at least one digit</small>
                <small>• Contains at least one letter</small>
              </div>
            </div>

            <div className="modal-footer">
              <Button 
                type="button" 
                variant="secondary" 
                onClick={onClose}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button 
                type="submit" 
                variant="primary"
                loading={loading}
              >
                Change Password
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
