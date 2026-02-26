import config from '../config';

/**
 * Get color based on risk probability
 * @param {number} probability - Risk probability (0-100)
 * @returns {string} Hex color code
 */
export const getRiskColor = (probability) => {
  if (probability >= 80) return config.RISK_COLORS.critical;
  if (probability >= 65) return config.RISK_COLORS.high;
  if (probability >= 40) return config.RISK_COLORS.medium;
  return config.RISK_COLORS.low;
};

/**
 * Get color based on risk class
 * @param {string} riskClass - 'Low', 'Medium', 'High'
 * @returns {string} Hex color code
 */
export const getRiskColorByClass = (riskClass) => {
  const classMap = {
    Low: config.RISK_COLORS.low,
    Medium: config.RISK_COLORS.medium,
    High: config.RISK_COLORS.critical
  };
  return classMap[riskClass] || config.RISK_COLORS.low;
};

/**
 * Get alert color based on level
 * @param {string} alertLevel - Alert level
 * @returns {string} Hex color code
 */
export const getAlertColor = (alertLevel) => {
  return config.ALERT_COLORS[alertLevel] || '#2196F3';
};

/**
 * Get risk class name based on probability
 * @param {number} probability - Risk probability (0-100)
 * @returns {string} Risk class name ('low', 'medium', 'high', 'critical')
 */
export const getRiskClassName = (probability) => {
  if (probability >= 80) return 'critical';
  if (probability >= 65) return 'high';
  if (probability >= 40) return 'medium';
  return 'low';
};
