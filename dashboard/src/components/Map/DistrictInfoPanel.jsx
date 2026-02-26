import React, { useState, useEffect } from 'react';
import { Card, Button, Spinner, Alert, Badge } from 'react-bootstrap';
import { FaTimes, FaExternalLinkAlt } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import districtService from '../../services/districtService';
import { getRiskColorByClass } from '../../utils/colorUtils';
import { formatPercentage } from '../../utils/formatUtils';
import './DistrictInfoPanel.css';

const DistrictInfoPanel = ({ districtName, onClose }) => {
  const [districtData, setDistrictData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (districtName) {
      fetchDistrictDetails();
    }
  }, [districtName]);

  const fetchDistrictDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await districtService.getDistrictDetails(districtName);
      setDistrictData(data);
    } catch (err) {
      setError('Failed to load district details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = () => {
    navigate(`/district/${districtName}`);
  };

  if (loading) {
    return (
      <Card className="district-info-panel">
        <Card.Body className="text-center">
          <Spinner animation="border" size="sm" />
          <p className="mt-2 mb-0">Loading...</p>
        </Card.Body>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="district-info-panel">
        <Card.Body>
          <Button
            variant="link"
            className="close-btn"
            onClick={onClose}
          >
            <FaTimes />
          </Button>
          <Alert variant="danger" className="mb-0">{error}</Alert>
        </Card.Body>
      </Card>
    );
  }

  if (!districtData) return null;

  const riskColor = getRiskColorByClass(districtData.risk.class);

  return (
    <Card className="district-info-panel">
      <Card.Body>
        <div className="d-flex justify-content-between align-items-start mb-3">
          <div>
            <h5 className="mb-1">{districtData.district}</h5>
            <p className="text-muted mb-0 small tamil-text">
              {districtData.name_tamil}
            </p>
          </div>
          <Button
            variant="link"
            className="close-btn p-0"
            onClick={onClose}
          >
            <FaTimes />
          </Button>
        </div>

        <div className="risk-indicator mb-3">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <span className="text-muted">Flood Risk</span>
            <Badge
              bg=""
              style={{
                backgroundColor: riskColor,
                color: 'white'
              }}
            >
              {districtData.risk.class}
            </Badge>
          </div>
          <div className="progress" style={{ height: '8px' }}>
            <div
              className="progress-bar"
              role="progressbar"
              style={{
                width: `${districtData.risk.probability}%`,
                backgroundColor: riskColor
              }}
              aria-valuenow={districtData.risk.probability}
              aria-valuemin="0"
              aria-valuemax="100"
            />
          </div>
          <div className="text-end mt-1">
            <small className="text-muted">
              {formatPercentage(districtData.risk.probability)}
            </small>
          </div>
        </div>

        <div className="info-section mb-3">
          <h6 className="text-muted mb-2">Details</h6>
          <div className="info-item">
            <span className="info-label">Elevation:</span>
            <span className="info-value">{districtData.elevation_m}m</span>
          </div>
          <div className="info-item">
            <span className="info-label">Population:</span>
            <span className="info-value">
              {(districtData.population / 1000000).toFixed(2)}M
            </span>
          </div>
          <div className="info-item">
            <span className="info-label">Major Rivers:</span>
            <span className="info-value">
              {districtData.major_rivers.join(', ')}
            </span>
          </div>
        </div>

        {districtData.top_drivers && districtData.top_drivers.length > 0 && (
          <div className="drivers-section mb-3">
            <h6 className="text-muted mb-2">Top Risk Drivers</h6>
            {districtData.top_drivers.slice(0, 3).map((driver, index) => (
              <div key={index} className="driver-item mb-2">
                <div className="d-flex justify-content-between mb-1">
                  <small className="text-truncate">{driver.display_name}</small>
                  <small className="fw-bold">
                    {formatPercentage(driver.contribution_pct)}
                  </small>
                </div>
                <div className="progress" style={{ height: '4px' }}>
                  <div
                    className="progress-bar bg-info"
                    style={{ width: `${driver.contribution_pct}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        <Button
          variant="primary"
          size="sm"
          className="w-100"
          onClick={handleViewDetails}
        >
          View Full Details <FaExternalLinkAlt className="ms-2" size={12} />
        </Button>
      </Card.Body>
    </Card>
  );
};

export default DistrictInfoPanel;
