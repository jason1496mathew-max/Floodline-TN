# Environment Variables Guide

## 📝 Configuration Files

Floodline TN uses environment variables for configuration. This guide explains how to set them up.

---

## 📂 Files Structure

```
floodline-tn/
├── .env.example          # Template for backend (DO NOT COMMIT .env)
├── .env                  # Your local backend config (gitignored)
└── dashboard/
    ├── .env.example      # Template for frontend
    ├── .env.local        # Your local frontend config (gitignored)
    └── .env.production   # Production frontend config (committed)
```

---

## 🔧 Backend Configuration

### 1. Create Local .env File

```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env  # or use any text editor
```

### 2. Required Variables

#### **SECRET_KEY** (Required)
- **Purpose:** JWT token signing, session encryption
- **Generate:**
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- **Example:** `SECRET_KEY=abc123XYZ789_secure_random_string`

#### **USE_MOCK_DATA** (Required)
- **Purpose:** Toggle between synthetic data and real APIs
- **Values:** `true` | `false`
- **Development:** `true`
- **Production:** `true` (until real API keys obtained)

#### **ALLOWED_ORIGINS** (Required)
- **Purpose:** CORS (Cross-Origin Resource Sharing) configuration
- **Format:** Comma-separated URLs (no spaces)
- **Development:** `http://localhost:3000,http://localhost:5173`
- **Production:** `https://floodline-tn.netlify.app`

---

### 3. Optional Variables

#### **API Keys** (Only if USE_MOCK_DATA=false)

**OPENWEATHER_API_KEY:**
- Get from: https://openweathermap.org/api
- Free tier: 1000 calls/day

**IMD_API_KEY:**
- Contact: India Meteorological Department
- Academic use: Often free

**CWC_API_KEY:**
- Contact: Central Water Commission
- Government projects: Often free

#### **Database** (Optional - defaults to SQLite)

```bash
# Development (SQLite - no setup needed)
DATABASE_URL=sqlite:///./data/floodline.db

# Production (PostgreSQL on Render)
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

#### **SMS Alerts** (Optional - for alert delivery)

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

Get from: https://www.twilio.com (Free trial: $15 credit)

#### **Email Alerts** (Optional)

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Gmail Setup:**
1. Enable 2FA on Google account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use app password (not your real password)

---

## 🌐 Frontend Configuration

### 1. Create Local .env File

```bash
cd dashboard

# Copy template
cp .env.example .env.local

# Edit with your values
nano .env.local
```

### 2. Required Variables

#### **REACT_APP_API_BASE_URL** (Required)
- **Purpose:** Backend API endpoint
- **Development:** `http://localhost:8000/api/v1`
- **Production:** `https://floodline-tn-api.onrender.com/api/v1`

#### **REACT_APP_ENVIRONMENT** (Required)
- **Purpose:** Environment indicator
- **Values:** `development` | `staging` | `production`

### 3. Optional Variables

```bash
# Disable source maps in production (faster builds)
GENERATE_SOURCEMAP=false

# Enable debug logging
REACT_APP_DEBUG=true

# Custom API timeout (milliseconds)
REACT_APP_API_TIMEOUT=30000
```

---

## 🚀 Deployment Configuration

### Render.com (Backend)

Set in Render dashboard → Environment variables:

```bash
SECRET_KEY=<generate-random-string>
USE_MOCK_DATA=true
ALLOWED_ORIGINS=https://floodline-tn.netlify.app,http://localhost:3000
PYTHON_VERSION=3.11.0
```

**How to set:**
1. Go to https://dashboard.render.com
2. Select your service
3. Environment tab → Add Environment Variable
4. Click "Save Changes" → Triggers redeploy

### Netlify (Frontend)

Set in Netlify dashboard → Site settings → Environment variables:

```bash
REACT_APP_API_BASE_URL=https://floodline-tn-api.onrender.com/api/v1
REACT_APP_ENVIRONMENT=production
```

**How to set:**
1. Go to https://app.netlify.com
2. Select your site
3. Site settings → Environment variables
4. Click "Add a variable"
5. Redeploy: Deploys → Trigger deploy

### GitHub Actions

Set in GitHub repository settings → Secrets and variables → Actions:

```bash
# Secrets (encrypted)
NETLIFY_AUTH_TOKEN=<your-netlify-token>
NETLIFY_SITE_ID=<your-site-id>

# Variables (not encrypted)
REACT_APP_API_BASE_URL=https://floodline-tn-api.onrender.com/api/v1
```

**How to set:**
1. Go to repository on GitHub
2. Settings → Secrets and variables → Actions
3. New repository secret

---

## 🔒 Security Best Practices

### ❌ Never Commit Secrets

```bash
# Ensure .env is in .gitignore
echo ".env" >> .gitignore
echo "dashboard/.env.local" >> .gitignore

# Check what will be committed
git status

# Verify secrets not in history
git log --all --full-history -- .env
```

### ✅ Rotate Keys Regularly

- **SECRET_KEY:** Every 90 days
- **API Keys:** When team members leave
- **Database passwords:** After security incidents

### ✅ Use Environment-Specific Values

```bash
# Development: Relaxed security
ALLOWED_ORIGINS=*
LOG_LEVEL=DEBUG

# Production: Strict security
ALLOWED_ORIGINS=https://floodline-tn.netlify.app
LOG_LEVEL=WARNING
```

### ✅ Validate Environment Variables

The backend automatically validates required variables on startup:

```python
# api/main.py checks:
- SECRET_KEY exists and ≥32 chars
- ALLOWED_ORIGINS is valid URL list
- USE_MOCK_DATA is true/false
```

---

## 🛠️ Troubleshooting

### Backend Issues

**Problem:** `SECRET_KEY not set`
```bash
# Solution: Generate and set
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output to .env
```

**Problem:** `CORS errors in browser console`
```bash
# Solution: Check ALLOWED_ORIGINS
# Must include frontend URL exactly (including http/https)
ALLOWED_ORIGINS=http://localhost:3000  # ✅ Correct
ALLOWED_ORIGINS=localhost:3000         # ❌ Wrong (missing http://)
```

### Frontend Issues

**Problem:** `API calls fail with 404`
```bash
# Solution: Check REACT_APP_API_BASE_URL
# Must end with /api/v1 (no trailing slash)
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1  # ✅ Correct
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1/ # ❌ Wrong (trailing slash)
```

**Problem:** `Environment variables not loading`
```bash
# Solution: Restart dev server
# Vite/React only loads .env on startup
npm run dev  # Restart needed after .env changes
```

---

## 📋 Checklist

Before deploying:

- [ ] All required variables set
- [ ] SECRET_KEY is strong (≥32 chars)
- [ ] ALLOWED_ORIGINS matches frontend URL
- [ ] .env files in .gitignore
- [ ] No secrets in Git history
- [ ] Production values different from development
- [ ] API keys have spending limits (if paid)
- [ ] Database backups configured (if PostgreSQL)

---

## 📞 Support

If you encounter issues:
1. Check this guide
2. Verify .env.example template
3. See DEPLOYMENT.md for platform-specific setup
4. GitHub Issues: Report missing documentation

---

**Last Updated:** February 26, 2025  
**Version:** 1.0.0
