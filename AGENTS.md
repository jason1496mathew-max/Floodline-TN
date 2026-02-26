# 🤖 Floodline TN - AI Agent Architecture

> **Multi-Agent System for 24-Hour Hackathon Build**
> **Project:** Floodline TN - AI-Based Flood Early Warning & Risk Prediction System
> **Parallel Development Strategy | Mock-First Approach | Production-Ready Stubs**

---

## 🎯 Agent Orchestration Strategy

This document defines **4 primary agents** and **8 specialized sub-agents** that work in parallel to deliver all 9 features within 24 hours. Each agent has clear inputs, outputs, and handoff protocols.

**Key Principles:**
- **Mock-first development**: All agents use synthetic data by default, with production API stubs ready
- **Parallel execution**: Agents 1-4 run simultaneously, sub-agents activate on-demand
- **Zero-coupling architecture**: Each agent produces standalone outputs that integrate via well-defined contracts
- **Fail-safe design**: If any API/dependency fails, mock fallback activates automatically
- **Sub-agent autonomy**: Primary agents can spawn sub-agents proactively when detecting complexity

---

## 🏗️ Primary Agents (4)

### **AGENT 1: Data Pipeline Engineer**
**Responsibility:** Build the data ingestion, processing, and feature engineering pipeline

**Sub-Agents (Proactive Activation):**
- **1A: Mock Data Generator** - Auto-spawns if no real API keys detected
- **1B: API Wrapper** - Auto-spawns when mock data ready, builds production stubs
- **1C: Data Quality Validator** - Auto-spawns after data generation to check schema integrity

**Deliverables:**
- `data/mock/tn_flood_data.csv` (38 districts × 8 years × daily records)
- `data/geospatial/tn_districts.geojson`
- `data/geospatial/tn_taluks.geojson`
- `data/demographic/vulnerability_index.csv`
- `pipeline/preprocess.py` (pandas + RobustScaler + imputation)
- `pipeline/api_wrapper.py` (with mock/live toggle)

**Time Budget:** 4 hours

**Proactive Sub-Agent Logic:**
```python
if not os.getenv("OPENWEATHER_API_KEY"):
    spawn_subagent("1A: Mock Data Generator")
if file_exists("data/mock/tn_flood_data.csv"):
    spawn_subagent("1B: API Wrapper")
if csv_generated and not validated:
    spawn_subagent("1C: Data Quality Validator")
```

---

### **AGENT 2: ML Model Architect**
**Responsibility:** Train, validate, and export the flood prediction models

**Sub-Agents (Proactive Activation):**
- **2A: Model Trainer** - Auto-spawns when training data available
- **2B: XAI Engineer** - Auto-spawns after model accuracy > 70%
- **2C: Hyperparameter Tuner** - Auto-spawns if initial F1 < 0.75

**Deliverables:**
- `models/flood_classifier.pkl` (trained ensemble model)
- `models/shap_explainer.pkl` (SHAP TreeExplainer)
- `models/metrics.json` (precision, recall, F1, confusion matrix)
- `models/train.py` (full training pipeline)
- `models/predict.py` (inference API)
- `models/shap_explain.py` (SHAP chart generator)

**Time Budget:** 4 hours (parallel with Agent 1)

**Proactive Sub-Agent Logic:**
```python
if training_data_available:
    spawn_subagent("2A: Model Trainer")
if model_trained and metrics["f1_score"] >= 0.70:
    spawn_subagent("2B: XAI Engineer")
if metrics["f1_score"] < 0.75:
    spawn_subagent("2C: Hyperparameter Tuner")
```

---

### **AGENT 3: Frontend & Visualization Engineer**
**Responsibility:** Build the React dashboard with interactive maps and charts

**Sub-Agents (Proactive Activation):**
- **3A: Map Renderer** - Auto-spawns when GeoJSON files ready
- **3B: Chart Builder** - Auto-spawns when API contract defined
- **3C: Responsive Design Fixer** - Auto-spawns after initial UI built

