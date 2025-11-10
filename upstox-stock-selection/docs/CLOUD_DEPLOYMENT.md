# Cloud Deployment Guide

This guide explains how to deploy the Upstox Stock Selection system to the cloud so it can run 24/7 without requiring your laptop to be on.

## Why Deploy to Cloud?

- ✅ **24/7 Availability**: Runs continuously without your laptop
- ✅ **No Power Consumption**: Saves electricity
- ✅ **Reliable**: Cloud services have high uptime
- ✅ **Accessible**: Monitor from anywhere
- ✅ **Cost-Effective**: Many free tier options available

## Deployment Options

### Option 1: Railway (Recommended - Free Tier Available)

**Railway** offers a free tier with 500 hours/month and is very easy to use.

#### Steps:

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo" (or "Empty Project")

3. **Configure Environment Variables**
   - Go to Project Settings → Variables
   - Add these variables:
     ```
     UPSTOX_API_KEY=your_api_key
     UPSTOX_ACCESS_TOKEN=your_access_token
     TELEGRAM_BOT_TOKEN=your_bot_token (optional)
     TELEGRAM_CHAT_ID=your_chat_id (optional)
     MAX_WORKERS=10
     HISTORICAL_DAYS=30
     ```

4. **Create `Procfile`** (in project root):
   ```
   worker: python scripts/run_continuous_alerts.py
   ```

5. **Create `railway.json`** (optional, for better configuration):
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

6. **Deploy**
   - Railway will automatically detect Python and install dependencies
   - The script will start running automatically

**Cost**: Free tier includes 500 hours/month (enough for 24/7 for ~20 days)

---

### Option 2: Render (Free Tier Available)

**Render** offers a free tier with some limitations.

#### Steps:

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New" → "Web Service"
   - Connect your GitHub repository

3. **Configure Settings**
   - **Name**: `upstox-alerts`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python scripts/run_continuous_alerts.py`
   - **Plan**: Free (or paid for 24/7)

4. **Add Environment Variables**
   - Go to Environment section
   - Add all required variables (same as Railway)

5. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy automatically

**Note**: Free tier spins down after 15 minutes of inactivity. For 24/7, you need a paid plan ($7/month) or use a background worker.

**For 24/7 on Free Tier**: Use "Background Worker" instead of "Web Service"

---

### Option 3: Fly.io (Free Tier Available)

**Fly.io** offers a generous free tier.

#### Steps:

1. **Install Fly CLI**
   ```bash
   # Windows (PowerShell)
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   
   # Mac/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create `fly.toml`** (in project root):
   ```toml
   app = "upstox-alerts"
   primary_region = "bom"  # Mumbai region (closer to India)
   
   [build]
   
   [env]
     UPSTOX_API_KEY = "your_api_key"
     UPSTOX_ACCESS_TOKEN = "your_access_token"
     TELEGRAM_BOT_TOKEN = "your_bot_token"
     TELEGRAM_CHAT_ID = "your_chat_id"
   
   [[services]]
     internal_port = 8080
     processes = ["app"]
     protocol = "tcp"
     script_checks = []
   
   [processes]
     app = "python scripts/run_continuous_alerts.py"
   ```

3. **Deploy**
   ```bash
   fly auth login
   fly launch
   fly deploy
   ```

**Cost**: Free tier includes 3 shared-cpu-1x VMs with 256MB RAM

---

### Option 4: AWS EC2 (Free Tier - 12 Months)

**AWS EC2** offers a free tier for 12 months.

#### Steps:

