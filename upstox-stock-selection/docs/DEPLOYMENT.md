# Deployment Guide

This guide consolidates all deployment-related documentation.

## Railway Deployment

### Quick Start

1. **Create Railway Account**
   - Sign up at [railway.app](https://railway.app)

2. **Deploy from GitHub**
   - Connect your GitHub repository
   - Railway will auto-detect the project

3. **Configure Environment Variables**
   - `UPSTOX_API_KEY`: Your Upstox API key
   - `UPSTOX_ACCESS_TOKEN`: Your Upstox access token
   - `TELEGRAM_BOT_TOKEN`: (Optional) Telegram bot token
   - `TELEGRAM_CHAT_ID`: (Optional) Telegram chat ID

4. **Deploy Services**
   - **Web Service**: Uses `Procfile` web command (Streamlit UI)
   - **Worker Service**: Uses `Procfile` worker command (Continuous alerts)

### Railway Configuration

The `Procfile` defines two services:
```
web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
worker: python scripts/run_continuous_alerts.py
```

### Troubleshooting

- **Port Issues**: Railway automatically sets `$PORT` - don't hardcode ports
- **Build Failures**: Check `requirements.txt` and `runtime.txt`
- **Memory Issues**: Railway free tier has limits - monitor usage

For detailed Railway setup, see:
- `docs/RAILWAY_DEPLOYMENT.md` - Full Railway deployment guide
- `docs/RAILWAY_TROUBLESHOOTING.md` - Common issues and solutions

## Cloud Deployment (General)

See `docs/CLOUD_DEPLOYMENT.md` for general cloud deployment strategies.

## OAuth Setup

See `docs/OAUTH_LOGIN_GUIDE.md` for Upstox OAuth configuration.

## Telegram Notifications

See `docs/TELEGRAM_SETUP.md` for Telegram bot setup.

