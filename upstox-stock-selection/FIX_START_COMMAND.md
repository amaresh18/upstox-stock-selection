# Fix Start Command for Continuous Alerts Service

## Problem

Your continuous alerts service built successfully, but it's using the **Streamlit command** instead of the **alerts script command**.

**Current (Wrong):**
```
streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
```

**Should Be:**
```
python scripts/run_continuous_alerts.py
```

## Quick Fix (2 Minutes)

### Step 1: Open Service Settings

1. **Go to Railway Dashboard**
2. **Click on your continuous alerts service** (the one you just built)
3. **Click "Settings" tab** (top menu)

### Step 2: Update Start Command

1. **Scroll down to "Start Command"** section
2. **Delete the current command** (the Streamlit one)
3. **Enter this command**:
   ```
   python scripts/run_continuous_alerts.py
   ```
4. **Click "Save"** (or "Update")

### Step 3: Verify

1. Railway will **automatically redeploy** after you save
2. **Go to "Deployments" tab**
3. **Watch the new deployment logs**
4. You should see:
   ```
   CONTINUOUS REAL-TIME ALERT MONITORING
   ✅ Credentials found
   ✅ Loaded 100 symbols
   📅 Scheduled check times today:
   ```

## Why This Happened

The `railway.json` file in your repo has the Streamlit command (for Web UI service). When you create a new service, Railway sometimes uses that file. You need to **override it in the service settings**.

## After Fixing

Once the Start Command is updated:

1. ✅ Service will run the alerts script (not Streamlit)
2. ✅ You'll see scheduled check times in logs
3. ✅ Telegram notifications will work (if credentials are set)
4. ✅ Service will check at: 9:15:30, 10:15:30, 11:15:30, etc.

## Still See Streamlit?

If you still see Streamlit logs after updating:

1. **Check you're looking at the right service** (should be named "continuous-alerts")
2. **Verify Start Command** in Settings shows: `python scripts/run_continuous_alerts.py`
3. **Wait for redeploy** to complete (check Deployments tab)
4. **Check latest logs** (not old deployment logs)

---

**That's it!** Once you update the Start Command, your continuous alerts service will run correctly! 🎉

