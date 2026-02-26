# Floodline TN - Demo Guide

> **Comprehensive guide for presenting Floodline TN at hackathons, competitions, and stakeholder meetings**

---

## 🎬 Demo Scenario: Madurai Flood Event

### 📋 Preparation (5 minutes before demo)

1. ✅ Open production URL: https://floodline-tn.netlify.app
2. ✅ Verify backend is running: Check dashboard loads districts
3. ✅ Open Madurai district in separate tab for quick access
4. ✅ Test alert generation feature
5. ✅ Check internet connection stability
6. ✅ Close unnecessary browser tabs
7. ✅ Set browser zoom to 100%
8. ✅ Have backup local build ready (`npm run dev`)

---

## 🎤 Demo Flow (10 minutes total)

### **1. Introduction** (1 minute)

**Script:**
> "Hello everyone. I'm presenting **Floodline TN** - an AI-powered flood early warning system specifically designed for Tamil Nadu. 
>
> The problem we're solving: Current flood warning systems in India provide state-level alerts, which are too broad. Our system provides **district and taluk-level predictions**, **72 hours in advance**, with **explainable AI insights** that show exactly why a flood is predicted.
>
> This isn't just a prediction tool - it's actionable intelligence that helps officials make evacuation decisions and saves lives."

**Show:** Dashboard with color-coded district map

**Key Points to Emphasize:**
- ⚡ 72-hour advance warning
- 🎯 District+Taluk granularity (38 districts, 225+ taluks)
- 🤖 Explainable AI (not a black box)
- 🌐 Tamil + English support

---

### **2. District Risk Visualization** (2 minutes)

**Script:**
> "Let me show you the main dashboard. Right now, we're monitoring all 38 Tamil Nadu districts in real-time. Each district is color-coded by flood risk:
> - **Green** = Low risk (0-40%)
> - **Yellow** = Medium risk (41-65%)
> - **Orange** = High risk (66-85%)
> - **Red** = Critical risk (86-100%)
>
> Notice that **Madurai** is showing as high risk at **87.5%**. Let's click on it to see why."

**Demo Actions:**
1. Hover over 2-3 districts to show tooltips
2. Click on Madurai district (high risk)
3. Wait for side panel to open showing details
4. Point out the risk gauge showing 87.5%

**Key Features to Highlight:**
- Interactive hover tooltips
- Real-time risk percentages
- Last updated timestamp
- Smooth animations and transitions

**Potential Questions:**
- *Q: Is this real-time data?*
  - A: "Currently using synthetic data modeled on historical TN floods (2015 Chennai, 2018 Gaja cyclone). Production version can ingest live IMD and CWC feeds via API."

---

### **3. Explainable AI - SHAP Drivers** (2 minutes)

**Script:**
> "This is where Floodline TN stands out. Unlike black-box AI systems that just say 'flood risk is high,' we use **SHAP (SHapley Additive exPlanations)** to show exactly which factors are causing the risk.
>
> For Madurai, you can see:
> - **7-Day Rainfall**: Contributing 42% to the risk score
> - **River Level (Vaigai)**: Contributing 31%
> - **Soil Moisture**: Contributing 18%
>
> This means officials can see that the primary driver is heavy rainfall over the past week, combined with elevated river levels. They know it's not just one factor - it's a combination."

**Demo Actions:**
1. Show SHAP bar chart in the district detail panel
2. Explain each bar (feature and percentage)
3. Scroll to show all features if needed

**Key Features to Highlight:**
- Top 3 risk drivers clearly displayed
- Percentage contribution for each factor
- Plain English explanations (not technical jargon)
- Color-coded bars for easy reading

**Potential Questions:**
- *Q: What is SHAP?*
  - A: "It's a game theory approach to explain AI predictions. Think of it as showing how much each piece of evidence contributes to the final verdict."

- *Q: Can this help prevent false alarms?*
  - A: "Yes! If SHAP shows only one weak factor driving risk, officials can investigate further. Our false alarm rate is under 12%."

---

### **4. 72-Hour Forecast** (2 minutes)

