# Quick Guide: Push to GitHub

## Easiest Method: GitHub Desktop

1. **Download GitHub Desktop**:
   - https://desktop.github.com/
   - Install it

2. **Open GitHub Desktop**:
   - File → Add Local Repository
   - Browse to: `C:\Users\dell\Documents\Amaresh\Auto-trading-\upstox-stock-selection`
   - Click "Add"

3. **Publish Repository**:
   - Click "Publish repository" button
   - Repository name: `upstox-stock-selection`
   - Owner: `amaresh18`
   - Description: "Upstox Stock Selection System"
   - Keep it private (or public)
   - Click "Publish Repository"

**That's it!** GitHub Desktop will handle authentication automatically.

## Alternative: Create Repository First

If the repository doesn't exist on GitHub:

1. **Go to GitHub**:
   - https://github.com/new
   - Repository name: `upstox-stock-selection`
   - Owner: `amaresh18`
   - Don't initialize with README
   - Click "Create repository"

2. **Then push**:
   ```powershell
   git push -u origin main
   ```

## Check Token Permissions

Your token needs `repo` scope. To check:

1. Go to: https://github.com/settings/tokens
2. Find your token
3. Make sure it has `repo` scope checked
4. If not, create a new token with `repo` scope

---

**Recommended**: Use GitHub Desktop - it's the easiest way!