**Deliverables:**
- `dashboard/src/components/FloodMap.jsx` (district polygons + color coding)
- `dashboard/src/components/TalukInset.jsx` (micro-zone drill-down)
- `dashboard/src/components/XAIPanel.jsx` (SHAP bar charts)
- `dashboard/src/components/ForecastTimeline.jsx` (72-hour rolling chart)
- `dashboard/src/components/AlertBanner.jsx` (emergency overlay)
- `dashboard/src/App.js` (main layout + routing)

**Time Budget:** 6 hours (parallel with Agent 4)

**Proactive Sub-Agent Logic:**
```python
if geojson_files_exist:
    spawn_subagent("3A: Map Renderer")
if api_contract_published:
    spawn_subagent("3B: Chart Builder")
if components_built and not mobile_tested:
    spawn_subagent("3C: Responsive Design Fixer")
```

---

### **AGENT 4: Backend & Integration Engineer**
**Responsibility:** Build the FastAPI backend connecting ML models to the frontend

**Sub-Agents (Proactive Activation):**
- **4A: API Developer** - Auto-spawns when model.pkl available
- **4B: Alert Engine** - Auto-spawns when predict endpoint working
- **4C: Database Manager** - Auto-spawns if caching needed for performance

**Deliverables:**
- `api/main.py` (FastAPI app with CORS + authentication)
- `api/routes/predict.py` (`/predict`, `/districts`, `/taluks/{district_id}`)
- `api/routes/forecast.py` (`/forecast/72h/{district_id}`)
- `api/routes/propagation.py` (`/river-propagation/{trigger_point}`)
- `api/routes/alerts.py` (`/alerts/generate`, `/alerts/history`)
- `alerts/alert_engine.py` (threshold logic + Tamil translation)
- `alerts/sms_mock.py` (mock SMS dispatch with logs)

**Time Budget:** 6 hours (parallel with Agent 3)

**Proactive Sub-Agent Logic:**
```python
if model_pkl_exists:
    spawn_subagent("4A: API Developer")
if endpoint_predict_working:
    spawn_subagent("4B: Alert Engine")
if response_time > 2000ms:
    spawn_subagent("4C: Database Manager")
```

---

## 🔧 Specialized Sub-Agents (8)

### **SUB-AGENT 1A: Mock Data Generator**
**Auto-Trigger Condition:** `not os.getenv("OPENWEATHER_API_KEY")` or user selects mock mode

**Purpose:** Generate realistic synthetic flood data when real APIs unavailable

**Intelligence:**
- Models monsoon seasonality (June-Dec rainfall spikes)
- Injects historical event patterns (2015 Chennai floods, 2018 Gaja cyclone)
- Correlates river levels with upstream rainfall using 6-hour lag functions
- Adds realistic noise (σ=15% of mean) and missing value patterns (3-5% MCAR)

**Output Schema:**
```csv
date,district,rainfall_mm,river_level_m,soil_moisture,humidity_pct,reservoir_pct,elevation_m,flood_occurred
2018-11-15,Madurai,185.3,3.2,0.78,89,67,120,1
```

**Proactive Action:** If data generation takes >30 min, auto-switch to pre-baked minimal dataset

---

### **SUB-AGENT 1B: API Wrapper**
**Auto-Trigger Condition:** `file_exists("data/mock/tn_flood_data.csv")`

**Purpose:** Build production-ready API connectors with automatic fallback

**Features:**
- Environment variable toggle: `USE_MOCK_DATA=true/false`
- Rate limit handling with exponential backoff
- Response caching (SQLite for hackathon, Redis-ready)
- Graceful degradation: if OpenWeatherMap fails, use mock + log warning

**Example:**
```python
def get_rainfall(district: str, date: str):
    if os.getenv("USE_MOCK_DATA") == "true":
        return mock_db.query(district, date)
    try:
        response = requests.get(f"{OPENWEATHER_API}/...", timeout=5)
        cache.set(key, response.json(), ttl=3600)
        return response.json()
    except (Timeout, ConnectionError):
        logger.warning("API failed, using cached mock")
        return mock_db.query(district, date)
```

