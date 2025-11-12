# Railway Port Configuration for Web UI Service

## Port Configuration

### How It Works

The **port number is NOT hardcoded** - Railway automatically provides it via the `$PORT` environment variable.

### Where It's Configured

**1. Procfile** (Primary Configuration):
```
web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
```

**2. Railway Service Settings** (If you set Start Command manually):
```
streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
```

### How Railway Assigns Ports

1. **Railway automatically sets `$PORT`** when your service starts
2. **Port is assigned dynamically** (usually between 3000-8000, but Railway manages it)
3. **You don't need to specify a number** - just use `$PORT`
4. **Railway routes traffic** from the public URL to your service's port automatically

### What You See in Logs

When Streamlit starts, you'll see:
```
You can now view your Streamlit app in your browser.

Network URL: http://0.0.0.0:8080
```

The actual port number (e.g., `8080`) is assigned by Railway and may vary.

### Important Notes

✅ **DO NOT hardcode a port number** - Always use `$PORT`
- ❌ Wrong: `--server.port 8080`
- ✅ Correct: `--server.port $PORT`

✅ **`--server.address 0.0.0.0`** is required
- This allows Railway to route external traffic to your service
- Without this, the service won't be accessible from outside

✅ **Railway handles port routing automatically**
- You don't need to configure port forwarding
- Railway's public URL automatically routes to your service's port

### Finding Your Port Number

**Method 1: Check Railway Logs**
1. Go to Railway Dashboard → Your Web UI Service
2. Go to **Deployments** → Latest → **Logs**
3. Look for: `Network URL: http://0.0.0.0:XXXX`
4. The number after `:` is your port

**Method 2: Check Environment Variables**
1. Railway Dashboard → Service → **Variables** tab
2. Look for `PORT` variable (Railway sets this automatically)
3. You can't edit it - Railway manages it

**Method 3: Check Service Settings**
1. Railway Dashboard → Service → **Settings**
2. Look for port configuration (usually shows as `$PORT`)

### For Continuous Alerts Service

The **worker service** (continuous alerts) does NOT need a port:
- It's a background worker, not a web service
- No public URL needed
- No port configuration required

### Troubleshooting

**Problem: "Port already in use"**
- Railway manages ports automatically
- This shouldn't happen on Railway
- If you see this, check if you hardcoded a port number

**Problem: "Can't access web UI"**
- Check that `--server.address 0.0.0.0` is set
- Verify service is running (not paused)
- Check Railway logs for port binding errors

**Problem: "Service not accessible"**
- Ensure service type is "web" (not "worker")
- Check that Railway assigned a public domain
- Verify `$PORT` is being used (not a hardcoded number)

---

## Summary

- **Port**: Automatically assigned by Railway via `$PORT` environment variable
- **Configuration**: `--server.port $PORT` in Procfile or Start Command
- **Address**: `--server.address 0.0.0.0` (required for external access)
- **You don't need to know the exact port number** - Railway handles everything!

