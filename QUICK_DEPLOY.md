# 🚀 Quick Deployment Checklist

> **10-minute deployment guide for Floodline TN**

---

## ✅ Pre-Deployment

```bash
# 1. Validate everything is ready
python scripts/pre_deploy_check.py

# 2. Commit all changes
git add .
git commit -m "Production deployment ready"
git push origin main
```

---

## 🔧 Backend Deployment (Render.com)

### Step 1: Create Account
- Go to https://render.com
- Sign up with GitHub

### Step 2: Create Web Service
- Click **"New +" → "Web Service"**
- Connect repository: `floodline-tn`
- Name: `floodline-tn-api`
- Region: **Singapore** (or closest)
- Branch: `main`
- Build Command: (auto-detected from `render.yaml`)
- Start Command: `uvicorn api.main:app --host 0.0.0.0 --port 8000`

### Step 3: Set Environment Variables
```bash
SECRET_KEY=<generate-with-python-secrets>
USE_MOCK_DATA=true
ALLOWED_ORIGINS=https://floodline-tn.netlify.app,http://localhost:3000
```

### Step 4: Deploy
- Click **"Create Web Service"**
- Wait 5-10 minutes
- Note URL: `https://floodline-tn-api.onrender.com`

### Step 5: Verify
```bash
curl https://floodline-tn-api.onrender.com/health
# Should return: {"status": "healthy", ...}
```

---

## 🌐 Frontend Deployment (Netlify)

### Step 1: Install CLI
```bash
npm install -g netlify-cli
```

### Step 2: Login
```bash
netlify login
```

### Step 3: Deploy
```bash
cd dashboard
npm install
npm run build
netlify deploy --prod
```

### Step 4: Set Environment Variables
- Go to https://app.netlify.com
- Select site → **Site settings → Environment variables**
- Add:
  ```
  REACT_APP_API_BASE_URL=https://floodline-tn-api.onrender.com/api/v1
  REACT_APP_ENVIRONMENT=production
  ```

### Step 5: Redeploy
```bash
netlify deploy --prod
```

### Step 6: Verify
- Open: https://floodline-tn.netlify.app
- Check: District map loads
- Test: Click district → SHAP chart appears

---

## 🎯 Demo Preparation

### 1. Test All Features

```bash
# Dashboard
✅ District map with color-coded risk
✅ Click district → SHAP panel opens
✅ Navigate to Forecast page
✅ Navigate to Propagation page
✅ Navigate to Alerts page
✅ Generate test alert

# API
✅ Health check: /health
✅ Districts list: /api/v1/districts
✅ Predict endpoint: /api/v1/predict
```

### 2. Prepare Demo Script
- Read [DEMO.md](DEMO.md)
- Practice 10-minute walkthrough
- Prepare for Q&A (see DEMO.md)

### 3. Backup Plan
- Have local dev running: `uvicorn api.main:app --reload`
- Have video recording ready
- Have screenshots in presentation deck

---

## 📋 Final Checklist

Before demo:
- [ ] Backend health check returns 200
- [ ] Frontend loads without errors
- [ ] All 38 districts visible on map
- [ ] SHAP charts rendering
- [ ] Forecast page working
- [ ] Propagation graph displaying
- [ ] Alerts can be generated
- [ ] Tamil text displays correctly
- [ ] Mobile responsive (test on phone)
- [ ] Internet connection stable
- [ ] Backup video ready

---

## 🆘 Quick Troubleshooting

### Backend Issues

**"Build failed on Render"**
```bash
# Solution: Check requirements.txt
pip freeze > requirements.txt
git commit -am "Update dependencies"
git push
```

**"Health check failing"**
```bash
# Solution: Check logs on Render dashboard
# Common issue: Model training timeout
# Fix: Reduce model complexity in models/train.py
```

### Frontend Issues

**"API calls failing"**
```bash
# Solution: Verify environment variables
# Netlify dashboard → Environment variables
# Must have: REACT_APP_API_BASE_URL
```

**"Map not rendering"**
```bash
# Solution: Check browser console
# Common issue: GeoJSON not loaded
# Verify: https://floodline-tn-api.onrender.com/api/v1/districts
```

---

## 📞 Quick Links

- **Dashboard:** https://floodline-tn.netlify.app
- **API:** https://floodline-tn-api.onrender.com
- **API Docs:** https://floodline-tn-api.onrender.com/docs
- **Render Dashboard:** https://dashboard.render.com
- **Netlify Dashboard:** https://app.netlify.com
- **GitHub Repo:** https://github.com/jason1496mathew-max/floodline-tn

---

## 🎤 Demo Day Essentials

**Bring:**
- [ ] Laptop fully charged
- [ ] Backup charger
- [ ] Mobile hotspot (if wifi unstable)
- [ ] USB drive with video backup
- [ ] Presentation remote (if available)
- [ ] Water bottle
- [ ] Confidence! 🚀

**Avoid:**
- ❌ Demo-ing features you haven't tested
- ❌ Reading from script (just use as guide)
- ❌ Apologizing for limitations
- ❌ Getting defensive about technical choices

**Focus On:**
- ✅ Impact: Lives saved, disaster preparedness
- ✅ Innovation: SHAP explainability, Tamil support
- ✅ Feasibility: <$100/month, government-ready
- ✅ Scalability: Works for any Indian state

---

**Good luck! You've got this. 🌊🚀**

*Remember: 72 hours can save lives. That's what this project is about.*
