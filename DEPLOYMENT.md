# Floodline TN - Deployment Guide

## 🌐 Production URLs

- **Frontend:** https://floodline-tn.netlify.app
- **Backend API:** https://floodline-tn-api.onrender.com
- **API Docs:** https://floodline-tn-api.onrender.com/docs
- **Health Check:** https://floodline-tn-api.onrender.com/health

---

## 🏗️ Architecture

```
Frontend (React) → Backend (FastAPI) → ML Models
     ↓                    ↓                 ↓
  Netlify              Render          Pickled Models
```

**Components:**
- **Frontend**: React + Vite, served via Netlify CDN
- **Backend**: FastAPI Python application on Render
- **Data**: Mock datasets (production-ready to swap with real APIs)
- **ML Models**: Pre-trained Random Forest + XGBoost ensemble

---

## 🚀 Pre-Deployment Checklist

Before deploying, run the validation script:

```bash
python scripts/pre_deploy_check.py
```

This checks:
- ✅ All required files exist
- ✅ ML model is trained
- ✅ Data files are generated
- ✅ Deployment configurations are present

---

## 📦 Backend Deployment (Render.com)

### Prerequisites
- GitHub account
- Render.com account (free tier available)
- Repository pushed to GitHub

### Step 1: Push Code to GitHub

```bash
git add .
git commit -m "Production ready deployment"
git push origin main
```

### Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 3: Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository `floodline-tn`
3. Configure service:
   - **Name:** `floodline-tn-api`
   - **Environment:** Python
   - **Region:** Singapore (or closest to target users)
   - **Branch:** `main`
   - **Build Command:** (leave empty - uses render.yaml)
   - **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port 8000`

### Step 4: Set Environment Variables

Go to **Environment** tab and add:

```bash
# Required
SECRET_KEY=<generate-random-32-char-string>
USE_MOCK_DATA=true
ALLOWED_ORIGINS=https://floodline-tn.netlify.app,http://localhost:3000

# Optional (for production APIs)
OPENWEATHER_API_KEY=<your-key>
IMD_API_KEY=<your-key>
CWC_API_KEY=<your-key>
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Run data generation scripts
   - Train ML model
   - Start the FastAPI server
3. Wait 5-10 minutes for first deployment
4. Note the URL: `https://floodline-tn-api.onrender.com`

### Step 6: Verify Backend

```bash
# Check health endpoint
curl https://floodline-tn-api.onrender.com/health

# Expected response:
# {"status": "healthy", "timestamp": "..."}

# Check API docs
# Open: https://floodline-tn-api.onrender.com/docs
```

---

## 🌐 Frontend Deployment (Netlify)

### Prerequisites
- Netlify account (free tier available)
- Node.js 18+ installed
- Netlify CLI installed

### Step 1: Install Netlify CLI

```bash
npm install -g netlify-cli
```

### Step 2: Login to Netlify

```bash
netlify login
```

This opens browser for authentication.

### Step 3: Initialize Site

```bash
cd dashboard
netlify init
```

Follow prompts:
- **Create & configure new site**
- Choose your team
- **Site name:** `floodline-tn`
- **Build command:** `npm run build`
- **Publish directory:** `build`

### Step 4: Configure Environment Variables

#### Option A: Via Dashboard
1. Go to https://app.netlify.com
2. Select your site
3. Go to **Site settings** → **Environment variables**
4. Add:
   ```
   REACT_APP_API_BASE_URL=https://floodline-tn-api.onrender.com/api/v1
   REACT_APP_ENVIRONMENT=production
   ```

#### Option B: Via CLI
```bash
netlify env:set REACT_APP_API_BASE_URL "https://floodline-tn-api.onrender.com/api/v1"
netlify env:set REACT_APP_ENVIRONMENT "production"
```

### Step 5: Deploy

```bash
# Build the application
npm run build

# Deploy to production
netlify deploy --prod
```

