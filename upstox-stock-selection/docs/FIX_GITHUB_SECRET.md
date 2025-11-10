# Fix GitHub Secret Detection Issue

## Problem

GitHub detected a secret (GitHub Personal Access Token) in the file `UpstoxTokenGen.txt` in commit `7bf905e`. This is blocking all pushes.

## Solution Options

### Option 1: Allow Secret via GitHub (Quickest - Recommended)

1. **Go to this URL**:
   https://github.com/amaresh18/upstox-stock-selection/security/secret-scanning/unblock-secret/35IqBA3b3pdNw8g7sbgiehz6GVH

2. **Click "Allow secret"** button

3. **Then push again**:
   ```powershell
   git push
   ```

**Note**: This allows the secret in that specific commit. The file is already removed from current commits.

### Option 2: Remove from Git History (Cleaner)

If you want to completely remove the secret from history:

1. **Install git-filter-repo** (if not installed):
   ```powershell
   pip install git-filter-repo
   ```

2. **Remove the file from all history**:
   ```powershell
   git filter-repo --path UpstoxTokenGen.txt --invert-paths --force
   ```

3. **Force push**:
   ```powershell
   git push --force
   ```

**Warning**: This rewrites git history. Only do this if you're the only one working on the repo.

### Option 3: Create Fresh Repository

If the above doesn't work:

1. Create a new repository on GitHub
2. Push only the current code (without history):
   ```powershell
   git checkout --orphan new-main
   git add .
   git commit -m "Initial commit - Upstox Stock Selection System"
   git remote set-url origin https://github.com/amaresh18/upstox-stock-selection.git
   git push -u origin new-main --force
   ```

## Current Status

- ✅ File `UpstoxTokenGen.txt` removed from current commits
- ✅ Added to `.gitignore`
- ✅ Build fixes pushed (runtime.txt, nixpacks.toml)
- ❌ Push blocked due to secret in old commit (7bf905e)

## Recommended Action

**Use Option 1** - It's the quickest and the file is already removed from current code. The secret in the old commit won't affect new deployments.

---

After allowing the secret, Railway deployment should work! 🚀

