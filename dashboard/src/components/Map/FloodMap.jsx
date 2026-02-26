import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import { Spinner, Alert } from 'react-bootstrap';
import L from 'leaflet';
import axios from 'axios';
import { getRiskColor } from '../../utils/colorUtils';
import MapLegend from './MapLegend';
import DistrictInfoPanel from './DistrictInfoPanel';
import config from '../../config';
import '../../utils/leafletIconFix';
import './FloodMap.css';

// Component to fit bounds when GeoJSON loads
const FitBounds = ({ geojsonData }) => {
  const map = useMap();

  useEffect(() => {
    if (geojsonData && geojsonData.features.length > 0) {
      const geoJsonLayer = L.geoJSON(geojsonData);
      const bounds = geoJsonLayer.getBounds();
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [20, 20] });
      }
    }
  }, [geojsonData, map]);

  return null;
};

const FloodMap = ({ districts }) => {
  const [geojsonData, setGeojsonData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDistrict, setSelectedDistrict] = useState(null);

  useEffect(() => {
    loadGeoJSON();
  }, []);

  const loadGeoJSON = async () => {
    try {
      setLoading(true);
      setError(null);

      // Try to load GeoJSON from public folder first
      try {
        const response = await axios.get('/tn_districts.geojson', {
          baseURL: process.env.PUBLIC_URL || ''
        });
        setGeojsonData(response.data);
      } catch (err) {
        console.log('GeoJSON not found in public folder, trying backend...');
        
        // Try backend API
        try {
          const response = await axios.get(`${config.API_BASE_URL}/geojson/districts`);
          setGeojsonData(response.data);
        } catch (backendErr) {
          console.log('GeoJSON not available from backend, using fallback markers');
          throw new Error('GeoJSON not available');
        }
      }
    } catch (err) {
      console.error('Failed to load GeoJSON:', err);
      setError('Map data not available. Using marker fallback...');
      
      // Fallback: create simple circle markers
      if (districts && districts.length > 0) {
        createFallbackMarkers();
      }
    } finally {
      setLoading(false);
    }
  };

  const createFallbackMarkers = () => {
    // Create simple GeoJSON with circle markers at district centers
    const features = districts.map(district => ({
      type: 'Feature',
      properties: {
        district_name: district.name,
        name_tamil: district.name_tamil || district.name,
        risk_probability: district.risk?.probability || 0
      },
      geometry: {
        type: 'Point',
        coordinates: [district.lon || 78.6569, district.lat || 11.1271]
      }
    }));

    setGeojsonData({
      type: 'FeatureCollection',
      features: features
    });
  };

  const getDistrictRisk = (districtName) => {
    const district = districts.find(d => d.name === districtName);
    return district ? district.risk?.probability || 0 : 0;
  };

  const getFeatureStyle = (feature) => {
    const districtName = feature.properties.district_name;
    const riskProbability = getDistrictRisk(districtName) || 
                           feature.properties.risk_probability || 
                           0;
    
    const fillColor = getRiskColor(riskProbability);

    return {
      fillColor: fillColor,
      weight: 2,
      opacity: 1,
      color: 'white',
      dashArray: '3',
      fillOpacity: 0.7
    };
  };

  const onEachFeature = (feature, layer) => {
    const districtName = feature.properties.district_name;
    const districtNameTamil = feature.properties.name_tamil || '';
    const riskProbability = getDistrictRisk(districtName) || 
                           feature.properties.risk_probability || 
                           0;

    // Tooltip on hover
    layer.bindTooltip(
      `<div class="map-tooltip">
        <strong>${districtName}</strong>
        ${districtNameTamil ? `<br/><span class="tamil-text">${districtNameTamil}</span>` : ''}
        <br/>Risk: ${riskProbability.toFixed(1)}%
      </div>`,
      {
        sticky: true,
        className: 'custom-tooltip'
      }
    );

    // Click handler
    layer.on({
      click: () => {
        setSelectedDistrict(districtName);
      },
      mouseover: (e) => {
        const layer = e.target;
        layer.setStyle({
          weight: 3,
          color: '#666',
          dashArray: '',
          fillOpacity: 0.9
        });
        layer.bringToFront();
      },
      mouseout: (e) => {
        const layer = e.target;
        layer.setStyle(getFeatureStyle(feature));
      }
    });
  };

  const pointToLayer = (feature, latlng) => {
    // For point features (fallback), create circle markers
    const riskProbability = feature.properties.risk_probability || 0;
    const fillColor = getRiskColor(riskProbability);

    return L.circleMarker(latlng, {
      radius: 8,
      fillColor: fillColor,
      color: '#fff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.8
    });
  };

  if (loading) {
    return (
      <div className="map-container d-flex align-items-center justify-content-center">
        <div className="text-center">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Loading map...</p>
        </div>
      </div>
    );
  }

  if (error && !geojsonData) {
    return (
      <div className="map-container">
        <Alert variant="warning">{error}</Alert>
      </div>
    );
  }

  return (
    <div className="map-wrapper position-relative">
      <MapContainer
        center={config.MAP_CENTER}
        zoom={config.MAP_ZOOM}
        className="map-container"
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {geojsonData && (
          <>
            <GeoJSON
              data={geojsonData}
              style={getFeatureStyle}
              onEachFeature={onEachFeature}
              pointToLayer={pointToLayer}
            />
            <FitBounds geojsonData={geojsonData} />
          </>
        )}

        <MapLegend />
      </MapContainer>

      {selectedDistrict && (
        <DistrictInfoPanel
          districtName={selectedDistrict}
          onClose={() => setSelectedDistrict(null)}
        />
      )}
    </div>
  );
};

export default FloodMap;