Or use the package.json script:
```bash
npm run deploy
```

### Step 6: Verify Frontend

1. Open https://floodline-tn.netlify.app
2. Test all pages:
   - Dashboard (district map)
   - Forecast page
   - Propagation page
   - Alerts page
3. Check browser console for errors

---

## ⚙️ Environment Variables Reference

### Backend (Render)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | JWT signing key (32+ chars) |
| `USE_MOCK_DATA` | Yes | `true` | Use synthetic data vs real APIs |
| `ALLOWED_ORIGINS` | Yes | - | CORS allowed origins (comma-separated) |
| `OPENWEATHER_API_KEY` | No | - | OpenWeatherMap API key |
| `IMD_API_KEY` | No | - | India Meteorological Dept key |
| `CWC_API_KEY` | No | - | Central Water Commission key |
| `DATABASE_URL` | No | - | PostgreSQL connection string |

### Frontend (Netlify)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REACT_APP_API_BASE_URL` | Yes | - | Backend API base URL |
| `REACT_APP_ENVIRONMENT` | Yes | - | `production` or `development` |
| `GENERATE_SOURCEMAP` | No | `false` | Generate source maps |

---

## 🔄 CI/CD Pipeline

### Automatic Deployment

Both backend and frontend auto-deploy on push to `main` branch:

**Backend (Render):**
- Push to `main` → Render auto-deploys
- Build time: ~5-7 minutes
- Includes model training

**Frontend (Netlify):**
- Push to `main` → GitHub Actions → Netlify
- Build time: ~2-3 minutes
- Includes production build optimization

### GitHub Actions Workflows

**Backend CI** (`.github/workflows/backend-ci.yml`):
- Runs tests on push/PR
- Linting with Black + Flake8
- Coverage reports to Codecov

**Frontend CI** (`.github/workflows/frontend-ci.yml`):
- Runs tests on push/PR
- Builds production bundle
- Deploys to Netlify on `main` branch

---

## 🔍 Monitoring & Logs

### Backend Logs (Render)

1. Go to Render dashboard
2. Select `floodline-tn-api` service
3. Click **"Logs"** tab
4. View real-time logs

**Log Levels:**
- `INFO`: Normal operations
- `WARNING`: Non-critical issues
- `ERROR`: Failures requiring attention

### Frontend Logs (Netlify)

1. Go to Netlify dashboard
2. Select `floodline-tn` site
3. Click **"Functions"** or **"Deploy logs"**

### Health Monitoring

**Backend Health Check:**
```bash
curl https://floodline-tn-api.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-02-26T10:30:00Z",
  "model_loaded": true,
  "data_ready": true
}
```

---

## 🛠️ Troubleshooting

### Backend Issues

#### ❌ Build fails on Render
**Symptom:** Build command errors during deployment

**Solutions:**
1. Check `requirements.txt` has all dependencies
2. Verify Python version in `runtime.txt` (3.11.0)
3. Check Render build logs for specific error
4. Test locally: `pip install -r requirements.txt`

#### ❌ Health check fails
**Symptom:** `/health` returns 502/503

**Solutions:**
1. Check if model training completed
2. Verify data files exist in `data/` directory
3. Check Render logs for startup errors
4. Increase Render startup timeout (Settings → Health Check)

#### ❌ CORS errors
**Symptom:** Frontend can't connect to API

**Solutions:**
1. Verify `ALLOWED_ORIGINS` includes frontend URL
2. Check `api/main.py` CORS middleware configuration
3. Ensure frontend uses correct API URL

### Frontend Issues

#### ❌ Build fails on Netlify
**Symptom:** Netlify build log shows errors

**Solutions:**
1. Check `package.json` scripts
2. Verify Node.js version (18+)
3. Test locally: `npm run build`
4. Check for missing dependencies: `npm install`

#### ❌ API connection fails
**Symptom:** Dashboard shows "Failed to load data"

