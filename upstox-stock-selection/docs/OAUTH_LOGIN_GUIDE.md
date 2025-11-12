# Upstox OAuth Login Guide

## Overview

The application now includes a secure OAuth 2.0 login flow for Upstox API authentication, similar to Zerodha Kite's integrated login experience. This eliminates the need to manually copy and paste access tokens.

## Features

- 🔐 **Secure OAuth 2.0 Flow**: Industry-standard authentication
- 🎨 **Zerodha Kite-Inspired UI**: Clean, professional design matching Kite's aesthetic
- 💾 **Multiple Save Options**: Save tokens locally or for Railway deployment
- 📋 **Step-by-Step Instructions**: Clear guidance throughout the process
- 🔄 **Token Exchange**: Automatic code-to-token conversion

## How to Use

### Step 1: Access OAuth Login

1. Open the Streamlit app
2. Navigate to the **API Credentials** section
3. You'll see two tabs:
   - **🔗 OAuth Login**: For secure OAuth authentication
   - **📝 Manual Entry**: For existing tokens

### Step 2: Configure OAuth Settings

In the **OAuth Login** tab, enter:

- **API Key (Client ID)**: Your Upstox API Key
  - Default: `e3d3c1d1-5338-4efa-b77f-c83ea604ea43`
- **API Secret**: Your Upstox API Secret
  - Default: `9kbfgnlibw`
- **Redirect URI**: Must match your Upstox app configuration
  - Default: `https://127.0.0.1`

### Step 3: Generate Authorization URL

1. Click **"🔐 Login with Upstox"** button
2. An authorization URL will be generated and displayed
3. Click the URL (opens in new tab) or copy it manually

### Step 4: Authorize Application

1. You'll be redirected to Upstox login page
2. Enter your Upstox credentials
3. Authorize the application
4. You'll be redirected to: `https://127.0.0.1/?code=XXXXX`
5. **Copy the `code` parameter** from the URL (e.g., `SJwE0P`)

### Step 5: Exchange Code for Token

1. Paste the authorization code in the **"Authorization Code"** field
2. Click **"🔄 Exchange Token"**
3. The app will automatically exchange the code for an access token

### Step 6: Save Token

After successful token exchange, you can:

- **💾 Save to Local File**: Saves to `.env.local` file
- **🚂 Copy for Railway**: Copies formatted variables for Railway deployment
- **🚂 Railway Deployment Instructions**: Expandable guide for Railway setup

## Token Storage

### Local Development

Tokens are saved to:
- **Environment Variables**: Current session only
- **`.env.local` file**: Persistent storage (if you click "Save to Local File")

### Railway Deployment

1. After token generation, click **"🚂 Copy for Railway"**
2. Go to Railway Dashboard → Your Project → Service
3. Click **Variables** tab
4. Add the variables:
   ```
   UPSTOX_API_KEY = your_api_key
   UPSTOX_ACCESS_TOKEN = your_access_token
   ```
5. No quotes needed around values

## Manual Entry (Alternative)

If you already have an access token:

1. Go to **"📝 Manual Entry"** tab
2. Enter your API Key and Access Token
3. Click **"💾 Save Manual Credentials"**

## OAuth Flow Reference

Based on [Upstox API Documentation](https://upstox.com/developer/api-documentation/login):

### Authorization URL Format
```
https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI
```

### Token Exchange Endpoint
```
POST https://api.upstox.com/v2/login/authorization/token
Content-Type: application/x-www-form-urlencoded

code=YOUR_CODE
client_id=YOUR_CLIENT_ID
client_secret=YOUR_CLIENT_SECRET
redirect_uri=YOUR_REDIRECT_URI
grant_type=authorization_code
```

## Troubleshooting

### "Token exchange failed"

- **Check API Secret**: Ensure it matches your Upstox app configuration
- **Check Redirect URI**: Must exactly match the one configured in Upstox
- **Check Code**: Authorization codes expire quickly (usually within minutes)
- **Verify API Key**: Ensure the API Key is correct

### "No access token in response"

- The token exchange was successful but the response format may have changed
- Check the error message for details
- Verify your Upstox app is active and has proper permissions

### Authorization URL not working

- Ensure your Upstox app is configured correctly
- Check that the redirect URI matches exactly
- Verify your API Key is valid

## Security Notes

1. **API Secret**: Never share your API secret publicly
2. **Access Tokens**: Tokens expire after a certain period (check `expires_in` in response)
3. **Local Storage**: `.env.local` file should be in `.gitignore` (already configured)
4. **Environment Variables**: Session-only storage is cleared when the app restarts

## Integration with Existing Code

The OAuth flow integrates seamlessly with existing functionality:

- Tokens saved via OAuth are automatically used for API calls
- Manual entry still works as before
- Environment variables take precedence
- Session state persists tokens during the session

## References

- [Upstox Login API Documentation](https://upstox.com/developer/api-documentation/login)
- [OAuth 2.0 Specification](https://oauth.net/2/)

---

**Last Updated**: OAuth integration added for secure token generation

