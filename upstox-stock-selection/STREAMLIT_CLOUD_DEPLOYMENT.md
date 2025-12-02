# Streamlit Cloud Deployment Guide

This guide will help you deploy your Upstox Stock Selection app to Streamlit Cloud (free hosting).

## Prerequisites

1. **GitHub Account**: Your code must be in a GitHub repository
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **Upstox API Credentials**: You'll need your API Key and Access Token

## Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. **Ensure all files are committed and pushed to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Verify these files exist in your repository:**
   - ✅ `app.py` (main Streamlit app)
   - ✅ `requirements.txt` (Python dependencies)
   - ✅ `.streamlit/config.toml` (Streamlit configuration)
   - ✅ `data/NSE.json` (stock symbols data - **IMPORTANT**: Make sure this file is committed)

### Step 2: Create Streamlit Cloud Account

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign in" and authorize with your GitHub account
3. You'll be redirected to your Streamlit Cloud dashboard

### Step 3: Deploy Your App

1. **Click "New app"** button
2. **Select your repository** from the dropdown
3. **Select the branch** (usually `main` or `master`)
4. **Set the main file path**: `app.py`
5. **Click "Deploy"**

### Step 4: Configure Secrets (API Credentials)

**IMPORTANT**: Never commit your API credentials to GitHub!

1. In your Streamlit Cloud app dashboard, click **"⚙️ Settings"** (or "Manage app")
2. Go to **"Secrets"** tab
3. Add your secrets in TOML format:

```toml
UPSTOX_API_KEY = "your_actual_api_key"
UPSTOX_ACCESS_TOKEN = "your_actual_access_token"
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"  # Optional
TELEGRAM_CHAT_ID = "your_telegram_chat_id"  # Optional
MAX_WORKERS = "10"  # Optional
HISTORICAL_DAYS = "30"  # Optional
VERBOSE_LOGGING = "false"  # Optional
```

4. Click **"Save"**

### Step 5: Update Your App to Use Secrets

The app will automatically read secrets from `st.secrets`. Make sure your app uses:

```python
# In app.py, use secrets like this:
api_key = st.secrets.get("UPSTOX_API_KEY", "")
access_token = st.secrets.get("UPSTOX_ACCESS_TOKEN", "")
```

**Note**: The current app.py already supports manual entry, but you can enhance it to use secrets automatically.

### Step 6: Verify Deployment

1. Your app will automatically build and deploy
2. You'll see a URL like: `https://your-app-name.streamlit.app`
3. Open the URL and test your app
4. Check the logs if there are any errors

## Important Notes

### File Paths
- ✅ All file paths in the app use relative paths (e.g., `data/NSE.json`)
- ✅ These work correctly on Streamlit Cloud
- ✅ Make sure `data/NSE.json` is committed to your repository

### Environment Variables
- Streamlit Cloud uses **Secrets** instead of environment variables
- Access them via `st.secrets` in your code
- Never commit secrets to GitHub!

### Resource Limits (Free Tier)
- **Memory**: 1 GB RAM
- **CPU**: Shared resources
- **Storage**: 1 GB
- **Bandwidth**: Reasonable limits
- **Uptime**: Apps sleep after 7 days of inactivity (wake up on first visit)

### Updating Your App
1. Push changes to GitHub
2. Streamlit Cloud automatically detects changes
3. App will rebuild and redeploy automatically
4. You can also manually trigger a rebuild from the dashboard

## Troubleshooting

### App Won't Start
- Check the logs in Streamlit Cloud dashboard
- Verify `requirements.txt` has all dependencies
- Ensure `app.py` is in the root directory

### "No module named X" Error
- Add missing dependencies to `requirements.txt`
- Check the logs for specific missing modules

### API Errors
- Verify secrets are set correctly
- Check if API credentials are valid
- Ensure API keys have proper permissions

### File Not Found Errors
- Make sure `data/NSE.json` is committed to GitHub
- Check file paths are relative (not absolute)
- Verify files exist in the repository

### App is Slow
- Reduce `MAX_WORKERS` in secrets
- Reduce `HISTORICAL_DAYS` for faster analysis
- Consider using fewer symbols

## Custom Domain (Optional)

Streamlit Cloud free tier doesn't support custom domains, but you can:
- Use the provided `*.streamlit.app` domain
- Share the URL with others
- Bookmark for easy access

## Monitoring

- **Logs**: View real-time logs in the Streamlit Cloud dashboard
- **Metrics**: Check app usage and performance
- **Errors**: All errors are logged and visible in the dashboard

## Cost

**Streamlit Cloud is FREE** for public repositories! 🎉

- ✅ Unlimited apps
- ✅ Unlimited deployments
- ✅ Free hosting
- ✅ Automatic HTTPS
- ✅ No credit card required

## Next Steps

1. ✅ Deploy to Streamlit Cloud
2. ✅ Configure secrets
3. ✅ Test your app
4. ✅ Share the URL with others
5. ✅ Monitor usage and logs

## Support

- **Streamlit Cloud Docs**: [docs.streamlit.io/streamlit-community-cloud](https://docs.streamlit.io/streamlit-community-cloud)
- **Streamlit Forum**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Issues**: Report issues in your repository

---

**Happy Deploying! 🚀**

