import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Breadcrumb, Spinner, Alert } from 'react-bootstrap';
import { useParams, Link } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import districtService from '../services/districtService';
import forecastService from '../services/forecastService';
import SHAPBarChart from '../components/Charts/SHAPBarChart';
import ForecastTimeline from '../components/Charts/ForecastTimeline';
import RiskGauge from '../components/Charts/RiskGauge';
import { getRiskClassName } from '../utils/colorUtils';
import { formatNumber } from '../utils/formatUtils';

const DistrictDetails = () => {
  const { name } = useParams();
  const { districts } = useAppContext();
  
  const [districtData, setDistrictData] = useState(null);
  const [taluks, setTaluks] = useState([]);
  const [shapData, setShapData] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDistrictData();
  }, [name]);

  const fetchDistrictData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Parallel fetch all data
      const [details, taluksData, shapResponse, forecastData] = await Promise.allSettled([
        districtService.getDistrictDetails(name),
        districtService.getTaluks(name),
        districtService.predictFloodRisk({ district: name }),
        forecastService.get72HourForecast(name)
      ]);

      // Handle district details
      if (details.status === 'fulfilled') {
        setDistrictData(details.value);
      }

      // Handle taluks
      if (taluksData.status === 'fulfilled') {
        setTaluks(taluksData.value || []);
      }

      // Handle SHAP data
      if (shapResponse.status === 'fulfilled' && shapResponse.value.shap_drivers) {
        setShapData(shapResponse.value);
      }

      // Handle forecast
      if (forecastData.status === 'fulfilled') {
        setForecast(forecastData.value);
      }

    } catch (err) {
      console.error('Error fetching district data:', err);
      setError('Failed to load district information');
    } finally {
      setLoading(false);
    }
  };

  // Find current district from context
  const currentDistrict = districts.find(d => d.name === name);

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" />
          <p className="mt-3">Loading district details...</p>
        </div>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">{error}</Alert>
        <Link to="/dashboard" className="btn btn-primary">Back to Dashboard</Link>
      </Container>
    );
  }

  const riskLevel = currentDistrict?.risk || districtData?.risk || 0;
  const riskClass = getRiskClassName(riskLevel);

  return (
    <Container className="mt-4">
      {/* Breadcrumb Navigation */}
      <Breadcrumb>
        <Breadcrumb.Item linkAs={Link} linkProps={{ to: '/dashboard' }}>
          Dashboard
        </Breadcrumb.Item>
        <Breadcrumb.Item active>{name}</Breadcrumb.Item>
      </Breadcrumb>

      {/* District Header */}
      <Row className="mb-4">
        <Col>
          <h2>{name} District</h2>
          <p className="text-muted">
            Detailed flood risk analysis and predictions
          </p>
        </Col>
      </Row>

      {/* Risk Overview */}
      <Row className="mb-4">
        <Col md={4}>
          <Card>
            <Card.Header>
              <h6 className="mb-0">Current Flood Risk</h6>
            </Card.Header>
            <Card.Body className="text-center">
              <RiskGauge 
                probability={riskLevel} 
                riskClass={riskClass} 
                size="large" 
              />
              <p className="mt-3 mb-0">
                <strong>Risk Level:</strong> {riskClass}
              </p>
              {districtData && (
                <small className="text-muted">
                  Last Updated: {new Date(districtData.last_updated || Date.now()).toLocaleString()}
                </small>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col md={8}>
          {shapData && (
            <SHAPBarChart shapDrivers={shapData.shap_drivers} />
          )}
          {!shapData && (
            <Card>
              <Card.Body>
                <Alert variant="info">
                  SHAP explanation data not available. Run a prediction to see feature importance.
                </Alert>
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>

      {/* Forecast Timeline */}
      {forecast && (
        <Row className="mb-4">
          <Col>
            <ForecastTimeline forecastData={forecast} districtName={name} />
          </Col>
        </Row>
      )}

      {/* Taluk-Level Data */}
      {taluks.length > 0 && (
        <Row className="mb-4">
          <Col>
            <Card>
              <Card.Header>
                <h6 className="mb-0">Taluk-Level Risk Assessment</h6>
              </Card.Header>
              <Card.Body>
                <Table responsive hover>
                  <thead>
                    <tr>
                      <th>Taluk</th>
                      <th>Risk Level</th>
                      <th>Elevation (m)</th>
                      <th>Vulnerability Score</th>
                      <th>Population Density</th>
                    </tr>
                  </thead>
                  <tbody>
                    {taluks.map((taluk, idx) => (
                      <tr key={idx}>
                        <td><strong>{taluk.name}</strong></td>
                        <td>
                          <span className={`badge bg-${taluk.risk >= 80 ? 'danger' : taluk.risk >= 65 ? 'warning' : taluk.risk >= 40 ? 'info' : 'success'}`}>
                            {formatNumber(taluk.risk, 1)}%
                          </span>
                        </td>
                        <td>{formatNumber(taluk.elevation || 0, 0)} m</td>
                        <td>{formatNumber(taluk.vulnerability_score || 0, 2)}</td>
                        <td>{taluk.population_density ? `${formatNumber(taluk.population_density, 0)}/km²` : 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* District Statistics */}
      {districtData && (
        <Row className="mb-4">
          <Col md={6}>
            <Card>
              <Card.Header>
                <h6 className="mb-0">Weather Conditions</h6>
              </Card.Header>
              <Card.Body>
                <div className="mb-2">
                  <strong>Rainfall (24h):</strong> {formatNumber(districtData.rainfall_mm || 0, 1)} mm
                </div>
                <div className="mb-2">
                  <strong>River Level:</strong> {formatNumber(districtData.river_level_m || 0, 2)} m
                </div>
                <div className="mb-2">
                  <strong>Soil Moisture:</strong> {formatNumber((districtData.soil_moisture || 0) * 100, 1)}%
                </div>
                <div className="mb-2">
                  <strong>Humidity:</strong> {formatNumber(districtData.humidity_pct || 0, 0)}%
                </div>
              </Card.Body>
            </Card>
          </Col>

          <Col md={6}>
            <Card>
              <Card.Header>
                <h6 className="mb-0">Infrastructure Status</h6>
              </Card.Header>
              <Card.Body>
                <div className="mb-2">
                  <strong>Reservoir Level:</strong> {formatNumber(districtData.reservoir_pct || 0, 1)}%
                </div>
                <div className="mb-2">
                  <strong>Average Elevation:</strong> {formatNumber(districtData.elevation_m || 0, 0)} m
                </div>
                <div className="mb-2">
                  <strong>Drainage Capacity:</strong> {districtData.drainage_capacity || 'Normal'}
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
    </Container>
  );
};

export default DistrictDetails;
