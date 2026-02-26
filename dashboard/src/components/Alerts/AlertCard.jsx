import React, { useState } from 'react';
import { Card, Badge, Button, Collapse } from 'react-bootstrap';
import { 
  FaChevronDown, 
  FaChevronUp, 
  FaMapMarkerAlt, 
  FaClock,
  FaExclamationCircle 
} from 'react-icons/fa';
import { getAlertColor } from '../../utils/colorUtils';
import { formatDate, getRelativeTime } from '../../utils/dateUtils';
import { formatPercentage } from '../../utils/formatUtils';
import './Alerts.css';

const AlertCard = ({ alert, showDetails = false }) => {
  const [expanded, setExpanded] = useState(showDetails);
  
  const alertColor = getAlertColor(alert.alert_level);
  const borderStyle = { borderLeft: `4px solid ${alertColor}` };

  const getStatusBadge = () => {
    const statusColors = {
      'pending': 'warning',
      'dispatched': 'info',
      'delivered': 'success',
      'failed': 'danger'
    };
    return (
      <Badge bg={statusColors[alert.status] || 'secondary'}>
        {alert.status || 'Active'}
      </Badge>
    );
  };

  return (
    <Card className="alert-card mb-3" style={borderStyle}>
      <Card.Body>
        <div className="d-flex justify-content-between align-items-start mb-2">
          <div>
            <Badge 
              style={{ backgroundColor: alertColor, color: 'white' }}
              className="me-2"
            >
              {alert.alert_level}
            </Badge>
            {getStatusBadge()}
          </div>
          <Button
            variant="link"
            size="sm"
            className="p-0"
            onClick={() => setExpanded(!expanded)}
            aria-expanded={expanded}
          >
            {expanded ? <FaChevronUp /> : <FaChevronDown />}
          </Button>
        </div>

        <h6 className="mb-2">
          <FaMapMarkerAlt className="me-2 text-muted" />
          {alert.district}
          {alert.district_tamil && (
            <span className="text-muted ms-2 tamil-text">
              {alert.district_tamil}
            </span>
          )}
        </h6>

        <div className="alert-summary mb-2">
          <div className="d-flex align-items-center mb-1">
            <FaExclamationCircle className="me-2 text-danger" />
            <span>
              Flood Risk: <strong>{formatPercentage(alert.flood_probability)}</strong>
            </span>
          </div>
          <div className="d-flex align-items-center text-muted small">
            <FaClock className="me-2" />
            {formatDate(alert.timestamp)}
            <span className="ms-2">({getRelativeTime(alert.timestamp)})</span>
          </div>
        </div>

        <Collapse in={expanded}>
          <div className="alert-details">
            {alert.top_driver && (
              <div className="driver-info mb-3 p-2 bg-light rounded">
                <small className="text-muted d-block mb-1">Primary Cause:</small>
                <strong>{alert.top_driver.display_name || alert.top_driver}</strong>
                {alert.top_driver.contribution_pct && (
                  <span className="ms-2 text-muted">
                    ({formatPercentage(alert.top_driver.contribution_pct)} contribution)
                  </span>
                )}
              </div>
            )}

            {alert.channels && (
              <div className="channels-info mb-3">
                <small className="text-muted d-block mb-1">Alert Channels:</small>
                <div>
                  {alert.channels.map((channel, index) => (
                    <Badge key={index} bg="secondary" className="me-1">
                      {channel.toUpperCase()}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {alert.messages && (
              <div className="messages-section">
                <small className="text-muted d-block mb-2">Alert Messages:</small>
                
                {alert.messages.english && (
                  <div className="message-box mb-2 p-2 border rounded">
                    <small className="text-muted">English:</small>
                    <p className="mb-0 small">{alert.messages.english}</p>
                  </div>
                )}

                {alert.messages.tamil && (
                  <div className="message-box p-2 border rounded">
                    <small className="text-muted">Tamil:</small>
                    <p className="mb-0 small tamil-text">{alert.messages.tamil}</p>
                  </div>
                )}
              </div>
            )}

            {alert.alert_id && (
              <div className="mt-2 text-muted small">
                Alert ID: <code>{alert.alert_id}</code>
              </div>
            )}
          </div>
        </Collapse>
      </Card.Body>
    </Card>
  );
};

export default AlertCard;
