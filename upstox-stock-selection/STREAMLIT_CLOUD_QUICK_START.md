# Streamlit Cloud Quick Start Guide

## 🚀 Deploy in 5 Minutes

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for Streamlit Cloud deployment"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository
5. Set main file: `app.py`
6. Click **"Deploy"**

### Step 3: Add Secrets
1. In app dashboard, click **"⚙️ Settings"**
2. Go to **"Secrets"** tab
3. Paste this (replace with your actual values):

```toml
UPSTOX_API_KEY = "your_api_key_here"
UPSTOX_ACCESS_TOKEN = "your_access_token_here"
```

4. Click **"Save"**

### Step 4: Wait for Deployment
- Build takes 2-5 minutes
- App URL: `https://your-app-name.streamlit.app`
- Open and test!

## ✅ Pre-Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] `app.py` exists in root directory
- [ ] `requirements.txt` has all dependencies
- [ ] `data/NSE.json` is committed (not in .gitignore)
- [ ] `.streamlit/config.toml` exists
- [ ] API credentials ready for secrets

## 📝 Important Files

Make sure these are in your repository:
- ✅ `app.py` - Main app
- ✅ `requirements.txt` - Dependencies
- ✅ `data/NSE.json` - Stock symbols (required!)
- ✅ `.streamlit/config.toml` - Streamlit config
- ✅ `src/` - All source code
- ✅ `assets/` - CSS files

## 🔒 Security Notes

- ❌ **NEVER** commit API keys to GitHub
- ✅ Use Streamlit Cloud Secrets for credentials
- ✅ Keep `data/NSE.json` in repository (it's safe, no secrets)

## 🆘 Troubleshooting

**App won't start?**
- Check logs in Streamlit Cloud dashboard
- Verify `requirements.txt` is complete
- Ensure `app.py` is in root directory

**"No module named X" error?**
- Add missing package to `requirements.txt`
- Check logs for specific error

**"File not found: data/NSE.json"?**
- Make sure `data/NSE.json` is committed to GitHub
- Check file path is correct

**API errors?**
- Verify secrets are set correctly
- Check API credentials are valid

## 📚 Full Guide

See `STREAMLIT_CLOUD_DEPLOYMENT.md` for detailed instructions.

---

**That's it! Your app is now live on Streamlit Cloud! 🎉**

