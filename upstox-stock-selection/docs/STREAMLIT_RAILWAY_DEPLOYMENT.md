# Deploy Streamlit UI to Railway

## Overview

This guide explains how to deploy the Streamlit Stock Selection UI to Railway so it's accessible as a web application.

## Prerequisites

- ✅ Code pushed to GitHub
- ✅ Railway account (free tier available)
- ✅ Upstox API credentials

## Step 1: Update Railway Configuration

The following files have been configured for Streamlit:

### `railway.json`
```json
{
  "deploy": {
    "startCommand": "streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true"
  }
}
```

### `Procfile`
```
web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
```

## Step 2: Deploy to Railway

### Option A: New Deployment (Recommended)

1. **Go to Railway Dashboard**: https://railway.app
2. **Create New Service** (or use existing project)
3. **Deploy from GitHub**:
   - Select "Deploy from GitHub repo"
   - Choose your repository: `upstox-stock-selection`
   - Railway will auto-detect the configuration

### Option B: Update Existing Deployment

1. **Go to your Railway project**
2. **Settings → Start Command**:
   - Update to: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
   - Or Railway will use `railway.json` automatically

## Step 3: Set Environment Variables

In Railway dashboard → **Variables** tab, add:

### Required:
```
UPSTOX_API_KEY = your_api_key_here
UPSTOX_ACCESS_TOKEN = your_access_token_here
```

### Optional:
```
TELEGRAM_BOT_TOKEN = your_bot_token (for notifications)
TELEGRAM_CHAT_ID = your_chat_id (for notifications)
```

**Note**: No quotes needed around values in Railway

## Step 4: Deploy

1. **Push to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Configure Streamlit for Railway deployment"
   git push
   ```

2. **Railway will automatically deploy** when you push, or:
   - Click **"Deploy"** button in Railway dashboard
   - Watch the **"Deployments"** tab for progress

## Step 5: Access Your Web App

1. **After deployment completes**, Railway will provide:
   - A public URL (e.g., `https://your-app.railway.app`)
   - Or you can set a custom domain

2. **Open the URL** in your browser
   - The Streamlit UI will be accessible
   - You can configure parameters and run analysis

## Step 6: Verify It's Working

1. **Check Railway Logs**:
   - Go to **Deployments** → Latest → **Logs**
   - You should see:
     ```
     You can now view your Streamlit app in your browser.
     Network URL: http://0.0.0.0:PORT
     ```

2. **Test the UI**:
   - Open the Railway-provided URL
   - You should see the Stock Selection UI
   - Enter API credentials
   - Test the "Load Defaults" button
   - Run an analysis

## Important Notes

### Port Configuration
- Railway provides a `$PORT` environment variable
- Streamlit is configured to use this port automatically
- The app listens on `0.0.0.0` to accept external connections

### Headless Mode
- `--server.headless true` prevents Streamlit from trying to open a browser
- Required for cloud deployment

### Environment Variables
- API credentials are set in Railway dashboard
- The UI will read them automatically
- Users can also enter them manually in the UI

### Data Files
- `data/NSE.json` must be committed to GitHub
- It's already in the repository for Railway to access

## Troubleshooting

### App Not Loading
1. Check Railway logs for errors
2. Verify environment variables are set
3. Ensure `data/NSE.json` exists in the repository
4. Check that port is correctly configured

### Import Errors
1. Verify all dependencies in `requirements.txt`
2. Check Railway build logs
3. Ensure Python version is compatible

### Connection Issues
1. Verify Railway service is running (not paused)
2. Check the public URL is correct
3. Try accessing from a different network

## Switching Between Scripts

If you want to switch back to the continuous alerts script:

**Update `railway.json`**:
```json
{
  "deploy": {
    "startCommand": "python scripts/run_continuous_alerts.py"
  }
}
```

**Or update `Procfile`**:
```
worker: python scripts/run_continuous_alerts.py
```

## Cost

- **Free Tier**: 500 hours/month (enough for ~20 days of 24/7 operation)
- **Paid Plans**: Start at $5/month for unlimited hours

## Next Steps

1. ✅ Deploy to Railway
2. ✅ Access the web UI
3. ✅ Configure parameters
4. ✅ Run stock selection analysis
5. ✅ Share the URL with team members (optional)

