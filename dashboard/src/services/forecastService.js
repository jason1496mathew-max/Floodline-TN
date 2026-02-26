import apiClient from './api';

const forecastService = {
  /**
   * Get 72-hour forecast for a district
   * @param {string} districtName - Name of the district
   * @param {string} scenario - 'normal' or 'intensified'
   */
  get72HourForecast: async (districtName, scenario = 'normal') => {
    try {
      const response = await apiClient.get(
        `/forecast/72h/${districtName}?scenario=${scenario}`
      );
      return response;
    } catch (error) {
      console.error(`Forecast failed for ${districtName}:`, error);
      throw error;
    }
  }
};

export default forecastService;
