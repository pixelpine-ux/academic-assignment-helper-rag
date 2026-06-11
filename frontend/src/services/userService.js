// ============================================
// User Profile API
// ============================================

export const users = {
  /**
   * Get current user profile
   */
  getProfile: async () => {
    return await apiRequest('/users/me');
  },
  
  /**
   * Get user statistics
   */
  getStatistics: async () => {
    return await apiRequest('/users/me/statistics');
  },
  
  /**
   * Change password
   */
  changePassword: async (currentPassword, newPassword) => {
    return await apiRequest('/users/me/password', {
      method: 'PUT',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });
  },
};
