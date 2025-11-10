# Alternative Ways to Push to GitHub

## Method 1: GitHub Desktop (Easiest - GUI)

1. **Download GitHub Desktop**:
   - Go to: https://desktop.github.com/
   - Download and install

2. **Connect Repository**:
   - Open GitHub Desktop
   - File → Add Local Repository
   - Select your project folder: `C:\Users\dell\Documents\Amaresh\Auto-trading-\upstox-stock-selection`
   - Click "Add Repository"

3. **Push to GitHub**:
   - Click "Publish repository" (if first time)
   - Or click "Push origin" (if already connected)
   - It will handle authentication automatically

## Method 2: GitHub CLI (gh)

1. **Install GitHub CLI**:
   ```powershell
   winget install GitHub.cli
   ```
   Or download from: https://cli.github.com/

2. **Login**:
   ```powershell
   gh auth login
   ```
   - Select: GitHub.com
   - Select: HTTPS
   - Authenticate: Login with a web browser
   - Follow the prompts

3. **Push**:
   ```powershell
   git push -u origin main
   ```

## Method 3: Use Token in URL (One-time)

1. **Update remote with token**:
   ```powershell
   git remote set-url origin https://amaresh18:YOUR_TOKEN@github.com/amaresh18/upstox-stock-selection.git
   ```

2. **Push**:
   ```powershell
   git push -u origin main
   ```

## Method 4: Use SSH Key

1. **Generate SSH Key** (if you don't have one):
   ```powershell
   ssh-keygen -t ed25519 -C "38761435+amaresh18@users.noreply.github.com"
   ```
   - Press Enter to accept default location
   - Press Enter for no passphrase (or set one)

2. **Copy Public Key**:
   ```powershell
   cat ~/.ssh/id_ed25519.pub
   ```
   Or on Windows:
   ```powershell
   type $env:USERPROFILE\.ssh\id_ed25519.pub
   ```

3. **Add SSH Key to GitHub**:
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Title: "Windows PC" (or any name)
   - Key: Paste the public key
   - Click "Add SSH key"

4. **Update Remote to Use SSH**:
   ```powershell
   git remote set-url origin git@github.com:amaresh18/upstox-stock-selection.git
   ```

5. **Test SSH Connection**:
   ```powershell
   ssh -T git@github.com
   ```
   Should say: "Hi amaresh18! You've successfully authenticated..."

6. **Push**:
   ```powershell
   git push -u origin main
   ```

## Method 5: Use Git Credential Manager (Windows)

1. **Install Git Credential Manager**:
   - Usually comes with Git for Windows
   - Or download: https://github.com/GitCredentialManager/git-credential-manager

2. **Configure**:
   ```powershell
   git config --global credential.helper manager-core
   ```

3. **Push** (will prompt for credentials):
   ```powershell
   git push -u origin main
   ```
   - Username: `amaresh18`
   - Password: Use your Personal Access Token (not GitHub password)

## Method 6: Manual Token Setup

1. **Create a .git-credentials file**:
   ```powershell
   # Create file: C:\Users\dell\.git-credentials
   # Content:
   https://amaresh18:YOUR_TOKEN@github.com
   ```

2. **Configure Git**:
   ```powershell
   git config --global credential.helper store
   ```

3. **Push**:
   ```powershell
   git push -u origin main
   ```

## Method 7: Use Different Remote URL Format

Try using the token in a different format:

```powershell
git remote set-url origin https://github.com/amaresh18/upstox-stock-selection.git
git push https://amaresh18:YOUR_TOKEN@github.com/amaresh18/upstox-stock-selection.git main
```

## Recommended: GitHub Desktop

**Easiest method** - Just download GitHub Desktop and it handles everything:
- ✅ No command line needed
- ✅ Visual interface
- ✅ Automatic authentication
- ✅ Easy to use

## Quick Test

To test if authentication works:

```powershell
# Test with curl
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

Should return your user info if token is valid.

---

**Which method would you like to try?** I recommend GitHub Desktop for the easiest experience, or SSH keys for a permanent solution.

