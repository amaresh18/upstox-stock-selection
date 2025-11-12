# Fix Railway Build Error: Railpack vs Nixpacks

## Problem

You're seeing this error:
```
✖ Railpack could not determine how to build the app.
```

This means Railway is using **Railpack** instead of **Nixpacks** to build your Python app.

## Solution

### Option 1: Force Nixpacks in Service Settings (Recommended)

1. **Go to Railway Dashboard**
2. **Click on your service** (the one with the error)
3. **Go to Settings tab**
4. **Look for "Builder" or "Build System"** option
5. **Select "Nixpacks"** (change from Railpack if needed)
6. **Save and redeploy**

### Option 2: Verify railway.json is Being Used

Your `railway.json` already specifies Nixpacks:
```json
{
  "build": {
    "builder": "NIXPACKS"
  }
}
```

**To ensure Railway uses it:**

1. **Check Service Source**:
   - Settings → Source
   - Make sure it's connected to the correct GitHub repo
   - Make sure it's on the `main` branch (or your default branch)

2. **Redeploy**:
   - Go to Deployments tab
   - Click "Redeploy" or push a new commit to trigger deployment

### Option 3: Create nixpacks.toml (If Needed)

If Railway still doesn't detect Python correctly, create `nixpacks.toml` in project root:

```toml
[phases.setup]
nixPkgs = ["python3", "pip"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "python scripts/run_continuous_alerts.py"
```

### Option 4: Check Repository Structure

The error shows:
```
├── Auto-trading-/
├── upstox-stock-selection/
```

This suggests Railway might be looking at a nested directory. 

**Fix:**
1. **Check Service Root Directory**:
   - Settings → Root Directory
   - Should be: `/` (root) or empty
   - If it shows `Auto-trading-/upstox-stock-selection/`, change it to `/`

2. **Verify GitHub Repo Structure**:
   - Your repo should have `requirements.txt` at the root
   - Not nested inside subdirectories

## Quick Checklist

- [ ] Service Settings → Builder = "Nixpacks" (not Railpack)
- [ ] Service Settings → Root Directory = `/` (or empty)
- [ ] Service Settings → Start Command = `python scripts/run_continuous_alerts.py`
- [ ] `railway.json` exists with `"builder": "NIXPACKS"`
- [ ] `requirements.txt` exists at project root
- [ ] Service is connected to correct GitHub repo/branch
- [ ] Redeploy after making changes

## After Fixing

1. **Redeploy the service**:
   - Deployments tab → Click "Redeploy"
   - OR push a new commit to trigger auto-deploy

2. **Check logs**:
   - You should see Nixpacks building:
     ```
     [Nixpacks] Detected Python project
     [Nixpacks] Installing dependencies...
     ```

3. **Verify it works**:
   - Logs should show your script starting
   - No more "Railpack" errors

## Still Having Issues?

1. **Delete and recreate the service**:
   - Sometimes Railway caches the wrong builder
   - Delete the service and create a new one

2. **Check Railway Status**:
   - Sometimes Railway has temporary issues
   - Check https://status.railway.app

3. **Contact Railway Support**:
   - If nothing works, Railway support can help

