import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Form, Alert } from 'react-bootstrap';
import { useAppContext } from '../context/AppContext';
import forecastService from '../services/forecastService';
import ForecastTimeline from '../components/Charts/ForecastTimeline';
import ModelMetricsCard from '../components/Charts/ModelMetricsCard';

const ForecastPage = () => {
  const { districts, loading: contexLoading } = useAppContext();
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Auto-select first district when available
  useEffect(() => {
    if (districts.length > 0 && !selectedDistrict) {
      setSelectedDistrict(districts[0].name);
    }
  }, [districts, selectedDistrict]);

  // Fetch forecast when district changes
  useEffect(() => {
    if (selectedDistrict) {
      fetchForecast(selectedDistrict);
    }
  }, [selectedDistrict]);

  const fetchForecast = async (districtName) => {
    try {
      setLoading(true);
      setError(null);
      const data = await forecastService.get72HourForecast(districtName);
      setForecastData(data);
    } catch (err) {
      console.error('Failed to fetch forecast:', err);
      setError('Unable to load forecast data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDistrictChange = (e) => {
    setSelectedDistrict(e.target.value);
  };

  return (
    <Container className="mt-4">
      <Row className="mb-4">
        <Col>
          <h2>72-Hour Flood Risk Forecast</h2>
          <p className="text-muted">
            Rolling 3-day predictions with confidence intervals for Tamil Nadu districts
          </p>
        </Col>
      </Row>

      {/* District Selector */}
      <Row className="mb-4">
        <Col md={6}>
          <Form.Group>
            <Form.Label>Select District:</Form.Label>
            <Form.Select 
              value={selectedDistrict} 
              onChange={handleDistrictChange}
              disabled={contexLoading || loading}
            >
              <option value="">Choose a district...</option>
              {districts.map((district) => (
                <option key={district.name} value={district.name}>
                  {district.name} ({(district.risk?.probability * 100 || 0).toFixed(1)}% risk)
                </option>
              ))}
            </Form.Select>
          </Form.Group>
        </Col>
      </Row>

      {error && (
        <Row className="mb-4">
          <Col>
            <Alert variant="danger">{error}</Alert>
          </Col>
        </Row>
      )}

      {/* Model Metrics */}
      <Row className="mb-4">
        <Col>
          <ModelMetricsCard />
        </Col>
      </Row>

      {/* Forecast Timeline */}
      {forecastData && selectedDistrict && (
        <Row className="mb-4">
          <Col>
            <ForecastTimeline 
              forecastData={forecastData} 
              districtName={selectedDistrict} 
            />
          </Col>
        </Row>
      )}

      {!forecastData && !loading && selectedDistrict && (
        <Row>
          <Col>
            <Alert variant="info">
              No forecast data available for {selectedDistrict}. Please select another district.
            </Alert>
          </Col>
        </Row>
      )}

      {/* Forecast Explanation */}
      <Row className="mt-4">
        <Col>
          <Alert variant="light">
            <h6>About the Forecast</h6>
            <ul className="mb-0">
              <li><strong>Base Scenario:</strong> Uses historical weather patterns and current conditions</li>
              <li><strong>Intensified Scenario:</strong> Models worst-case conditions (30% higher rainfall)</li>
              <li><strong>Confidence Interval:</strong> Shaded area shows prediction uncertainty range</li>
              <li><strong>Reference Lines:</strong> 65% (Watch), 80% (Warning) thresholds</li>
              <li><strong>Update Frequency:</strong> Forecasts refresh every 6 hours with latest data</li>
            </ul>
          </Alert>
        </Col>
      </Row>
    </Container>
  );
};

export default ForecastPage;