**Proactive Action:** Auto-enables caching if API latency > 2 seconds

---

### **SUB-AGENT 1C: Data Quality Validator**
**Auto-Trigger Condition:** `csv_generated and not validated`

**Purpose:** Ensure data integrity before ML training

**Checks:**
- Schema validation (8 required columns present)
- Date range coverage (minimum 3 years of data)
- Missing value rate (<10% per column)
- Outlier detection (Z-score > 4 flagged, not removed)
- Class balance (flood events 10-40% of total)

**Output:** `data/quality_report.json` with pass/fail + remediation steps

**Proactive Action:** If validation fails, auto-spawn data repair sub-process

---

### **SUB-AGENT 2A: Model Trainer**
**Auto-Trigger Condition:** `training_data_available`

**Purpose:** Train ensemble model with cross-validation

**Process:**
1. Train-test split: 80-20 stratified by district
2. Cross-validation: 5-fold with district grouping (prevent leakage)
3. Models: Random Forest (n_estimators=100) + XGBoost (max_depth=6)
4. Ensemble: Soft voting with 0.4/0.6 RF/XGBoost weights
5. Threshold tuning: Optimize for <15% false alarm rate
6. Export: Joblib dump with metadata JSON

**Output:**
```json
{
  "model_version": "1.0.0",
  "trained_on": "2026-02-25T10:30:00Z",
  "features": ["rainfall_mm", "river_level_m", "soil_moisture", "humidity_pct", "reservoir_pct", "rainfall_7d", "elevation_m"],
  "metrics": {
    "f1_score": 0.83,
    "precision": 0.81,
    "recall": 0.85,
    "false_alarm_rate": 0.12
  }
}
```

**Proactive Action:** If F1 < 0.75, auto-spawn hyperparameter tuner

---

### **SUB-AGENT 2B: XAI Engineer**
**Auto-Trigger Condition:** `model_trained and metrics["f1_score"] >= 0.70`

**Purpose:** Pre-compute SHAP values and generate explanation charts

**Deliverables:**
- Per-feature SHAP importance scores for all 38 districts
- Top-3 driver explanations in plain English
- Pre-rendered bar charts (base64 PNG for instant serving)

**Example Output:**
```json
{
  "district": "Madurai",
  "prediction": 0.87,
  "drivers": [
    {"feature": "river_level_m", "shap_value": 0.42, "display": "Vaigai river level: 42% risk driver"},
    {"feature": "rainfall_7d", "shap_value": 0.31, "display": "7-day rainfall: 31% risk driver"},
    {"feature": "soil_moisture", "shap_value": 0.18, "display": "Soil saturation: 18% risk driver"}
  ],
  "chart_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**Proactive Action:** If SHAP computation >5 min, switch to permutation importance

---

### **SUB-AGENT 2C: Hyperparameter Tuner**
**Auto-Trigger Condition:** `metrics["f1_score"] < 0.75`

**Purpose:** Optimize model performance using Optuna/GridSearch

**Search Space:**
```python
{
    "rf__n_estimators": [50, 100, 200],
    "rf__max_depth": [10, 20, None],
    "xgb__learning_rate": [0.01, 0.1, 0.3],
    "xgb__max_depth": [3, 6, 9]
}
```

**Time Limit:** 30 minutes (early stopping if no improvement in 10 trials)

**Proactive Action:** If tuning doesn't improve F1, recommend feature engineering

---

### **SUB-AGENT 3A: Map Renderer**
**Auto-Trigger Condition:** `geojson_files_exist`

**Purpose:** Render district polygons with risk-based color coding

**Features:**
- Leaflet.js with Tamil Nadu-centered viewport (11.1271°N, 78.6569°E, zoom 7)
- GeoJSON layer with dynamic fillColor based on risk score
- Click handler: opens side panel with district details + SHAP chart
- Responsive: full-height on desktop, 60vh on mobile

**Color Scheme:**
- 0-40%: `#4CAF50` (green)
- 41-65%: `#FFC107` (yellow)
- 66-85%: `#FF9800` (orange)
- 86-100%: `#F44336` (red)

