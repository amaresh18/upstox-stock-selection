# Upstox API Credentials Setup

## Current Credentials

**API Key**: `e3d3c1d1-5338-4efa-b77f-c83ea604ea43`

**Access Token**: `eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIzUUFSVEoiLCJqdGkiOiI2OTEyNDg5YjQ3ODQ3MjdlNWY4YjIyYWIiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2MjgwNTkxNSwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYyODEyMDAwfQ.EG-kDo3g1G5u5Cl_HrnBo612vvYNwASV8KNZd3XHoiA`

**API Secret**: `9kbfgnlibw` (not currently used by scripts, kept for reference)

## How to Set Credentials

### Method 1: PowerShell Script (Easiest)

Run the setup script:

```powershell
.\scripts\set_credentials.ps1
```

This sets the credentials for the current PowerShell session.

### Method 2: Manual PowerShell (Current Session)

```powershell
$env:UPSTOX_API_KEY='e3d3c1d1-5338-4efa-b77f-c83ea604ea43'
$env:UPSTOX_ACCESS_TOKEN='eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIzUUFSVEoiLCJqdGkiOiI2OTEyNDg5YjQ3ODQ3MjdlNWY4YjIyYWIiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2MjgwNTkxNSwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYyODEyMDAwfQ.EG-kDo3g1G5u5Cl_HrnBo612vvYNwASV8KNZd3XHoiA'
```

### Method 3: Permanent Windows Environment Variables

1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to **Advanced** tab → **Environment Variables**
3. Under **User variables**, click **New**
4. Add:
   - Variable name: `UPSTOX_API_KEY`
   - Variable value: `e3d3c1d1-5338-4efa-b77f-c83ea604ea43`
5. Click **New** again:
   - Variable name: `UPSTOX_ACCESS_TOKEN`
   - Variable value: `eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIzUUFSVEoiLCJqdGkiOiI2OTEyNDg5YjQ3ODQ3MjdlNWY4YjIyYWIiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2MjgwNTkxNSwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYyODEyMDAwfQ.EG-kDo3g1G5u5Cl_HrnBo612vvYNwASV8KNZd3XHoiA`
6. Restart PowerShell/terminal for changes to take effect

### Method 4: For Railway Deployment

1. Go to Railway dashboard
2. Click on your project → service
3. Go to **Variables** tab
4. Add:
   - `UPSTOX_API_KEY` = `e3d3c1d1-5338-4efa-b77f-c83ea604ea43`
   - `UPSTOX_ACCESS_TOKEN` = `eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIzUUFSVEoiLCJqdGkiOiI2OTEyNDg5YjQ3ODQ3MjdlNWY4YjIyYWIiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2MjgwNTkxNSwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYyODEyMDAwfQ.EG-kDo3g1G5u5Cl_HrnBo612vvYNwASV8KNZd3XHoiA`

## Verify Credentials Are Set

```powershell
# Check if credentials are set
if ($env:UPSTOX_API_KEY -and $env:UPSTOX_ACCESS_TOKEN) {
    Write-Host "✅ Credentials are set"
} else {
    Write-Host "❌ Credentials not set"
}
```

## Important Notes

1. **API Secret**: The API secret (`9kbfgnlibw`) is not currently used by the scripts. Only API key and access token are required.

2. **Access Token Expiry**: Access tokens expire after a certain period. If you get authentication errors, you may need to generate a new access token from Upstox.

3. **Security**: 
   - Never commit credentials to git (they're in `.gitignore`)
   - Don't share credentials publicly
   - Use environment variables or secure storage

4. **Session Scope**: 
   - PowerShell environment variables set with `$env:` are only for the current session
   - To make them permanent, use Windows Environment Variables (Method 3)

## Quick Start

After setting credentials, you can run any script:

```powershell
# Set credentials (if not already set)
.\scripts\set_credentials.ps1

# Run continuous alerts
python scripts/run_continuous_alerts.py

# Run real-time alerts for specific date
python scripts/run_realtime_alerts.py --date 2025-11-10

# Run backtest
python scripts/run_backtest.py
```

## Troubleshooting

### Credentials Not Found

**Error**: `❌ Error: UPSTOX_API_KEY and UPSTOX_ACCESS_TOKEN must be set`

**Solution**: 
1. Run `.\scripts\set_credentials.ps1` in PowerShell
2. Or set them manually using Method 2 above
3. Verify with: `echo $env:UPSTOX_API_KEY`

### Access Token Expired

**Error**: `401 Unauthorized` or `Invalid token`

**Solution**: 
1. Generate a new access token from Upstox Developer Dashboard
2. Update the `UPSTOX_ACCESS_TOKEN` environment variable
3. Restart the script

---

**Last Updated**: Credentials configured as of current setup

