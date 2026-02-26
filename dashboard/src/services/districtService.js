import apiClient from './api';

const districtService = {
  /**
   * Get all districts with current risk levels
   */
  getAllDistricts: async () => {
    try {
      const response = await apiClient.get('/districts');
      return response;
    } catch (error) {
      console.error('Failed to fetch districts:', error);
      throw error;
    }
  },

  /**
   * Get detailed information for a specific district
   * @param {string} districtName - Name of the district
   */
  getDistrictDetails: async (districtName) => {
    try {
      const response = await apiClient.get(`/districts/${districtName}`);
      return response;
    } catch (error) {
      console.error(`Failed to fetch details for ${districtName}:`, error);
      throw error;
    }
  },

  /**
   * Get taluk-level data for a district
   * @param {string} districtName - Name of the district
   */
  getTaluks: async (districtName) => {
    try {
      const response = await apiClient.get(`/taluks/${districtName}`);
      return response;
    } catch (error) {
      console.error(`Failed to fetch taluks for ${districtName}:`, error);
      throw error;
    }
  },

  /**
   * Make a prediction for custom input
   * @param {object} predictionData - Input features
   */
  predictFloodRisk: async (predictionData) => {
    try {
      const response = await apiClient.post('/predict', predictionData);
      return response;
    } catch (error) {
      console.error('Prediction failed:', error);
      throw error;
    }
  },

  /**
   * Get model performance metrics
   */
  getModelMetrics: async () => {
    try {
      const response = await apiClient.get('/metrics');
      return response;
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      throw error;
    }
  }
};

export default districtService;
