import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Badge, Spinner, Table } from 'react-bootstrap';
import { FaWater, FaArrowRight, FaMapMarkerAlt, FaClock, FaUsers, FaExclamationTriangle } from 'react-icons/fa';
import { useAppContext } from '../context/AppContext';
import alertService from '../services/alertService';

const PropagationPage = () => {
  const { districts } = useAppContext();
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [rainfall, setRainfall] = useState(200);
  const [riverLevel, setRiverLevel] = useState(4.0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [propagationData, setPropagationData] = useState(null);

  useEffect(() => {
    // Set default district to first upstream district if available
    if (districts.length > 0 && !selectedDistrict) {
      setSelectedDistrict('Dharmapuri');
    }
  }, [districts]);

  const handleSimulate = async () => {
    if (!selectedDistrict) {
      setError('Please select a trigger district');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await alertService.getPropagationTimeline(
        selectedDistrict,
        rainfall,
        riverLevel
      );
      setPropagationData(data);
    } catch (err) {
      setError('Failed to simulate flood propagation. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColorClass = (riskLevel) => {
    const colorMap = {
      'Critical': 'danger',
      'High': 'warning',
      'Medium': 'info',
      'Low': 'secondary'
    };
    return colorMap[riskLevel] || 'secondary';
  };

  return (
    <Container fluid className="mt-4">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h2 className="mb-1">
                <FaWater className="me-2" />
                River Flood Propagation
              </h2>
              <p className="text-muted mb-0">
                Simulate flood cascade timeline across river networks
              </p>
            </div>
          </div>
        </Col>
      </Row>

      {/* Control Panel */}
      <Row className="mb-4">
        <Col lg={12}>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Simulation Parameters</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={4}>
                  <Form.Group className="mb-3">
                    <Form.Label>Trigger District</Form.Label>
                    <Form.Select
                      value={selectedDistrict}
                      onChange={(e) => setSelectedDistrict(e.target.value)}
                    >
                      <option value="">Select district...</option>
                      {districts
                        .sort((a, b) => a.name.localeCompare(b.name))
                        .map((district) => (
                          <option key={district.name} value={district.name}>
                            {district.name}
                          </option>
                        ))}
                    </Form.Select>
                    <Form.Text className="text-muted">
                      Upstream district where flood originates
                    </Form.Text>
                  </Form.Group>
                </Col>
                <Col md={3}>
                  <Form.Group className="mb-3">
                    <Form.Label>Rainfall (mm)</Form.Label>
                    <Form.Control
                      type="number"
                      value={rainfall}
                      onChange={(e) => setRainfall(parseFloat(e.target.value))}
                      min="0"
                      max="500"
                      step="10"
                    />
                    <Form.Text className="text-muted">
                      24-hour cumulative rainfall
                    </Form.Text>
                  </Form.Group>
                </Col>
                <Col md={3}>
                  <Form.Group className="mb-3">
                    <Form.Label>River Level (m)</Form.Label>
                    <Form.Control
                      type="number"
                      value={riverLevel}
                      onChange={(e) => setRiverLevel(parseFloat(e.target.value))}
                      min="0"
                      max="10"
                      step="0.1"
                    />
                    <Form.Text className="text-muted">
                      Current water level
                    </Form.Text>
                  </Form.Group>
                </Col>
                <Col md={2} className="d-flex align-items-end">
                  <Button
                    variant="primary"
                    className="w-100 mb-3"
                    onClick={handleSimulate}
                    disabled={loading || !selectedDistrict}
                  >
                    {loading ? (
                      <>
                        <Spinner size="sm" className="me-2" />
                        Simulating...
                      </>
                    ) : (
                      'Simulate'
                    )}
                  </Button>
                </Col>
              </Row>

              {error && (
                <Alert variant="danger" dismissible onClose={() => setError(null)}>
                  {error}
                </Alert>
              )}

              {propagationData && propagationData.trigger_conditions && (
                <Alert variant={propagationData.cascade_triggered ? 'warning' : 'info'}>
                  <strong>Trigger Status:</strong> {propagationData.trigger_conditions.triggered ? 'ACTIVATED' : 'NOT ACTIVATED'}
                  {propagationData.trigger_conditions.trigger_reasons && 
                   propagationData.trigger_conditions.trigger_reasons.length > 0 && (
                    <>
                      <br />
                      <small>{propagationData.trigger_conditions.trigger_reasons.join(', ')}</small>
                    </>
                  )}
                </Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Results */}
      {propagationData && (
        <>
          {/* Summary Cards */}
          <Row className="mb-4">
            <Col md={3}>
              <Card className="text-center h-100">
                <Card.Body>
                  <FaMapMarkerAlt className="text-primary mb-2" size={32} />
                  <h3>{propagationData.affected_districts}</h3>
                  <p className="text-muted mb-0">Affected Districts</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center h-100">
                <Card.Body>
                  <FaClock className="text-warning mb-2" size={32} />
                  <h3>{propagationData.max_propagation_hours}h</h3>
                  <p className="text-muted mb-0">Max Propagation Time</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center h-100">
                <Card.Body>
                  <FaWater className="text-info mb-2" size={32} />
                  <h3>{propagationData.rivers_involved?.length || 0}</h3>
                  <p className="text-muted mb-0">Rivers Involved</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center h-100">
                <Card.Body>
                  <FaExclamationTriangle className="text-danger mb-2" size={32} />
                  <h3>
                    {propagationData.timeline?.filter(t => t.risk_level === 'Critical').length || 0}
                  </h3>
                  <p className="text-muted mb-0">Critical Zones</p>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* Rivers Involved */}
          {propagationData.rivers_involved && propagationData.rivers_involved.length > 0 && (
            <Row className="mb-4">
              <Col>
                <Card>
                  <Card.Header>
                    <h5 className="mb-0">Rivers Involved</h5>
                  </Card.Header>
                  <Card.Body>
                    <div className="d-flex flex-wrap gap-2">
                      {propagationData.rivers_involved.map((river, index) => (
                        <Badge key={index} bg="info" className="p-2">
                          <FaWater className="me-1" />
                          {river}
                        </Badge>
                      ))}
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          )}

          {/* Cascade Timeline */}
          {propagationData.timeline && propagationData.timeline.length > 0 ? (
            <Row className="mb-4">
              <Col>
                <Card>
                  <Card.Header>
                    <h5 className="mb-0">Flood Cascade Timeline</h5>
                  </Card.Header>
                  <Card.Body>
                    <div className="timeline-container">
                      {propagationData.timeline.map((entry, index) => (
                        <div key={index} className="timeline-entry mb-4">
                          <Row className="align-items-center">
                            <Col md={1} className="text-center">
                              {index > 0 && (
                                <FaArrowRight className="text-muted mb-3" />
                              )}
                              <div className="timeline-hour">
                                <FaClock className="text-primary me-1" />
                                <strong>{entry.onset_hour}h</strong>
                              </div>
                            </Col>
                            <Col md={11}>
                              <Card className="shadow-sm">
                                <Card.Body>
                                  <Row>
                                    <Col md={6}>
                                      <h5 className="mb-2">
                                        {entry.district}
                                        <Badge
                                          bg={getRiskColorClass(entry.risk_level)}
                                          className="ms-2"
                                        >
                                          {entry.risk_level}
                                        </Badge>
                                      </h5>
                                      <p className="text-muted mb-2">
                                        <small>{entry.district_tamil}</small>
                                      </p>
                                      <div className="mb-2">
                                        <FaWater className="text-info me-2" />
                                        <strong>River:</strong> {entry.river} ({entry.river_tamil})
                                      </div>
                                      <div>
                                        <FaUsers className="text-secondary me-2" />
                                        <strong>Population:</strong> {entry.population.toLocaleString()}
                                      </div>
                                    </Col>
                                    <Col md={6}>
                                      <div className="mb-2">
                                        <strong>Distance:</strong> {entry.distance_km} km from trigger
                                      </div>
                                      <div className="mb-2">
                                        <strong>Travel Time:</strong> {entry.travel_time_hours.toFixed(1)} hours
                                      </div>
                                      <div className="mb-2">
                                        <strong>Elevation:</strong> {entry.elevation_m}m
                                      </div>
                                      {entry.vulnerable_points && entry.vulnerable_points.length > 0 && (
                                        <div className="mt-2">
                                          <Badge bg="warning" className="me-1">
                                            <FaExclamationTriangle className="me-1" />
                                            Vulnerable Points
                                          </Badge>
                                          <div className="mt-1">
                                            <small>{entry.vulnerable_points.join(', ')}</small>
                                          </div>
                                        </div>
                                      )}
                                    </Col>
                                  </Row>
                                  {entry.path && entry.path.length > 1 && (
                                    <div className="mt-3 pt-3 border-top">
                                      <small className="text-muted">
                                        <strong>Flow Path:</strong> {entry.path.join(' → ')}
                                      </small>
                                    </div>
                                  )}
                                </Card.Body>
                              </Card>
                            </Col>
                          </Row>
                        </div>
                      ))}
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          ) : (
            <Row className="mb-4">
              <Col>
                <Alert variant="success">
                  <FaExclamationTriangle className="me-2" />
                  {propagationData.summary || 'No downstream districts affected by this flood scenario.'}
                </Alert>
              </Col>
            </Row>
          )}

          {/* Evacuation Priority Table */}
          {propagationData.evacuation_priority && propagationData.evacuation_priority.length > 0 && (
            <Row className="mb-4">
              <Col>
                <Card>
                  <Card.Header>
                    <h5 className="mb-0">Evacuation Priority Order</h5>
                  </Card.Header>
                  <Card.Body>
                    <Table striped hover responsive>
                      <thead>
                        <tr>
                          <th>Priority</th>
                          <th>District</th>
                          <th>Onset Time</th>
                          <th>Risk Level</th>
                          <th>Population</th>
                          <th>Action Required</th>
                        </tr>
                      </thead>
                      <tbody>
                        {propagationData.evacuation_priority.map((entry, index) => (
                          <tr key={index}>
                            <td>
                              <Badge bg={index < 3 ? 'danger' : 'warning'}>
                                #{index + 1}
                              </Badge>
                            </td>
                            <td>
                              <strong>{entry.district}</strong>
                              <br />
                              <small className="text-muted">{entry.district_tamil}</small>
                            </td>
                            <td>
                              <FaClock className="text-primary me-1" />
                              {entry.onset_hour} hours
                            </td>
                            <td>
                              <Badge bg={getRiskColorClass(entry.risk_level)}>
                                {entry.risk_level}
                              </Badge>
                            </td>
                            <td>{entry.population.toLocaleString()}</td>
                            <td>
                              <small>
                                {entry.onset_hour <= 6 
                                  ? 'Immediate evacuation' 
                                  : entry.onset_hour <= 12 
                                  ? 'Prepare evacuation' 
                                  : 'Monitor situation'}
                              </small>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          )}
        </>
      )}

      {/* Instructions */}
      {!propagationData && !loading && (
        <Row>
          <Col>
            <Card>
              <Card.Body>
                <h5>How to Use</h5>
                <ol>
                  <li>Select an upstream <strong>trigger district</strong> where flooding originates</li>
                  <li>Set <strong>rainfall amount</strong> (mm) and <strong>river level</strong> (meters)</li>
                  <li>Click <strong>Simulate</strong> to calculate flood propagation timeline</li>
                  <li>View cascade timeline showing when floods reach downstream districts</li>
                  <li>Check evacuation priorities for emergency planning</li>
                </ol>
                <Alert variant="info" className="mt-3">
                  <strong>Note:</strong> This simulation uses river network topology and flow velocities 
                  to predict flood arrival times in downstream districts. Results help optimize evacuation 
                  timing and resource allocation.
                </Alert>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
    </Container>
  );
};

export default PropagationPage;
