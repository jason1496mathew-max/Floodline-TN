# 🐍 Python Installation Guide for Floodline TN

## Current Status
Python is not installed or not properly configured on your system.

## Installation Options

### Option 1: Official Python Installer (Recommended)

1. Download Python 3.10 or later from: https://www.python.org/downloads/
2. During installation, **CHECK** "Add Python to PATH"
3. Install with default settings
4. Verify installation:
   ```powershell
   python --version
   # Should show: Python 3.10.x or later
   ```

### Option 2: Chocolatey Package Manager

```powershell
# Run PowerShell as Administrator
choco install python310 -y

# Verify installation
python --version
```

### Option 3: Windows Store

```powershell
# Open Microsoft Store and search for "Python 3.10"
# Or run:
winget install Python.Python.3.10
```

## After Python Installation

Once Python is installed, run these commands in the project directory:

```powershell
# Navigate to project
cd C:\Users\HP\Desktop\jiphackathon

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Validate setup
python scripts\validate_setup.py
```

## Troubleshooting

### "Python not found" after installation
- Restart PowerShell/Terminal
- Verify PATH environment variable includes Python directory
- Try `py` command instead of `python`

### "Execution policy" error when activating venv
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### GeoPandas installation fails
```powershell
# Install from conda-forge if using Anaconda
conda install geopandas

# Or use pre-built wheels
pip install --find-links=https://girder.github.io/large_image_wheels GDAL
pip install geopandas
```

## Quick Validation

After setup, ensure these imports work:

```python
python -c "import sklearn, xgboost, fastapi, pandas; print('✅ All OK')"
```

## Next Steps

Once Python is installed and dependencies are ready:
1. ✅ Run validation script: `python scripts\validate_setup.py`
2. Move to Prompt 2: Mock data generation
3. Start development!

---
**Status:** Waiting for Python installation
**Agent:** Data Pipeline Engineer (Agent 1)
**Module:** 01 - Project Setup
