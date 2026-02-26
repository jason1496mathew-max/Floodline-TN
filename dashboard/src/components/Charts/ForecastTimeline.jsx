import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  Area,
  ComposedChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { Card, Form, Spinner, Alert } from 'react-bootstrap';
import forecastService from '../../services/forecastService';
import { formatPercentage } from '../../utils/formatUtils';
import './Charts.css';

const ForecastTimeline = ({ districtName }) => {
  const [forecastData, setForecastData] = useState(null);
  const [scenario, setScenario] = useState('normal');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (districtName) {
      fetchForecast();
    }
  }, [districtName, scenario]);

  const fetchForecast = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await forecastService.get72HourForecast(districtName, scenario);
      setForecastData(data);
    } catch (err) {
      setError('Failed to load forecast data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleScenarioChange = (e) => {
    setScenario(e.target.value);
  };

  if (loading) {
    return (
      <Card>
        <Card.Body className="text-center">
          <Spinner animation="border" size="sm" />
          <p className="mt-2 mb-0">Loading forecast...</p>
        </Card.Body>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <Card.Body>
          <Alert variant="warning">{error}</Alert>
        </Card.Body>
      </Card>
    );
  }

  if (!forecastData || !forecastData.forecast) {
    return null;
  }

  // Format data for chart
  const chartData = forecastData.forecast.map(point => ({
    hour: point.hour,
    hourLabel: `${point.hour}h`,
    risk: point.risk_probability,
    lower: point.confidence_interval.lower,
    upper: point.confidence_interval.upper,
    level: point.risk_level
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="custom-chart-tooltip">
          <p className="mb-1">
            <strong>Hour {data.hour}</strong>
          </p>
          <p className="mb-1">
            Risk: <strong>{formatPercentage(data.risk)}</strong>
          </p>
          <p className="mb-1 small">
            Confidence: {formatPercentage(data.lower)} - {formatPercentage(data.upper)}
          </p>
          <p className="mb-0 small">
            <span className={`badge bg-${getLevelColor(data.level)}`}>
              {data.level}
            </span>
          </p>
        </div>
      );
    }
    return null;
  };

  const getLevelColor = (level) => {
    const colorMap = {
      'Low': 'success',
      'Medium': 'warning',
      'High': 'danger'
    };
    return colorMap[level] || 'secondary';
  };

  return (
    <Card className="forecast-chart-card">
      <Card.Header>
        <div className="d-flex justify-content-between align-items-center">
          <div>
            <h6 className="mb-0">72-Hour Flood Risk Forecast</h6>
            <small className="text-muted">{districtName}</small>
          </div>
          <Form.Select
            size="sm"
            style={{ width: 'auto' }}
            value={scenario}
            onChange={handleScenarioChange}
          >
            <option value="normal">Normal Scenario</option>
            <option value="intensified">Intensified (+15%)</option>
          </Form.Select>
        </div>
      </Card.Header>
      <Card.Body>
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart
            data={chartData}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="hourLabel"
              label={{ value: 'Hours from Now', position: 'insideBottom', offset: -5 }}
            />
            <YAxis
              label={{ value: 'Flood Risk (%)', angle: -90, position: 'insideLeft' }}
              domain={[0, 100]}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />

            {/* Confidence interval area */}
            <Area
              type="monotone"
              dataKey="upper"
              stroke="none"
              fill="#2196F3"
              fillOpacity={0.1}
              name="Confidence Upper"
            />
            <Area
              type="monotone"
              dataKey="lower"
              stroke="none"
              fill="#2196F3"
              fillOpacity={0.1}
              name="Confidence Lower"
            />

            {/* Main risk line */}
            <Line
              type="monotone"
              dataKey="risk"
              stroke="#2196F3"
              strokeWidth={3}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              name="Risk Probability"
            />

            {/* Threshold lines */}
            <ReferenceLine y={80} stroke="#F44336" strokeDasharray="3 3" label="High Risk" />
            <ReferenceLine y={65} stroke="#FF9800" strokeDasharray="3 3" label="Medium Risk" />
          </ComposedChart>
        </ResponsiveContainer>

        <div className="forecast-summary mt-3">
          <div className="row">
            <div className="col-md-4">
              <div className="summary-card">
                <small className="text-muted">Peak Risk Hour</small>
                <h5 className="mb-0">Hour {forecastData.peak_risk.hour}</h5>
              </div>
            </div>
            <div className="col-md-4">
              <div className="summary-card">
                <small className="text-muted">Peak Probability</small>
                <h5 className="mb-0">{formatPercentage(forecastData.peak_risk.probability)}</h5>
              </div>
            </div>
            <div className="col-md-4">
              <div className="summary-card">
                <small className="text-muted">Scenario</small>
                <h5 className="mb-0 text-capitalize">{scenario}</h5>
              </div>
            </div>
          </div>
        </div>
      </Card.Body>
    </Card>
  );
};

export default ForecastTimeline;