**Proactive Action:** If GeoJSON parsing fails, auto-switch to circle markers at district centroids

---

### **SUB-AGENT 3B: Chart Builder**
**Auto-Trigger Condition:** `api_contract_published`

**Purpose:** Generate Recharts visualizations

**Chart Types:**
1. **SHAP Bar Chart**: Horizontal bars showing feature contributions
2. **72-Hour Timeline**: Line chart with confidence interval bands
3. **Propagation Flow**: Directed graph using react-flow-renderer

**Accessibility:**
- ARIA labels on all charts
- High-contrast color palettes
- Text alternatives for screen readers

**Proactive Action:** If Recharts causes bundle size >500KB, lazy load charts

---

### **SUB-AGENT 4A: API Developer**
**Auto-Trigger Condition:** `model_pkl_exists`

**Purpose:** Build FastAPI backend with async endpoints

**Core Endpoints:**
```python
POST /predict
  Body: {district: str, date: str}
  Returns: {risk_class, probability, shap_drivers}

GET /districts
  Returns: [{name, risk, lat, lon, last_updated}]

GET /taluks/{district_id}
  Returns: [{taluk_name, risk, elevation, vulnerability_score}]

GET /forecast/72h/{district_id}
  Returns: [{hour, risk, confidence_lower, confidence_upper}]

GET /river-propagation/{trigger_district}
  Returns: {graph: {nodes, edges}, timeline: [...]}

POST /alerts/generate
  Body: {district, risk_level}
  Returns: {alert_id, message_tamil, message_english, channels}
```

**Security:**
- JWT authentication on POST endpoints
- Rate limiting: 100 req/min per IP
- CORS: whitelist frontend domain

**Proactive Action:** If endpoint response >2s, auto-enable caching

---

### **SUB-AGENT 4B: Alert Engine**
**Auto-Trigger Condition:** `endpoint_predict_working`

**Purpose:** Generate multi-level alerts in Tamil and English

**Alert Levels:**
- **Advisory (50-64%)**: Blue banner, no SMS
- **Watch (65-79%)**: Yellow banner, SMS to district officials
- **Warning (80-89%)**: Orange banner, SMS to public + officials
- **Emergency (90-100%)**: Red banner, SMS + push + dashboard takeover

**Tamil Translation Map:**
```python
ALERTS_TAMIL = {
    "warning": "எச்சரிக்கை",
    "flood_risk": "வெள்ள அபாயம்",
    "high": "அதிகமாக",
    "medium": "நடுத்தர",
    "move_safe": "பாதுகாப்பான இடத்திற்கு செல்லவும்",
    "reason": "காரணம்"
}
```

**SMS Template:**
```
எச்சரிக்கை: {district} மாவட்டத்தில் வெள்ள அபாயம் {risk_level}. 
காரணம்: {top_shap_driver}. 
உடனடியாக பாதுகாப்பான இடத்திற்கு செல்லவும்.
- Floodline TN
```

**Proactive Action:** If SMS gateway unavailable, auto-enable email fallback

---

## 🔄 Agent Communication Protocol

### **Handoff Contracts**

**Agent 1 → Agent 2:**
- Signal: `data/mock/tn_flood_data.csv` file created + quality validation passed
- Contract: CSV with 8 required columns, no nulls in target variable, minimum 3 years data

**Agent 2 → Agent 4:**
- Signal: `models/flood_classifier.pkl` + `models/metrics.json` created
- Contract: Scikit-learn compatible model with `.predict_proba()` method, F1 ≥ 0.70

