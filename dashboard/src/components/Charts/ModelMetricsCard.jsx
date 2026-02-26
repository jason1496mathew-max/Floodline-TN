import React, { useState, useEffect } from 'react';
import { Card, Row, Col, ProgressBar, Spinner, Alert } from 'react-bootstrap';
import { FaCheckCircle, FaExclamationTriangle } from 'react-icons/fa';
import districtService from '../../services/districtService';
import { formatNumber } from '../../utils/formatUtils';

const ModelMetricsCard = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await districtService.getModelMetrics();
      setMetrics(data);
    } catch (err) {
      setError('Failed to load model metrics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <Card.Body className="text-center">
          <Spinner animation="border" size="sm" />
          <p className="mt-2 mb-0">Loading metrics...</p>
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

  if (!metrics) return null;

  const getScoreColor = (score) => {
    if (score >= 0.85) return 'success';
    if (score >= 0.75) return 'warning';
    return 'danger';
  };

  const getScoreIcon = (score) => {
    if (score >= 0.75) {
      return <FaCheckCircle className="text-success me-2" />;
    }
    return <FaExclamationTriangle className="text-warning me-2" />;
  };

  const f1Score = metrics.metrics.f1_score_weighted;
  const precision = metrics.metrics.precision_weighted;
  const recall = metrics.metrics.recall_weighted;
  const accuracy = metrics.metrics.accuracy;

  return (
    <Card className="model-metrics-card">
      <Card.Header>
        <h6 className="mb-0">Model Performance Metrics</h6>
        <small className="text-muted">
          Version {metrics.model_version} | Trained: {new Date(metrics.trained_on).toLocaleDateString()}
        </small>
      </Card.Header>
      <Card.Body>
        <Row className="mb-3">
          <Col md={6}>
            <div className="metric-item mb-3">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span>
                  {getScoreIcon(f1Score)}
                  <strong>F1 Score</strong>
                </span>
                <span className={`badge bg-${getScoreColor(f1Score)}`}>
                  {formatNumber(f1Score * 100, 1)}%
                </span>
              </div>
              <ProgressBar 
                now={f1Score * 100} 
                variant={getScoreColor(f1Score)}
                style={{ height: '8px' }}
              />
              <small className="text-muted">
                Overall model accuracy (target: 80%)
              </small>
            </div>

            <div className="metric-item mb-3">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span>
                  {getScoreIcon(precision)}
                  <strong>Precision</strong>
                </span>
                <span className={`badge bg-${getScoreColor(precision)}`}>
                  {formatNumber(precision * 100, 1)}%
                </span>
              </div>
              <ProgressBar 
                now={precision * 100} 
                variant={getScoreColor(precision)}
                style={{ height: '8px' }}
              />
              <small className="text-muted">
                False alarm rate minimization
              </small>
            </div>
          </Col>

          <Col md={6}>
            <div className="metric-item mb-3">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span>
                  {getScoreIcon(recall)}
                  <strong>Recall</strong>
                </span>
                <span className={`badge bg-${getScoreColor(recall)}`}>
                  {formatNumber(recall * 100, 1)}%
                </span>
              </div>
              <ProgressBar 
                now={recall * 100} 
                variant={getScoreColor(recall)}
                style={{ height: '8px' }}
              />
              <small className="text-muted">
                Actual flood detection rate
              </small>
            </div>

            <div className="metric-item mb-3">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span>
                  {getScoreIcon(accuracy)}
                  <strong>Accuracy</strong>
                </span>
                <span className={`badge bg-${getScoreColor(accuracy)}`}>
                  {formatNumber(accuracy * 100, 1)}%
                </span>
              </div>
              <ProgressBar 
                now={accuracy * 100} 
                variant={getScoreColor(accuracy)}
                style={{ height: '8px' }}
              />
              <small className="text-muted">
                Correct predictions overall
              </small>
            </div>
          </Col>
        </Row>

        {metrics.cross_validation && (
          <div className="cv-metrics mt-3 pt-3 border-top">
            <h6 className="mb-2">Cross-Validation Results</h6>
            <Row>
              <Col md={6}>
                <small className="text-muted">Mean F1 Score:</small>
                <p className="mb-0">
                  <strong>{formatNumber(metrics.cross_validation.mean_f1 * 100, 2)}%</strong>
                  <span className="text-muted small ms-2">
                    (±{formatNumber(metrics.cross_validation.std_f1 * 100, 2)}%)
                  </span>
                </p>
              </Col>
              <Col md={6}>
                <small className="text-muted">Features Used:</small>
                <p className="mb-0">
                  <strong>{metrics.features_count}</strong>
                </p>
              </Col>
            </Row>
          </div>
        )}

        <div className="model-info mt-3 pt-3 border-top">
          <p className="small text-muted mb-0">
            <strong>Model Type:</strong> Random Forest + XGBoost Ensemble (40% / 60%)
            <br />
            <strong>Training Data:</strong> 8 years of synthetic Tamil Nadu flood patterns
          </p>
        </div>
      </Card.Body>
    </Card>
  );
};

export default ModelMetricsCard;
