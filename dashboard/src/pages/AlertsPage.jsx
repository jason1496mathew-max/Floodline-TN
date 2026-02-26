import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Form, Alert, Badge } from 'react-bootstrap';
import { FaBell, FaExclamationTriangle, FaInfoCircle } from 'react-icons/fa';
import AlertHistory from '../components/Alerts/AlertHistory';
import { useAppContext } from '../context/AppContext';

const AlertsPage = () => {
  const { districts, generateTestAlert: generateTestAlertContext } = useAppContext();
  const [showTestAlert, setShowTestAlert] = useState(false);

  const handleGenerateTestAlert = () => {
    // Use first district as default
    if (districts.length > 0) {
      generateTestAlertContext(districts[0].name);
      setShowTestAlert(true);
      setTimeout(() => setShowTestAlert(false), 5000);
    }
  };

  const alertStats = [
    {
      title: 'Active Alerts',
      count: 3,
      icon: <FaBell />,
      color: 'primary'
    },
    {
      title: 'Emergency',
      count: 1,
      icon: <FaExclamationTriangle />,
      color: 'danger'
    },
    {
      title: 'Warnings',
      count: 2,
      icon: <FaInfoCircle />,
      color: 'warning'
    }
  ];

  return (
    <Container fluid className="mt-4">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h2 className="mb-1">Alert Management</h2>
              <p className="text-muted mb-0">
                Monitor and manage flood risk alerts across Tamil Nadu
              </p>
            </div>
            <Button
              variant="outline-primary"
              onClick={handleGenerateTestAlert}
            >
              Generate Test Alert
            </Button>
          </div>
        </Col>
      </Row>

      {showTestAlert && (
        <Alert variant="info" dismissible onClose={() => setShowTestAlert(false)}>
          <strong>Test Alert Generated:</strong> This is a demonstration of the alert system. 
          In production, alerts are generated automatically based on flood risk predictions.
        </Alert>
      )}

      <Row className="mb-4">
        {alertStats.map((stat, index) => (
          <Col md={4} key={index}>
            <Card className="text-center">
              <Card.Body>
                <div className={`text-${stat.color} mb-2`} style={{ fontSize: '2rem' }}>
                  {stat.icon}
                </div>
                <h6 className="text-muted mb-2">{stat.title}</h6>
                <h2 className={`mb-0 text-${stat.color}`}>{stat.count}</h2>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Alert Configuration</h5>
            </Card.Header>
            <Card.Body>
              <Form>
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Alert Thresholds</Form.Label>
                      <div className="border rounded p-3">
                        <div className="d-flex justify-content-between align-items-center mb-2">
                          <span>Advisory:</span>
                          <Badge bg="info">50-64%</Badge>
                        </div>
                        <div className="d-flex justify-content-between align-items-center mb-2">
                          <span>Watch:</span>
                          <Badge bg="warning">65-79%</Badge>
                        </div>
                        <div className="d-flex justify-content-between align-items-center mb-2">
                          <span>Warning:</span>
                          <Badge bg="danger">80-89%</Badge>
                        </div>
                        <div className="d-flex justify-content-between align-items-center">
                          <span>Emergency:</span>
                          <Badge bg="dark">90-100%</Badge>
                        </div>
                      </div>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Alert Channels</Form.Label>
                      <Form.Check 
                        type="checkbox" 
                        label="SMS Alerts" 
                        id="sms-alerts"
                        defaultChecked 
                        disabled
                      />
                      <Form.Check 
                        type="checkbox" 
                        label="Email Notifications" 
                        id="email-alerts"
                        defaultChecked 
                        disabled
                      />
                      <Form.Check 
                        type="checkbox" 
                        label="Push Notifications" 
                        id="push-alerts"
                        defaultChecked 
                        disabled
                      />
                      <Form.Check 
                        type="checkbox" 
                        label="Dashboard Banners" 
                        id="dashboard-alerts"
                        defaultChecked 
                        disabled
                      />
                    </Form.Group>

                    <Form.Group>
                      <Form.Label>Language Preferences</Form.Label>
                      <Form.Select disabled>
                        <option>Tamil + English (Bilingual)</option>
                        <option>Tamil Only</option>
                        <option>English Only</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>
                </Row>
                <Alert variant="info" className="mt-3 mb-0">
                  <strong>Note:</strong> Alert configuration is locked for demo purposes. 
                  In production, authorized users can customize thresholds and channels.
                </Alert>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        <Col>
          <AlertHistory />
        </Col>
      </Row>
    </Container>
  );
};

export default AlertsPage;