**Agent 1 → Agent 3:**
- Signal: GeoJSON files in `data/geospatial/` directory
- Contract: Valid GeoJSON with `properties.district_name` and `properties.NAME_3` (taluk) fields

**Agent 4 → Agent 3:**
- Signal: Backend running on `localhost:8000`, `/health` returns 200
- Contract: OpenAPI schema at `/docs` matching frontend expectations

---

## 🚨 Failure Modes & Proactive Recovery

| Failure | Detection | Auto-Recovery Sub-Agent |
|---------|-----------|-------------------------|
| Mock data generation timeout | Agent 1 >30min | Use pre-baked minimal dataset (1000 rows) |
| Model training F1 <0.70 | Agent 2 validation | Spawn hyperparameter tuner OR use simpler Random Forest |
| GeoJSON file corrupt | Agent 3 parse error | Switch to district centroid markers |
| Backend won't start (port conflict) | Agent 4 startup | Auto-assign random port 8001-8010 |
| SHAP computation >5min | Agent 2B timeout | Switch to permutation importance |
| Frontend bundle >10MB | Agent 3 build | Auto-enable code splitting + lazy loading |

---

## 📊 Agent Performance Metrics

Each agent reports:
- **Completion %**: Features delivered vs. planned
- **Quality score**: Test pass rate (unit + integration)
- **Handoff status**: Dependencies met (🟢 green / 🟡 yellow / 🔴 red)
- **Sub-agent spawns**: Count of proactive sub-agents activated

**Minimum Viable Demo Threshold:**
- Agent 1: 80% (mock data + 1 GeoJSON working)
- Agent 2: 75% (model trained, even if accuracy suboptimal)
- Agent 3: 70% (map rendering, even if 1-2 charts missing)
- Agent 4: 80% (predict + districts endpoints functional)

---

## 🎯 24-Hour Execution Timeline

**Hours 0-4:**
- Agent 1 + Agent 2 run in parallel
- Sub-agents 1A, 1B, 1C, 2A activate automatically based on triggers

**Hours 4-8:**
- Agent 3 + Agent 4 start (using Agent 1/2 outputs)
- Sub-agents 3A, 4A activate
- Integration testing begins

**Hours 8-12:**
- Sub-agents 2B, 3B, 4B activate for advanced features
- Feature freeze: focus on integration bugs

**Hours 12-16:**
- End-to-end demo rehearsal
- Bug fixes only, no new features

**Hours 16-20:**
- Sub-agent 3C (responsive design) activates
- Polish: UI responsiveness, error handling, loading states
- Demo script preparation

**Hours 20-24:**
- Deployment to Render + GitHub Pages
- Final demo recording
- Presentation deck finalization

---

## 🧠 Proactive Sub-Agent Decision Matrix

| Condition | Sub-Agent Spawned | Reason |
|-----------|-------------------|--------|
| No API keys found | 1A: Mock Data Generator | Prevent build blocker |
| Data generation >30min | 1C: Data Quality + fallback | Time constraint mitigation |
| F1 score <0.75 | 2C: Hyperparameter Tuner | Performance optimization |
| SHAP >5min | Switch to permutation | Time constraint mitigation |
| API response >2s | 4C: Database Manager (caching) | UX performance |
| Frontend bundle >10MB | Code splitting sub-process | Load time optimization |
| GeoJSON parse fails | Fallback to centroid markers | Graceful degradation |

---

## 🔮 Post-Hackathon Agent Evolution

**Phase 2 Agents (not in 24-hour scope):**
- **Agent 5: Satellite Image Processor** - Sentinel-1 SAR inundation detection
- **Agent 6: Crowd-Source Validator** - Field officer report ingestion
- **Agent 7: Climate Scenario Modeler** - IPCC projection integration
- **Agent 8: Mobile App Builder** - React Native offline-first app

---

**Agent Architecture Version:** 2.0 (Proactive Sub-Agent Edition)  
**Project:** Floodline TN  
**Last Updated:** 2026-02-25  
**Status:** Ready for parallel deployment with autonomous failure recovery