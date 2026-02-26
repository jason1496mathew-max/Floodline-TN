import React from 'react';
import { Container } from 'react-bootstrap';
import config from '../../config';

const Footer = () => {
  return (
    <footer className="bg-dark text-white py-3 mt-5">
      <Container>
        <div className="text-center">
          <p className="mb-1">
            © 2026 {config.APP_NAME} - AI-Based Flood Early Warning System
          </p>
          <p className="mb-0 small text-muted">
            Developed for Hack Fusion 1.0 | Tamil Nadu Disaster Management
          </p>
        </div>
      </Container>
    </footer>
  );
};

export default Footer;
