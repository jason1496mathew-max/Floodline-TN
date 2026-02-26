import React from 'react';
import { getRiskColor } from '../../utils/colorUtils';
import { formatPercentage } from '../../utils/formatUtils';
import './Charts.css';

const RiskGauge = ({ probability, riskClass, size = 'medium' }) => {
  const sizeMap = {
    small: { width: 150, height: 150, fontSize: '1.5rem' },
    medium: { width: 200, height: 200, fontSize: '2rem' },
    large: { width: 250, height: 250, fontSize: '2.5rem' }
  };

  const dimensions = sizeMap[size];
  const radius = dimensions.width / 2 - 10;
  const circumference = 2 * Math.PI * radius;
  const progress = (probability / 100) * circumference;
  const color = getRiskColor(probability);

  return (
    <div className="risk-gauge" style={{ width: dimensions.width }}>
      <svg width={dimensions.width} height={dimensions.height}>
        {/* Background circle */}
        <circle
          cx={dimensions.width / 2}
          cy={dimensions.height / 2}
          r={radius}
          fill="none"
          stroke="#e0e0e0"
          strokeWidth="12"
        />
        {/* Progress circle */}
        <circle
          cx={dimensions.width / 2}
          cy={dimensions.height / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeDasharray={`${progress} ${circumference}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${dimensions.width / 2} ${dimensions.height / 2})`}
          style={{ transition: 'stroke-dasharray 0.5s ease' }}
        />
        {/* Center text */}
        <text
          x="50%"
          y="45%"
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize={dimensions.fontSize}
          fontWeight="bold"
          fill={color}
        >
          {formatPercentage(probability)}
        </text>
        <text
          x="50%"
          y="60%"
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="0.9rem"
          fill="#666"
        >
          {riskClass}
        </text>
      </svg>
    </div>
  );
};

export default RiskGauge;
