# GitHub Push Instructions

## Current Issue

The repository is configured to push to: `https://github.com/amaresh18/upstox-stock-selection`

However, there's an authentication issue - your system is trying to authenticate as `gajawadaamaresh18` instead of `amaresh18`.

## Solutions

### Option 1: Use Personal Access Token (Recommended)

1. **Create a Personal Access Token**:
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Give it a name (e.g., "upstox-stock-selection")
   - Select scopes: `repo` (full control of private repositories)
   - Click "Generate token"
   - **Copy the token** (you won't see it again!)

2. **Push using the token**:
   ```bash
   git push https://YOUR_TOKEN@github.com/amaresh18/upstox-stock-selection.git main
   ```
   
   Replace `YOUR_TOKEN` with your personal access token.

### Option 2: Use GitHub CLI

If you have GitHub CLI installed:

```bash
gh auth login
git push -u origin main
```

### Option 3: Update Git Credentials

1. **Clear cached credentials**:
   ```bash
   git credential-manager-core erase
   ```
   
   Or on Windows:
   ```powershell
   git credential-manager erase
   ```

2. **Push again** - it will prompt for credentials:
   ```bash
   git push -u origin main
   ```
   
   When prompted:
   - Username: `amaresh18`
   - Password: Use your Personal Access Token (not your GitHub password)

### Option 4: Use SSH with Correct Key

1. **Generate a new SSH key** (if needed):
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. **Add SSH key to GitHub**:
   - Copy the public key: `cat ~/.ssh/id_ed25519.pub`
   - Go to GitHub → Settings → SSH and GPG keys → New SSH key
   - Paste the key and save

3. **Update SSH config** (if needed):
   ```bash
   # Edit ~/.ssh/config
   Host github.com-amaresh18
     HostName github.com
     User git
     IdentityFile ~/.ssh/id_ed25519
   ```

4. **Update remote**:
   ```bash
   git remote set-url origin git@github.com-amaresh18:amaresh18/upstox-stock-selection.git
   git push -u origin main
   ```

## Quick Fix (Temporary)

If you just want to push once, you can use:

```bash
git push https://amaresh18@github.com/amaresh18/upstox-stock-selection.git main
```

It will prompt for a password - use your Personal Access Token.

## Verify Repository Exists

Make sure the repository exists at: https://github.com/amaresh18/upstox-stock-selection

If it doesn't exist:
1. Go to GitHub
2. Click "New repository"
3. Name it: `upstox-stock-selection`
4. Don't initialize with README (since we're pushing existing code)
5. Create the repository
6. Then push using one of the methods above

## Current Status

- ✅ Remote URL set to: `https://github.com/amaresh18/upstox-stock-selection.git`
- ✅ All files committed locally
- ❌ Push blocked due to authentication issue

## After Successful Push

Once pushed, you can:
- Deploy to Railway (it will auto-detect from GitHub)
- Share the repository
- Set up CI/CD

---

**Note**: Never commit sensitive data (API keys, tokens, passwords) to GitHub. They're already in `.gitignore`.

