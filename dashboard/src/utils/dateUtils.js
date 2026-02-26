import { format, formatDistanceToNow } from 'date-fns';

/**
 * Format ISO date to readable string
 * @param {string} isoDate - ISO date string
 * @returns {string} Formatted date
 */
export const formatDate = (isoDate) => {
  return format(new Date(isoDate), 'PPpp');
};

/**
 * Get relative time (e.g., "2 hours ago")
 * @param {string} isoDate - ISO date string
 * @returns {string} Relative time string
 */
export const getRelativeTime = (isoDate) => {
  return formatDistanceToNow(new Date(isoDate), { addSuffix: true });
};

/**
 * Format date for API requests
 * @param {Date} date - Date object
 * @returns {string} YYYY-MM-DD format
 */
export const formatDateForAPI = (date) => {
  return format(date, 'yyyy-MM-dd');
};
