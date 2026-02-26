import React, { createContext, useState, useContext, useEffect } from 'react';
import districtService from '../services/districtService';

const AppContext = createContext();

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
};

export const AppProvider = ({ children }) => {
  const [districts, setDistricts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDistrict, setSelectedDistrict] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Fetch all districts on mount
  useEffect(() => {
    fetchDistricts();
  }, []);

  const fetchDistricts = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await districtService.getAllDistricts();
      
      // Transform API data to match component expectations
      const transformedDistricts = (data.districts || []).map(district => ({
        ...district,
        // Flatten coordinates if nested
        lat: district.coordinates?.lat || district.lat,
        lon: district.coordinates?.lon || district.lon,
        // Ensure risk object exists
        risk: {
          probability: district.risk_probability || 0,
          class: district.risk_class || 'Low'
        }
      }));
      
      setDistricts(transformedDistricts);
      setLastUpdated(new Date());
    } catch (err) {
      setError('Failed to load district data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const selectDistrict = (districtName) => {
    setSelectedDistrict(districtName);
  };

  const addAlert = (alert) => {
    setAlerts((prevAlerts) => [alert, ...prevAlerts]);
  };

  const clearAlerts = () => {
    setAlerts([]);
  };

  const refreshData = () => {
    fetchDistricts();
  };

  const generateTestAlert = (districtName) => {
    // Find the district or use a default
    const district = districts.find(d => d.name === districtName) || districts[0];
    
    if (!district) {
      console.warn('No districts available to generate test alert');
      return;
    }

    const testAlert = {
      alert_id: `TEST-${Date.now()}`,
      district: district.name,
      district_tamil: district.name_tamil || district.name,
      alert_level: 'Warning',
      flood_probability: 85.5,
      timestamp: new Date().toISOString(),
      status: 'pending',
      channels: ['sms', 'push', 'dashboard'],
      top_driver: {
        display_name: '7-Day Cumulative Rainfall',
        contribution_pct: 42.3
      },
      messages: {
        english: `High flood risk detected in ${district.name} district. Move to higher ground immediately.`,
        tamil: `${district.name_tamil || district.name} மாவட்டத்தில் வெள்ள அபாயம் அதிகமாக உள்ளது. உயர்ந்த இடத்திற்கு செல்லவும்.`
      },
      explanation_text: 'Heavy rainfall combined with high river levels has significantly increased flood risk.'
    };
    
    addAlert(testAlert);
    
    // Auto-dismiss after 10 seconds
    setTimeout(() => {
      setAlerts(prev => prev.filter(a => a.alert_id !== testAlert.alert_id));
    }, 10000);
  };

  const value = {
    districts,
    loading,
    error,
    selectedDistrict,
    alerts,
    lastUpdated,
    selectDistrict,
    addAlert,
    clearAlerts,
    refreshData,
    generateTestAlert
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
