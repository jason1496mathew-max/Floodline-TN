import React from 'react';
import { Card } from 'react-bootstrap';
import config from '../../config';
import './MapLegend.css';

const MapLegend = () => {
  const legendItems = [
    { label: 'Low (0-40%)', color: config.RISK_COLORS.low },
    { label: 'Medium (41-65%)', color: config.RISK_COLORS.medium },
    { label: 'High (66-85%)', color: config.RISK_COLORS.high },
    { label: 'Critical (86-100%)', color: config.RISK_COLORS.critical }
  ];

  return (
    <Card className="map-legend">
      <Card.Body>
        <h6 className="mb-3">Flood Risk Level</h6>
        {legendItems.map((item, index) => (
          <div key={index} className="legend-item mb-2">
            <span
              className="legend-color"
              style={{ backgroundColor: item.color }}
            />
            <span className="legend-label">{item.label}</span>
          </div>
        ))}
      </Card.Body>
    </Card>
  );
};

export default MapLegend;
