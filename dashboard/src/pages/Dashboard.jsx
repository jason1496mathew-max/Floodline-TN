import React from 'react';
import { Container, Row, Col, Card, Alert } from 'react-bootstrap';
import { FaSync } from 'react-icons/fa';
import { useAppContext } from '../context/AppContext';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import FloodMap from '../components/Map/FloodMap';
import { getRelativeTime } from '../utils/dateUtils';

const Dashboard = () => {
  const { districts, loading, error, lastUpdated, refreshData } = useAppContext();

  if (loading) {
    return <LoadingSpinner message="Loading district data..." />;
  }

  if (error) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">
          {error}
          <button 
            className="btn btn-sm btn-outline-danger ms-3"
            onClick={refreshData}
          >
            Retry
          </button>
        </Alert>
      </Container>
    );
  }

  // Calculate statistics
  const totalDistricts = districts.length;
  const highRiskCount = districts.filter(d => d.risk?.probability >= 80).length;
  const mediumRiskCount = districts.filter(d => d.risk?.probability >= 65 && d.risk?.probability < 80).length;

  return (
    <Container fluid className="mt-4">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h2 className="mb-1">Floodline TN Dashboard</h2>
              <p className="text-muted mb-0">
                Real-time flood risk monitoring for Tamil Nadu
              </p>
            </div>
            <div className="text-end">
              <button 
                className="btn btn-sm btn-outline-primary"
                onClick={refreshData}
              >
                <FaSync className="me-2" />
                Refresh
              </button>
              {lastUpdated && (
                <div className="text-muted small mt-1">
                  Updated {getRelativeTime(lastUpdated.toISOString())}
                </div>
              )}
            </div>
          </div>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col md={4}>
          <Card className="text-center">
            <Card.Body>
              <h6 className="text-muted mb-2">Total Districts</h6>
              <h2 className="mb-0">{totalDistricts}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="text-center border-danger">
            <Card.Body>
              <h6 className="text-muted mb-2">High Risk</h6>
              <h2 className="mb-0 text-danger">{highRiskCount}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="text-center border-warning">
            <Card.Body>
              <h6 className="text-muted mb-2">Medium Risk</h6>
              <h2 className="mb-0 text-warning">{mediumRiskCount}</h2>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        <Col>
          <Card>
            <Card.Header>
              <h5 className="mb-0">District Risk Heatmap</h5>
            </Card.Header>
            <Card.Body className="p-0">
              <FloodMap districts={districts} />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mt-4">
        <Col>
          <Card>
            <Card.Header>
              <h5 className="mb-0">High Risk Districts</h5>
            </Card.Header>
            <Card.Body>
              {highRiskCount === 0 ? (
                <p className="text-muted mb-0">No high-risk districts at this time</p>
              ) : (
                <div className="list-group list-group-flush">
                  {districts
                    .filter(d => d.risk?.probability >= 80)
                    .sort((a, b) => (b.risk?.probability || 0) - (a.risk?.probability || 0))
                    .map((district, index) => (
                      <div key={index} className="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                          <strong>{district.name}</strong>
                          <span className="text-muted small ms-2 tamil-text">
                            {district.name_tamil}
                          </span>
                        </div>
                        <span className="badge bg-danger">
                          {district.risk?.probability.toFixed(1)}%
                        </span>
                      </div>
                    ))}
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;
