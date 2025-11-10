# Railway Root Directory Configuration Fix

## Problem

Railway is analyzing the wrong directory. The logs show:

```
The app contents that Railpack analyzed contains:
./
├── Auto-trading-/
├── upstox-stock-selection/  ← Your project is here
├── README.md
└── project-structure.md
```

Railway is looking at the repository root, but your project files (`Procfile`, `requirements.txt`, etc.) are inside `upstox-stock-selection/`.

## Solution: Configure Root Directory in Railway Dashboard

You **MUST** configure the root directory in Railway's dashboard. This cannot be done via `railway.json`.

### Steps:

1. **Go to Railway Dashboard**
   - Navigate to [railway.app](https://railway.app)
   - Log in to your account

2. **Select Your Project**
   - Click on your project (e.g., `upstox-stock-selection`)

3. **Select Your Service**
   - Click on the service that's failing to build

4. **Go to Settings Tab**
   - Click on the **"Settings"** tab in the service

5. **Find "Source" or "Root Directory" Setting**
   - Look for a setting called **"Source"**, **"Root Directory"**, or **"Working Directory"**
   - This is usually under the "Source" section

6. **Set Root Directory**
   - Enter: `upstox-stock-selection`
   - Or: `./upstox-stock-selection`
   - Save the changes

7. **Redeploy**
   - Railway should automatically trigger a new deployment
   - Or manually trigger a redeploy from the "Deployments" tab

## Alternative: Move Files to Repository Root

If you prefer not to configure the root directory, you can move all project files to the repository root:

1. Move `Procfile`, `requirements.txt`, `runtime.txt` to the repository root
2. Move `scripts/` and `src/` directories to the repository root
3. Update any paths in your code if needed
4. Commit and push changes

## Verification

After setting the root directory, Railway should see:

```
./
├── Procfile
├── requirements.txt
├── runtime.txt
├── scripts/
├── src/
└── ...
```

Instead of:

```
./
├── Auto-trading-/
├── upstox-stock-selection/
├── README.md
└── project-structure.md
```

## Why This Happens

Railway analyzes the repository root by default. If your project is in a subdirectory (monorepo structure), you need to tell Railway which directory to use as the service root.

## Still Having Issues?

If Railway still can't find the files after setting the root directory:

1. Check that the root directory path is correct (case-sensitive)
2. Verify that `Procfile` and `requirements.txt` exist in that directory
3. Check Railway logs for any new error messages
4. Contact Railway support or post on [Railway Help Station](https://station.railway.com/)