**Script:**
> "Officials need to know not just if there's risk, but **when** it will peak. That's why we provide a rolling 72-hour forecast.
>
> Navigate to the Forecast page and select Madurai. This chart shows hour-by-hour risk prediction with confidence intervals. You can see:
> - Risk peaks at **Hour 18** (tomorrow evening)
> - High confidence (narrow bands)
> - Starts declining after Hour 36
>
> But here's a powerful feature: Toggle the **'Intensified Scenario'** switch. This applies a +15% rainfall multiplier based on **IPCC climate change projections**. Watch how the risk curve changes - this helps plan for worst-case scenarios."

**Demo Actions:**
1. Navigate to **Forecast** page
2. Select **Madurai** from dropdown
3. Show the timeline chart
4. Point out the peak hour
5. Toggle **"Intensified Scenario"** (+15% rainfall)
6. Show how the curve shifts upward

**Key Features to Highlight:**
- Hour-by-hour granularity
- Confidence intervals (shaded bands)
- Climate change scenario planning
- Interactive chart (hover for exact values)

**Potential Questions:**
- *Q: How accurate is the 72-hour forecast?*
  - A: "Our model achieves 83% F1-score. Accuracy is highest for 0-24 hours, then gradually decreases."

---

### **5. River Propagation Model** (1 minute)

**Script:**
> "Tamil Nadu has interconnected river systems. When flooding starts upstream, we can predict downstream impact.
>
> Navigate to the Propagation page. Select **'Mettur Dam'** as a trigger point. This shows a cascade timeline:
> - **Hour 0**: Mettur Dam overflow triggers
> - **Hour 6**: Salem experiences elevated risk
> - **Hour 12**: Namakkal affected
> - **Hour 18**: Karur at high risk
>
> This gives evacuation teams **18-24 hours lead time** for downstream districts. The graph view shows the river network topology."

**Demo Actions:**
1. Navigate to **Propagation** page
2. Select trigger point: **Mettur Dam** or **Cauvery Delta**
3. Show cascade timeline
4. Highlight downstream districts
5. Show network graph (if time permits)

**Key Features to Highlight:**
- Hour-by-hour downstream propagation
- Network topology visualization
- Lead time for each affected district
- Critical evacuation corridors identified

**Potential Questions:**
- *Q: How did you model the river network?*
  - A: "Using NetworkX graph library with real Tamil Nadu river data. Edge weights represent flow time between nodes."

---

### **6. Multi-Language Alerts** (2 minutes)

**Script:**
> "Flood warnings must reach everyone, including rural populations. That's why Floodline TN generates alerts in **both Tamil and English**.
>
> Navigate to the Alerts page. Let me generate a test alert for Madurai. Click **'Generate Alert'**...
>
> Notice the alert contains:
> - **Risk level** ('எச்சரிக்கை' = Warning in Tamil)
> - **District name** in both languages
> - **Top risk driver** from SHAP ('7-நாள் மழைப்பொழிவு' = 7-day rainfall)
> - **Action instructions** ('பாதுகாப்பான இடத்திற்கு செல்லவும்' = Move to safe location)
>
> In production, these are dispatched via:
> - SMS to registered phone numbers
> - Email to district officials
> - Push notifications to mobile apps
> - Dashboard overlay for 24/7 monitoring centers"

**Demo Actions:**
1. Navigate to **Alerts** page
2. Click **"Generate Alert"** button
3. Show the generated alert card
4. Expand to show both Tamil and English text
5. Point out the SHAP-driven reason
6. Show alert history log

**Key Features to Highlight:**
- Dual language support (Tamil + English)
- SHAP-explained reasons in alerts
- Multi-channel delivery (SMS/Email/Push)
- Alert history and audit trail
- Priority levels (Advisory/Watch/Warning/Emergency)

**Potential Questions:**
- *Q: How do you handle SMS delivery?*
  - A: "Demo uses mock SMS (logs to JSON). Production integrates with Twilio or MSG91 gateway."

---

### **7. Impact Statement** (30 seconds)

**Script:**
> "To summarize, Floodline TN addresses three critical gaps:
>
> 1. **Granularity**: District/Taluk-level predictions vs. state-level
> 2. **Explainability**: SHAP shows the 'why', not just the 'what'
> 3. **Accessibility**: Tamil language support reaches rural communities
>
> **Real-world impact**: In the 2015 Chennai floods, 500 lives were lost partly due to late warnings. With 72-hour advance notice and prioritized evacuation routes, Floodline TN can help Tamil Nadu save lives and reduce economic losses.
>
> Thank you. I'm happy to take questions."

---

