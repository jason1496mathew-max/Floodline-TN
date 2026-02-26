import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppProvider, useAppContext } from './context/AppContext';
import ErrorBoundary from './components/Common/ErrorBoundary';
import AppNavbar from './components/Common/Navbar';
import Footer from './components/Common/Footer';
import AlertBanner from './components/Alerts/AlertBanner';

// Pages
import Dashboard from './pages/Dashboard';
import DistrictDetails from './pages/DistrictDetails';
import ForecastPage from './pages/ForecastPage';
import PropagationPage from './pages/PropagationPage';
import AlertsPage from './pages/AlertsPage';

// Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css';
// Import Leaflet CSS
import 'leaflet/dist/leaflet.css';
// Import custom styles
import './assets/styles/App.css';

// Alert Banner Wrapper (needs to be inside AppProvider)
const AppContent = () => {
  const { alerts } = useAppContext();
  const [activeAlerts, setActiveAlerts] = useState([]);

  useEffect(() => {
    // Filter for active high-priority alerts
    const highPriorityAlerts = alerts.filter(
      alert => ['Warning', 'Emergency'].includes(alert.alert_level)
    );
    setActiveAlerts(highPriorityAlerts);
  }, [alerts]);

  const handleDismissAlert = (alertId) => {
    setActiveAlerts(activeAlerts.filter(a => a.alert_id !== alertId));
  };

  const handleViewDetails = (alert) => {
    // Navigate to alerts page or show modal
    console.log('View alert details:', alert);
  };

  return (
    <>
      {activeAlerts.length > 0 && (
        <AlertBanner
          alerts={activeAlerts}
          onDismiss={handleDismissAlert}
          onViewDetails={handleViewDetails}
        />
      )}
      <div 
        className="App d-flex flex-column min-vh-100" 
        style={{ marginTop: activeAlerts.length > 0 ? '80px' : '0' }}
      >
        <AppNavbar />
        <main className="flex-grow-1">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/district/:name" element={<DistrictDetails />} />
            <Route path="/forecast" element={<ForecastPage />} />
            <Route path="/propagation" element={<PropagationPage />} />
            <Route path="/alerts" element={<AlertsPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </>
  );
};

function App() {
  return (
    <ErrorBoundary>
      <AppProvider>
        <Router>
          <AppContent />
        </Router>
      </AppProvider>
    </ErrorBoundary>
  );
}

export default App;
