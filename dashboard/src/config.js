const config = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  MAP_CENTER: [11.1271, 78.6569], // Tamil Nadu center
  MAP_ZOOM: 7,
  REFRESH_INTERVAL: 300000, // 5 minutes in milliseconds
  ALERT_REFRESH_INTERVAL: 60000, // 1 minute
  APP_NAME: 'Floodline TN',
  APP_VERSION: '1.0.0',
  RISK_COLORS: {
    low: '#4CAF50',
    medium: '#FFC107',
    high: '#FF9800',
    critical: '#F44336'
  },
  ALERT_COLORS: {
    Advisory: '#2196F3',
    Watch: '#FFC107',
    Warning: '#FF9800',
    Emergency: '#F44336'
  }
};

export default config;