**Solutions:**
1. Verify `REACT_APP_API_BASE_URL` is set correctly
2. Check backend is running (health check)
3. Open browser DevTools → Network tab
4. Check for CORS errors in console

#### ❌ Map not rendering
**Symptom:** District map is blank

**Solutions:**
1. Check GeoJSON files exist in backend
2. Verify `/districts` API returns data
3. Check Leaflet CSS is loaded
4. Open browser console for JavaScript errors

### Database Issues

#### ❌ SQLite errors on Render
**Symptom:** Database locked or read-only errors

**Solutions:**
1. Render's ephemeral filesystem resets on restart
2. Use PostgreSQL for persistent data:
   ```bash
   # Add to render.yaml
   databases:
     - name: floodline-db
       plan: free
   ```
3. Update `DATABASE_URL` environment variable

---

## 🔄 Rollback Procedure

### Backend Rollback (Render)

1. Go to Render dashboard
2. Select **`floodline-tn-api`**
3. Click **"Events"** tab
4. Find previous successful deployment
5. Click **"Redeploy"**

### Frontend Rollback (Netlify)

1. Go to Netlify dashboard
2. Select **`floodline-tn`** site
3. Click **"Deploys"** tab
4. Find previous successful deploy
5. Click **"⋮"** → **"Publish deploy"**

---

## 📈 Performance Optimization

### Backend

**Enable Caching:**
```python
# api/routes/predict.py
from functools import lru_cache

@lru_cache(maxsize=128)
def predict_cached(district: str, date: str):
    return predict(district, date)
```

**Database Connection Pooling:**
```python
# Use SQLAlchemy with pool
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL, pool_size=10)
```

### Frontend

**Code Splitting:**
```javascript
// Lazy load components
const ForecastPage = lazy(() => import('./pages/ForecastPage'));
```

**Asset Optimization:**
- Enable Netlify image optimization
- Use WebP format for images
- Minify CSS/JS (done by Vite)

---

## 🆕 Deploying Updates

### Minor Updates (Bug Fixes)

```bash
# 1. Fix bug locally
# 2. Test locally
npm run build  # frontend
python -m pytest  # backend

# 3. Commit and push
git add .
git commit -m "Fix: description"
git push origin main

# 4. Auto-deploys via CI/CD
```

### Major Updates (New Features)

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Develop and test
# 3. Create pull request
# 4. Merge to main after review
# 5. Auto-deploys to production
```

---

## 🔐 Security Best Practices

1. **Never commit secrets:**
   - Use environment variables
   - Add `.env` to `.gitignore`

2. **Use HTTPS only:**
   - Render/Netlify provide free SSL
   - Enforce HTTPS redirects

3. **API Rate Limiting:**
   - Already configured in `api/middleware/rate_limit.py`
   - 100 requests/minute per IP

4. **CORS Configuration:**
   - Whitelist only known origins
   - Don't use `*` in production

5. **Dependency Updates:**
   ```bash
   # Check for vulnerabilities
   pip-audit  # Python
   npm audit  # JavaScript
   ```

---

## 📞 Support & Resources

- **GitHub Issues:** [floodline-tn/issues](https://github.com/jason1496mathew-max/floodline-tn/issues)
- **API Status:** https://floodline-tn-api.onrender.com/health
- **Render Docs:** https://render.com/docs
- **Netlify Docs:** https://docs.netlify.com

---

## ✅ Post-Deployment Checklist

- [ ] Backend health check returns 200
- [ ] Frontend loads without errors
- [ ] All API endpoints working
- [ ] Districts map rendering correctly
- [ ] Forecast page showing data
- [ ] Propagation model working
- [ ] Alerts can be generated
- [ ] SHAP explanations visible
- [ ] Mobile responsive design works
- [ ] CI/CD pipeline configured
- [ ] Monitoring set up
- [ ] Documentation updated

---

**Last Updated:** February 26, 2025  
**Version:** 1.0.0  
**Status:** Production Ready 🚀
