# Floodline TN Dashboard

React.js dashboard for the Floodline TN Flood Early Warning System.

## Setup

Install dependencies:
```bash
npm install
```

## Development

Start development server:
```bash
npm run dev
```

The app will run on http://localhost:3000

## Backend API

Ensure the FastAPI backend is running on http://localhost:8000

## Features

- Interactive flood risk map
- 72-hour forecast visualization
- District-level details with SHAP explanations
- River propagation modeling
- Multi-level alert system

## Technology Stack

- React 18.x
- Vite
- Bootstrap 5
- Leaflet.js (maps)
- Recharts (charts)
- Axios (API calls)
- React Router v6

## Project Structure

```
dashboard/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Route pages
│   ├── services/       # API service layer
│   ├── context/        # Global state management
│   ├── utils/          # Utility functions
│   ├── assets/         # Styles and images
│   ├── App.jsx         # Main app component
│   └── main.jsx        # Entry point
├── public/             # Static assets
└── package.json
```