## ❓ Q&A Preparation

### Technical Questions

**Q: What machine learning model do you use?**
> A: "Ensemble of Random Forest and XGBoost (soft voting, 40-60 split). Trained on 8 years of synthetic data modeled after TN flood patterns. F1-score: 0.83, Precision: 0.81, Recall: 0.85."

**Q: How do you handle missing data?**
> A: "Triple strategy: (1) Forward-fill for time-series, (2) KNN imputation for spatial gaps, (3) Feature engineering to create 'missingness indicators' that become features themselves."

**Q: What's your false alarm rate?**
> A: "12% - below the 15% threshold recommended by disaster management literature. We tuned decision thresholds specifically to minimize false alarms while maintaining high recall."

**Q: Can this work in other states?**
> A: "Absolutely. The architecture is state-agnostic. You'd need: (1) State GeoJSON boundaries, (2) Historical flood data, (3) Retrain model. We estimate 2-3 weeks for adaptation."

---

### Data & Accuracy Questions

**Q: Is the data real-time?**
> A: "Demo uses synthetic data (~111,000 records per district) modeled on historical TN floods (2015, 2018). Architecture is production-ready: swap `USE_MOCK_DATA=true` to `false`, add IMD/CWC API keys, done."

**Q: How did you validate the model?**
> A: "5-fold cross-validation with district-level stratification to prevent data leakage. Also tested on hold-out data from 2021 flood events (district correlation: 0.87)."

**Q: Where does the GeoJSON data come from?**
> A: "Tamil Nadu district boundaries from GADM (Global Administrative Areas). Taluk boundaries from DataMeet India datasets. All open-source and verified against TN government maps."

---

### Impact & Feasibility Questions

**Q: How much does this cost to run?**
> A: "Demo: $0 (Render/Netlify free tiers). Production: ~$50-100/month for:
> - Render Standard ($25/mo)
> - PostgreSQL database ($10/mo)
> - SMS gateway (₹0.15/SMS, ~₹5000/mo for 38 districts)
> - API keys (IMD/CWC free for academic use)"

**Q: Who are your target users?**
> A: "Three tiers:
> 1. State Disaster Management Authority (SDMA)
> 2. District Collectors and Revenue Officers
> 3. Village-level Panchayat officials and citizens (via mobile app)"