1. **Create AWS Account**
   - Go to [aws.amazon.com](https://aws.amazon.com)
   - Sign up (requires credit card, but free tier is free)

2. **Launch EC2 Instance**
   - Go to EC2 Dashboard
   - Click "Launch Instance"
   - Choose: **Amazon Linux 2023** or **Ubuntu**
   - Instance type: **t2.micro** (free tier eligible)
   - Configure security group (allow SSH on port 22)

3. **Connect to Instance**
   ```bash
   ssh -i your-key.pem ec2-user@your-instance-ip
   ```

4. **Install Dependencies**
   ```bash
   # For Amazon Linux
   sudo yum update -y
   sudo yum install python3 git -y
   
   # For Ubuntu
   sudo apt update
   sudo apt install python3 python3-pip git -y
   ```

5. **Clone and Setup**
   ```bash
   git clone <your-repo-url>
   cd upstox-stock-selection
   pip3 install -r requirements.txt
   ```

6. **Create Systemd Service** (for auto-start)
   ```bash
   sudo nano /etc/systemd/system/upstox-alerts.service
   ```
   
   Add this content:
   ```ini
   [Unit]
   Description=Upstox Stock Selection Alerts
   After=network.target
   
   [Service]
   Type=simple
   User=ec2-user
   WorkingDirectory=/home/ec2-user/upstox-stock-selection
   Environment="UPSTOX_API_KEY=your_api_key"
   Environment="UPSTOX_ACCESS_TOKEN=your_access_token"
   Environment="TELEGRAM_BOT_TOKEN=your_bot_token"
   Environment="TELEGRAM_CHAT_ID=your_chat_id"
   ExecStart=/usr/bin/python3 scripts/run_continuous_alerts.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

7. **Start Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable upstox-alerts
   sudo systemctl start upstox-alerts
   sudo systemctl status upstox-alerts
   ```

**Cost**: Free for 12 months (t2.micro), then ~$8-10/month

---

### Option 5: Google Cloud Run (Pay Per Use)

**Cloud Run** charges only when the service is running.

#### Steps:

1. **Create `Dockerfile`** (in project root):
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   CMD ["python", "scripts/run_continuous_alerts.py"]
   ```

2. **Deploy to Cloud Run**
   ```bash
   # Install gcloud CLI first
   gcloud run deploy upstox-alerts \
     --source . \
     --platform managed \
     --region asia-south1 \
     --set-env-vars UPSTOX_API_KEY=your_key,UPSTOX_ACCESS_TOKEN=your_token \
     --min-instances 1 \
     --max-instances 1
   ```

**Cost**: Pay per use, but minimum 1 instance = ~$5-10/month

---

### Option 6: Heroku (Paid - $7/month)

**Heroku** is simple but requires a paid plan for 24/7.

#### Steps:

1. **Install Heroku CLI**
   ```bash
   # Download from heroku.com/cli
   ```

2. **Create `Procfile`**:
   ```
   worker: python scripts/run_continuous_alerts.py
   ```

3. **Deploy**
   ```bash
   heroku login
   heroku create upstox-alerts
   heroku config:set UPSTOX_API_KEY=your_key
   heroku config:set UPSTOX_ACCESS_TOKEN=your_token
   git push heroku main
   heroku ps:scale worker=1
   ```

**Cost**: $7/month for 24/7 dyno

---

## Recommended: Railway (Easiest) or AWS EC2 (Most Reliable)

### Quick Comparison

| Service | Free Tier | 24/7 Free | Ease of Use | Best For |
|---------|-----------|-----------|-------------|----------|
| **Railway** | ✅ 500 hrs/month | ⚠️ Partial | ⭐⭐⭐⭐⭐ | Beginners |
| **Render** | ✅ Limited | ❌ No | ⭐⭐⭐⭐ | Simple apps |
| **Fly.io** | ✅ Generous | ✅ Yes | ⭐⭐⭐ | Docker users |
| **AWS EC2** | ✅ 12 months | ✅ Yes | ⭐⭐⭐ | Production |
| **Cloud Run** | ✅ $300 credit | ✅ Yes | ⭐⭐ | Serverless |
| **Heroku** | ❌ No | ❌ No | ⭐⭐⭐⭐⭐ | Simple (paid) |

---

## Security Best Practices

1. **Never commit secrets to Git**
   - Use environment variables
   - Add `.env` to `.gitignore`

2. **Use Secret Management**
   - Railway/Render: Built-in environment variables
   - AWS: Use Secrets Manager or Parameter Store
   - Fly.io: `fly secrets set KEY=value`

3. **Rotate Tokens Regularly**
   - Update access tokens every 30-60 days
   - Update environment variables in cloud platform

---

## Monitoring

### Check if Script is Running

**Railway/Render/Fly.io:**
- Check logs in dashboard
- Look for "Checking for alerts..." messages

**AWS EC2:**
```bash
ssh into instance
sudo systemctl status upstox-alerts
journalctl -u upstox-alerts -f  # View logs
```

### Telegram Notifications

The script will send Telegram notifications when alerts are detected, so you'll know it's working even if you can't access the server.

---

## Troubleshooting

### Script Stops Running

1. **Check Logs**: Look for errors in cloud platform logs
2. **Restart Service**: Most platforms auto-restart, but you can manually restart
3. **Check Environment Variables**: Ensure all required variables are set
4. **Check API Limits**: Upstox API may have rate limits

### High Memory Usage

- Reduce `MAX_WORKERS` environment variable
- Process fewer symbols at once

### Network Issues

- Ensure cloud instance has internet access
- Check firewall rules allow outbound HTTPS (443)

---

## Next Steps

1. Choose a platform (recommend Railway for beginners)
2. Set up account and project
3. Configure environment variables
4. Deploy and monitor
5. Test with Telegram notifications

---

## Support

If you encounter issues:
1. Check platform-specific documentation
2. Review logs for error messages
3. Verify environment variables are set correctly
4. Test locally first to ensure script works

