import apiClient from './api';

const alertService = {
  /**
   * Generate a new alert (requires authentication)
   * @param {object} alertData - Alert details
   */
  generateAlert: async (alertData) => {
    try {
      const response = await apiClient.post('/alerts/generate', alertData);
      return response;
    } catch (error) {
      console.error('Alert generation failed:', error);
      throw error;
    }
  },

  /**
   * Get alert history (requires authentication)
   * @param {number} limit - Number of alerts to retrieve
   */
  getAlertHistory: async (limit = 10) => {
    try {
      const response = await apiClient.get(`/alerts/history?limit=${limit}`);
      return response;
    } catch (error) {
      console.error('Failed to fetch alert history:', error);
      throw error;
    }
  },

  /**
   * Get river propagation timeline
   * @param {string} triggerDistrict - Upstream trigger district
   * @param {number} rainfall - Optional rainfall value
   * @param {number} riverLevel - Optional river level value
   */
  getPropagationTimeline: async (triggerDistrict, rainfall = 150, riverLevel = 2.5) => {
    try {
      const response = await apiClient.get(
        `/propagation/${triggerDistrict}?rainfall_mm=${rainfall}&river_level_m=${riverLevel}`
      );
      return response;
    } catch (error) {
      console.error('Propagation fetch failed:', error);
      throw error;
    }
  }
};

export default alertService;
