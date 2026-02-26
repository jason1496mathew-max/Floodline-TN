import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Card } from 'react-bootstrap';
import { formatPercentage } from '../../utils/formatUtils';
import './Charts.css';

const SHAPBarChart = ({ drivers, title = "Risk Drivers" }) => {
  if (!drivers || drivers.length === 0) {
    return (
      <Card>
        <Card.Body>
          <p className="text-muted mb-0">No driver data available</p>
        </Card.Body>
      </Card>
    );
  }

  // Format data for Recharts
  const chartData = drivers.map(driver => ({
    name: driver.display_name,
    contribution: driver.contribution_pct,
    impact: driver.impact || 'increases risk'
  }));

  // Color based on contribution
  const getBarColor = (contribution) => {
    if (contribution > 40) return '#F44336';
    if (contribution > 30) return '#FF9800';
    if (contribution > 20) return '#FFC107';
    return '#2196F3';
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="custom-chart-tooltip">
          <p className="label mb-1">
            <strong>{data.name}</strong>
          </p>
          <p className="contribution mb-1">
            Contribution: <strong>{formatPercentage(data.contribution)}</strong>
          </p>
          <p className="impact mb-0 small text-muted">
            {data.impact}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="shap-chart-card">
      <Card.Header>
        <h6 className="mb-0">{title}</h6>
        <small className="text-muted">
          Explainable AI - Feature Importance
        </small>
      </Card.Header>
      <Card.Body>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              type="number" 
              domain={[0, 100]}
              label={{ value: 'Contribution (%)', position: 'insideBottom', offset: -5 }}
            />
            <YAxis 
              type="category" 
              dataKey="name" 
              width={150}
              tick={{ fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="contribution" radius={[0, 4, 4, 0]}>
              {chartData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={getBarColor(entry.contribution)} 
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        <div className="shap-explanation mt-3">
          <p className="small text-muted mb-2">
            <strong>Interpretation:</strong> The chart shows which factors contribute 
            most to the flood risk prediction. Higher percentages indicate stronger influence.
          </p>
        </div>
      </Card.Body>
    </Card>
  );
};

export default SHAPBarChart;
