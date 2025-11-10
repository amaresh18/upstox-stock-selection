# How Railway Knows Which Script to Run

## Overview

When you have multiple scripts in your project, Railway needs to know which one to run. Railway determines this through **configuration files** in your project root.

## Configuration Files

### 1. `railway.json` (Primary - Takes Priority)

**Location**: Project root (`railway.json`)

**Current Configuration**:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python scripts/run_continuous_alerts.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Key Field**: `deploy.startCommand`
- This tells Railway exactly which command to run
- **This takes priority** over other methods

### 2. `Procfile` (Secondary - Used if railway.json doesn't exist)

**Location**: Project root (`Procfile`)

**Current Configuration**:
```
worker: python scripts/run_continuous_alerts.py
```

**Format**: `process_type: command`
- `worker` = process type name
- `python scripts/run_continuous_alerts.py` = command to run

**When Used**: Railway uses this if `railway.json` doesn't specify a `startCommand`

## How Railway Chooses

Railway follows this priority order:

1. **`railway.json` → `deploy.startCommand`** (Highest Priority)
   - If this exists, Railway uses it
   - ✅ **Currently configured**: `python scripts/run_continuous_alerts.py`

2. **`Procfile` → `worker` process**
   - Used if `railway.json` doesn't have `startCommand`
   - ✅ **Currently configured**: `python scripts/run_continuous_alerts.py`

3. **Railway Dashboard Settings**
   - You can manually set the start command in Railway dashboard
   - Settings → Start Command

4. **Auto-detection** (Lowest Priority)
   - Railway tries to auto-detect based on project type
   - May not work correctly for Python projects with multiple scripts

## Current Setup

**Railway is configured to run**: `python scripts/run_continuous_alerts.py`

This is specified in **both** configuration files:
- ✅ `railway.json` → `startCommand`
- ✅ `Procfile` → `worker` process

## Available Scripts in Your Project

Your `scripts/` folder contains:

```
scripts/
├── run_continuous_alerts.py      ← Currently running on Railway
├── run_realtime_alerts.py        ← One-time alerts for specific date
├── run_backtest.py               ← Backtesting script
├── run_stock_selection.py        ← Stock selection script
├── sync_nifty100_to_upstox.py    ← Sync Nifty 100 instruments
├── check_nifty100_status.py      ← Check Nifty 100 status
├── map_from_upstox_file.py       ← Map instruments from Excel
└── ... (other utility scripts)
```

## How to Change Which Script Runs

### Method 1: Update `railway.json` (Recommended)

Edit `railway.json`:

```json
{
  "deploy": {
    "startCommand": "python scripts/run_realtime_alerts.py",
    ...
  }
}
```

**To run a different script**, change the `startCommand` value:
- `python scripts/run_realtime_alerts.py` - One-time alerts
- `python scripts/run_backtest.py` - Backtesting
- `python scripts/run_stock_selection.py` - Stock selection
- etc.

### Method 2: Update `Procfile`

Edit `Procfile`:

```
worker: python scripts/run_realtime_alerts.py
```

**Note**: This only works if `railway.json` doesn't have `startCommand`

### Method 3: Railway Dashboard

1. Go to Railway dashboard
2. Click on your project → service
3. Go to **Settings** tab
4. Find **Start Command** field
5. Enter: `python scripts/run_continuous_alerts.py`
6. Save

**Note**: Dashboard settings override file configurations

## Example: Running Different Scripts

### Example 1: Run Backtest Script

**Update `railway.json`**:
```json
{
  "deploy": {
    "startCommand": "python scripts/run_backtest.py",
    ...
  }
}
```

### Example 2: Run Real-time Alerts for Specific Date

**Update `railway.json`**:
```json
{
  "deploy": {
    "startCommand": "python scripts/run_realtime_alerts.py --date 2025-11-10",
    ...
  }
}
```

### Example 3: Run Multiple Scripts (Advanced)

You can run multiple scripts using a shell script:

**Create `start.sh`**:
```bash
#!/bin/bash
python scripts/run_continuous_alerts.py &
python scripts/run_backtest.py
```

**Update `railway.json`**:
```json
{
  "deploy": {
    "startCommand": "bash start.sh",
    ...
  }
}
```

## Verification

To verify which script Railway is running:

1. **Check Railway Logs**:
   - Go to Railway dashboard
   - Click on your service
   - Go to **Deployments** → Latest → **Logs**
   - Look for the script name in the output

2. **Check Configuration Files**:
   - Look at `railway.json` → `startCommand`
   - Look at `Procfile` → `worker` command

3. **Check Railway Dashboard**:
   - Go to Settings → Start Command
   - See what's configured there

## Best Practices

1. **Use `railway.json`** for explicit configuration
   - More reliable
   - Version controlled
   - Clear and explicit

2. **Keep `Procfile` as backup**
   - Useful if `railway.json` is missing
   - Standard for many platforms

3. **Document which script runs**
   - Add comments in configuration files
   - Update README if needed

4. **Test locally first**
   - Run the script locally before deploying
   - Ensure it works correctly

## Current Configuration Summary

✅ **Railway is configured to run**: `python scripts/run_continuous_alerts.py`

**Configuration files**:
- `railway.json` → `startCommand: "python scripts/run_continuous_alerts.py"`
- `Procfile` → `worker: python scripts/run_continuous_alerts.py`

**Why this script?**
- `run_continuous_alerts.py` is designed for 24/7 operation
- It runs continuously during market hours
- It checks for alerts at scheduled times (9:15:30, 10:15:30, etc.)
- It's the main production script for automated alerts

**Other scripts** are utility scripts:
- `run_realtime_alerts.py` - For one-time alerts (not continuous)
- `run_backtest.py` - For backtesting (not continuous)
- Other scripts - Utility scripts for setup/maintenance

## Troubleshooting

### Script Not Running

1. **Check `railway.json`**:
   ```bash
   cat railway.json
   ```
   Verify `startCommand` is correct

2. **Check `Procfile`**:
   ```bash
   cat Procfile
   ```
   Verify command is correct

3. **Check Railway Dashboard**:
   - Settings → Start Command
   - May override file settings

4. **Check Logs**:
   - Look for error messages
   - Verify script path is correct

### Wrong Script Running

1. **Check priority order**:
   - Railway dashboard settings (highest)
   - `railway.json` → `startCommand`
   - `Procfile` → `worker`

2. **Update the correct file**:
   - If dashboard has setting, update there
   - Otherwise, update `railway.json`

3. **Redeploy**:
   - Push changes to GitHub
   - Railway will redeploy with new configuration

---

**Summary**: Railway knows which script to run from `railway.json` → `startCommand` (or `Procfile` if that doesn't exist). Currently configured to run `python scripts/run_continuous_alerts.py`.

