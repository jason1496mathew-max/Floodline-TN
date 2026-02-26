/**
 * Format number to fixed decimal places
 * @param {number} num - Number to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted number
 */
export const formatNumber = (num, decimals = 2) => {
  return parseFloat(num).toFixed(decimals);
};

/**
 * Format percentage
 * @param {number} value - Value to format
 * @returns {string} Formatted percentage
 */
export const formatPercentage = (value) => {
  return `${formatNumber(value, 1)}%`;
};

/**
 * Capitalize first letter
 * @param {string} str - String to capitalize
 * @returns {string} Capitalized string
 */
export const capitalize = (str) => {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};