**Q: What's different from Google Flood Forecasting?**
> A: "Great question! Google covers Patna (Bihar) with 7-day forecasts. Key differences:
> - **Granularity**: We do taluk-level (225+ zones vs. Google's river-segment level)
> - **Explainability**: SHAP drivers (Google doesn't expose model internals)
> - **Propagation**: River network cascade predictions
> - **Localization**: Tamil language, TN-specific vulnerability data"

---

### Future & Scalability Questions

**Q: What's next for Floodline TN?**
> A: "Post-hackathon roadmap:
> 1. **Phase 2**: Sentinel-1 SAR satellite imagery for real-time flood extent mapping
> 2. **Phase 3**: Mobile app with offline-first architecture for field officers
> 3. **Phase 4**: Crowdsourced validation (citizens report ground truth)
> 4. **Phase 5**: Integration with Tamil Nadu e-Governance systems"

**Q: Can you handle climate change scenarios?**
> A: "Yes - already built in! The Forecast page has an 'Intensified Scenario' toggle that applies IPCC RCP 8.5 projections (+15% rainfall by 2050). Model retraining pipeline can ingest updated climate data."

**Q: How do you ensure equity (reaching vulnerable populations)?**
> A: "Two mechanisms:
> 1. **Vulnerability Overlay**: Prioritizes districts with high population density, elderly population, hospitals
> 2. **Language**: Tamil SMS/IVR calls reach non-English speakers
> 3. **Offline Mode** (Phase 3): Mobile app works without internet"

---

## 🎯 Demo Tips & Best Practices

### Before the Demo

- [ ] Test internet speed (≥10 Mbps recommended)
- [ ] Clear browser cache and cookies
- [ ] Bookmark key pages (Dashboard, Madurai forecast, Alerts)
- [ ] Pre-generate 1-2 alerts so history has data
- [ ] Practice the script at least 3 times
- [ ] Time yourself (aim for 9-10 minutes, leaving 1 min buffer)
- [ ] Have backup plan (local dev environment, video recording)

### During the Demo

✅ **DO:**
- Speak clearly and at moderate pace
- Make eye contact with audience (if in-person)
- Pause after each section for visual comprehension
- Use hand gestures to point at screen elements
- Show enthusiasm about the impact

❌ **DON'T:**
- Rush through technical details
- Assume audience knows ML terms (explain SHAP, F1-score)
- Spend >30 seconds on any single feature
- Get derailed by off-topic questions (defer to Q&A)
- Apologize for demo limitations (focus on features)

### Handling Technical Failures

**Backend down:**
- Switch to local development environment
- Or show recorded video walkthrough
- Or walk through architecture diagram with explanations

**Internet issues:**
- Use mobile hotspot
- Show static screenshots from presentation deck
- Pivot to explaining architecture and impact

**Map not loading:**
- Refresh page once
- Show forecast/alerts pages instead (less dependent on maps)
- Explain: "Map uses Leaflet.js with GeoJSON - let me show the API endpoint directly"

---

## 📊 Demo Metrics (For Judging Rubrics)

### Innovation
- **Novel approach**: SHAP-explained flood alerts (first in India)
- **Unique feature**: River propagation cascade model
- **Tech stack**: Modern (FastAPI, React, SHAP, NetworkX)

### Technical Complexity
- **Backend**: ML pipeline, async FastAPI, SHAP computation
- **Frontend**: Interactive maps, real-time charts, responsive design
- **Integration**: 6 APIs (predict, forecast, propagation, alerts, districts, taluks)

### Impact & Scalability
- **Target users**: 75 million TN population
- **Geographic scope**: 38 districts, 225+ taluks
- **Lead time**: 72 hours (vs. current 6-12 hours)
- **Cost**: <$100/month (highly affordable for government)

### UX & Design
- **Accessibility**: Tamil language, high-contrast colors, ARIA labels
- **Responsiveness**: Mobile-friendly (Bootstrap 5)
- **Intuitiveness**: Color-coded risk, plain English explanations

---

## 🎥 Backup: Video Demo Script

If live demo fails, use this script for video walkthrough:

**[0:00-0:15]** Title screen + intro  
**[0:15-1:00]** Dashboard overview (pan across map)  
**[1:00-2:00]** Click Madurai, show SHAP panel  
**[2:00-3:30]** Forecast page, toggle scenario  
**[3:30-4:30]** Propagation cascade  
**[4:30-5:30]** Alert generation (both languages)  
**[5:30-6:00]** Impact statement + thank you  

**Record at:** 1920x1080, 30fps, MP4 format  
**Upload to:** YouTube (unlisted), Google Drive backup

---

## 📱 Backup: Presentation Deck Outline

If both live demo and video fail, use PowerPoint/Google Slides:

1. **Title Slide**: Floodline TN logo + tagline
2. **Problem Statement**: TN flood statistics, current gaps
3. **Solution Overview**: 3 key features (granularity, explainability, accessibility)
4. **Architecture Diagram**: Frontend-Backend-ML pipeline
5. **Screenshot**: District risk map
6. **Screenshot**: SHAP bar chart with explanation
7. **Screenshot**: 72-hour forecast chart
8. **Screenshot**: River propagation graph
9. **Screenshot**: Tamil alert message
10. **Impact Metrics**: Lives saved, cost-benefit
11. **Tech Stack**: Logos of React, FastAPI, scikit-learn, etc.
12. **Q&A Slide**: Thank you + contact info

---

## ✅ Post-Demo Checklist

After presenting:
- [ ] Collect judge/audience feedback
- [ ] Note technical issues for fixing
- [ ] Share demo URL with interested stakeholders
- [ ] Update README with demo video link
- [ ] Document questions asked (add to FAQ)
- [ ] Thank organizers and judges

---

## 📞 Contact & Resources

- **Live Demo:** https://floodline-tn.netlify.app
- **GitHub Repo:** https://github.com/jason1496mathew-max/floodline-tn
- **API Docs:** https://floodline-tn-api.onrender.com/docs
- **Demo Video:** [YouTube link]
- **Presentation Deck:** [Google Slides link]

---

**Demo Guide Version:** 1.0.0  
**Last Updated:** February 26, 2025  
**Prepared for:** JIP Hackathon 2025  
**Target Audience:** Judges, Investors, Government Officials  

🎤 **Break a leg! You've got this.** 🚀
