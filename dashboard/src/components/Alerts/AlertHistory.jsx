import React, { useState, useEffect } from 'react';
import { Card, Spinner, Alert, Button, ButtonGroup, Form, Row, Col } from 'react-bootstrap';
import { FaSync, FaFilter } from 'react-icons/fa';
import alertService from '../../services/alertService';
import AlertCard from './AlertCard';
import './Alerts.css';

const AlertHistory = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, emergency, warning, watch
  const [limit, setLimit] = useState(10);

  useEffect(() => {
    fetchAlertHistory();
  }, [limit]);

  const fetchAlertHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Note: This requires JWT authentication
      // For demo, we'll use mock data if API fails
      const data = await alertService.getAlertHistory(limit);
      setAlerts(data.alerts || []);
    } catch (err) {
      console.error('Failed to fetch alert history:', err);
      
      // Fallback to mock data for demo
      const mockAlerts = generateMockAlerts(limit);
      setAlerts(mockAlerts);
      setError('Using demo data (authentication required for live data)');
    } finally {
      setLoading(false);
    }
  };

  const generateMockAlerts = (count) => {
    const districts = ['Chennai', 'Madurai', 'Coimbatore', 'Tiruchirappalli', 'Salem'];
    const levels = ['Advisory', 'Watch', 'Warning', 'Emergency'];
    const now = new Date();

    return Array.from({ length: count }, (_, i) => {
      const hoursAgo = i * 2;
      const timestamp = new Date(now.getTime() - hoursAgo * 60 * 60 * 1000);
      const level = levels[Math.floor(Math.random() * levels.length)];
      const district = districts[Math.floor(Math.random() * districts.length)];
      const probability = 50 + Math.random() * 50;

      return {
        alert_id: `FLT-${timestamp.getTime()}-${i.toString().padStart(4, '0')}`,
        district: district,
        district_tamil: getDistrictTamil(district),
        alert_level: level,
        flood_probability: probability,
        timestamp: timestamp.toISOString(),
        status: i === 0 ? 'pending' : 'delivered',
        channels: level === 'Emergency' ? ['sms', 'email', 'push'] : ['push'],
        top_driver: {
          display_name: '7-Day Cumulative Rainfall',
          contribution_pct: 40 + Math.random() * 20
        },
        messages: {
          english: `High flood risk detected in ${district} district. Probability: ${probability.toFixed(1)}%.`,
          tamil: `${getDistrictTamil(district)} மாவட்டத்தில் வெள்ள அபாயம் அதிகமாக உள்ளது.`
        }
      };
    });
  };

  const getDistrictTamil = (district) => {
    const tamilNames = {
      'Chennai': 'சென்னை',
      'Madurai': 'மதுரை',
      'Coimbatore': 'கோயம்புத்தூர்',
      'Tiruchirappalli': 'திருச்சிராப்பள்ளி',
      'Salem': 'சேலம்'
    };
    return tamilNames[district] || district;
  };

  const filteredAlerts = alerts.filter(alert => {
    if (filter === 'all') return true;
    return alert.alert_level.toLowerCase() === filter;
  });

  const handleRefresh = () => {
    fetchAlertHistory();
  };

  const handleFilterChange = (newFilter) => {
    setFilter(newFilter);
  };

  const handleLimitChange = (e) => {
    setLimit(parseInt(e.target.value));
  };

  return (
    <Card>
      <Card.Header>
        <div className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Alert History</h5>
          <Button variant="outline-primary" size="sm" onClick={handleRefresh}>
            <FaSync className="me-2" />
            Refresh
          </Button>
        </div>
      </Card.Header>
      <Card.Body>
        {error && (
          <Alert variant="info" className="mb-3">
            {error}
          </Alert>
        )}

        <Row className="mb-3">
          <Col md={6}>
            <div className="d-flex align-items-center">
              <FaFilter className="me-2 text-muted" />
              <ButtonGroup size="sm">
                <Button
                  variant={filter === 'all' ? 'primary' : 'outline-primary'}
                  onClick={() => handleFilterChange('all')}
                >
                  All
                </Button>
                <Button
                  variant={filter === 'emergency' ? 'danger' : 'outline-danger'}
                  onClick={() => handleFilterChange('emergency')}
                >
                  Emergency
                </Button>
                <Button
                  variant={filter === 'warning' ? 'warning' : 'outline-warning'}
                  onClick={() => handleFilterChange('warning')}
                >
                  Warning
                </Button>
                <Button
                  variant={filter === 'watch' ? 'info' : 'outline-info'}
                  onClick={() => handleFilterChange('watch')}
                >
                  Watch
                </Button>
              </ButtonGroup>
            </div>
          </Col>
          <Col md={6} className="text-end">
            <Form.Select
              size="sm"
              style={{ width: 'auto', display: 'inline-block' }}
              value={limit}
              onChange={handleLimitChange}
            >
              <option value={10}>Last 10 alerts</option>
              <option value={25}>Last 25 alerts</option>
              <option value={50}>Last 50 alerts</option>
              <option value={100}>Last 100 alerts</option>
            </Form.Select>
          </Col>
        </Row>

        {loading ? (
          <div className="text-center py-4">
            <Spinner animation="border" variant="primary" />
            <p className="mt-2 text-muted">Loading alerts...</p>
          </div>
        ) : filteredAlerts.length === 0 ? (
          <Alert variant="info">
            No alerts found for the selected filter.
          </Alert>
        ) : (
          <div className="alert-list">
            {filteredAlerts.map((alert, index) => (
              <AlertCard key={index} alert={alert} />
            ))}
          </div>
        )}

        {!loading && filteredAlerts.length > 0 && (
          <div className="text-center mt-3">
            <small className="text-muted">
              Showing {filteredAlerts.length} of {alerts.length} alerts
            </small>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

export default AlertHistory;
