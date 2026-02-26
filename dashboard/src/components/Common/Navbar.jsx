import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Navbar, Nav, Container, Badge } from 'react-bootstrap';
import { FaWater, FaHome, FaChartLine, FaBell, FaProjectDiagram } from 'react-icons/fa';
import { useAppContext } from '../../context/AppContext';
import config from '../../config';

const AppNavbar = () => {
  const location = useLocation();
  const { alerts, lastUpdated } = useAppContext();

  const isActive = (path) => location.pathname === path;

  return (
    <Navbar bg="dark" variant="dark" expand="lg" sticky="top">
      <Container fluid>
        <Navbar.Brand as={Link} to="/">
          <FaWater className="me-2" />
          {config.APP_NAME}
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="navbar-nav" />
        <Navbar.Collapse id="navbar-nav">
          <Nav className="me-auto">
            <Nav.Link 
              as={Link} 
              to="/" 
              active={isActive('/')}
            >
              <FaHome className="me-1" />
              Dashboard
            </Nav.Link>
            <Nav.Link 
              as={Link} 
              to="/forecast" 
              active={isActive('/forecast')}
            >
              <FaChartLine className="me-1" />
              Forecast
            </Nav.Link>
            <Nav.Link 
              as={Link} 
              to="/propagation" 
              active={isActive('/propagation')}
            >
              <FaProjectDiagram className="me-1" />
              River Propagation
            </Nav.Link>
            <Nav.Link 
              as={Link} 
              to="/alerts" 
              active={isActive('/alerts')}
            >
              <FaBell className="me-1" />
              Alerts
              {alerts.length > 0 && (
                <Badge bg="danger" className="ms-2">
                  {alerts.length}
                </Badge>
              )}
            </Nav.Link>
          </Nav>
          <Nav>
            <Navbar.Text className="me-3">
              {lastUpdated && (
                <small className="text-muted">
                  Updated: {lastUpdated.toLocaleTimeString()}
                </small>
              )}
            </Navbar.Text>
            <Navbar.Text>
              <Badge bg="info">v{config.APP_VERSION}</Badge>
            </Navbar.Text>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default AppNavbar;
