import React, { useState, useEffect } from 'react';
import { Alert, Button, Container, Badge } from 'react-bootstrap';
import { FaTimes, FaBell, FaExclamationTriangle } from 'react-icons/fa';
import { getAlertColor } from '../../utils/colorUtils';
import { getRelativeTime } from '../../utils/dateUtils';
import './Alerts.css';

const AlertBanner = ({ alerts, onDismiss, onViewDetails }) => {
  const [visible, setVisible] = useState(true);
  const [currentAlertIndex, setCurrentAlertIndex] = useState(0);

  // Rotate through alerts if multiple
  useEffect(() => {
    if (alerts.length > 1) {
      const interval = setInterval(() => {
        setCurrentAlertIndex((prev) => (prev + 1) % alerts.length);
      }, 5000); // Rotate every 5 seconds

      return () => clearInterval(interval);
    }
  }, [alerts.length]);

  if (!visible || alerts.length === 0) {
    return null;
  }

  const currentAlert = alerts[currentAlertIndex];
  const alertColor = getAlertColor(currentAlert.alert_level);
  const isEmergency = currentAlert.alert_level === 'Emergency';

  const getAlertIcon = () => {
    if (isEmergency) {
      return <FaExclamationTriangle className="me-2 alert-icon-pulse" />;
    }
    return <FaBell className="me-2" />;
  };

  const handleDismiss = () => {
    setVisible(false);
    if (onDismiss) {
      onDismiss(currentAlert.alert_id);
    }
  };

  const handleViewDetails = () => {
    if (onViewDetails) {
      onViewDetails(currentAlert);
    }
  };

  return (
    <div 
      className={`alert-banner ${isEmergency ? 'alert-banner-emergency' : ''}`}
      style={{ 
        backgroundColor: alertColor,
        color: 'white'
      }}
    >
      <Container fluid>
        <div className="d-flex align-items-center justify-content-between py-2">
          <div className="d-flex align-items-center flex-grow-1">
            {getAlertIcon()}
            <div className="flex-grow-1">
              <div className="d-flex align-items-center mb-1">
                <Badge 
                  bg="light" 
                  text="dark" 
                  className="me-2"
                >
                  {currentAlert.alert_level.toUpperCase()}
                </Badge>
                <strong>{currentAlert.district}</strong>
                <span className="mx-2">•</span>
                <span>{currentAlert.flood_probability.toFixed(1)}% Risk</span>
                {alerts.length > 1 && (
                  <>
                    <span className="mx-2">•</span>
                    <small>Alert {currentAlertIndex + 1} of {alerts.length}</small>
                  </>
                )}
              </div>
              <div className="alert-message">
                {currentAlert.messages?.english || currentAlert.explanation_text || 'High flood risk detected'}
              </div>
              <small className="opacity-75">
                {getRelativeTime(currentAlert.timestamp)}
              </small>
            </div>
          </div>
          <div className="d-flex align-items-center ms-3">
            <Button
              variant="light"
              size="sm"
              className="me-2"
              onClick={handleViewDetails}
            >
              View Details
            </Button>
            <Button
              variant="link"
              className="text-white p-1"
              onClick={handleDismiss}
              aria-label="Dismiss alert"
            >
              <FaTimes size={20} />
            </Button>
          </div>
        </div>
      </Container>
    </div>
  );
};

export default AlertBanner;
