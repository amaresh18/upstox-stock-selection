# Android APK Build Guide

Complete guide to build and publish your Stock Selection app on Google Play Store.

## 📱 Overview

Your Streamlit app can be packaged as an Android APK using a WebView wrapper. This approach:
- ✅ Maintains all web functionality
- ✅ Provides native app experience
- ✅ Easy updates (just update web app)
- ✅ No rebuild needed for web changes

## 🚀 Quick Start

### Option 1: Use Android Studio (Recommended)

1. **Download Android Studio**
   - Visit [developer.android.com/studio](https://developer.android.com/studio)
   - Install Android Studio

2. **Open Project**
   - Open Android Studio
   - Select "Open an Existing Project"
   - Navigate to `android-app` folder
   - Wait for Gradle sync

3. **Configure Railway URL**
   - Open `app/src/main/java/com/stockselection/MainActivity.java`
   - Replace `WEB_URL` with your Railway URL:
     ```java
     private static final String WEB_URL = "https://your-app.railway.app";
     ```

4. **Build APK**
   - **Build → Build Bundle(s) / APK(s) → Build APK(s)**
   - APK location: `app/build/outputs/apk/debug/app-debug.apk`

### Option 2: Command Line Build

```bash
cd android-app
./gradlew assembleDebug
```

APK will be in: `app/build/outputs/apk/debug/app-debug.apk`

## 🔐 Build Signed Release APK (For Play Store)

### Step 1: Generate Keystore

```bash
keytool -genkey -v -keystore stock-selection-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias stock-selection
```

**Important**: Save the password and keystore file securely!

### Step 2: Configure Signing

1. Create `keystore.properties` in `android-app/`:
   ```
   storePassword=YOUR_STORE_PASSWORD
   keyPassword=YOUR_KEY_PASSWORD
   keyAlias=stock-selection
   storeFile=../stock-selection-key.jks
   ```

2. Update `app/build.gradle` to include signing config (see full example in README)

### Step 3: Build Release APK

In Android Studio:
- **Build → Generate Signed Bundle / APK**
- Select **APK**
- Choose keystore
- Build variant: **release**

Or command line:
```bash
./gradlew assembleRelease
```

## 📱 Testing

### Install on Device

1. Enable Developer Options on Android device
2. Enable USB Debugging
3. Connect via USB
4. Run: `adb install app-debug.apk`

Or transfer APK to device and install manually.

## 🏪 Play Store Submission

### Prerequisites

1. **Google Play Developer Account**
   - Visit [play.google.com/console](https://play.google.com/console)
   - Pay $25 one-time registration fee
   - Complete account setup

2. **App Assets**
   - App Icon: 512x512px PNG
   - Feature Graphic: 1024x500px PNG
   - Screenshots: At least 2 (phone), optional tablet
   - Privacy Policy URL (required)

### Submission Steps

1. **Create App**
   - Go to Play Console
   - Click "Create app"
   - Fill in app details

2. **Store Listing**
   - App name: "Stock Selection"
   - Short description (80 chars max)
   - Full description (4000 chars max)
   - Upload screenshots
   - Upload app icon and feature graphic

3. **Upload APK/AAB**
   - Go to **Production → Create new release**
   - Upload signed APK or AAB
   - Add release notes
   - Save

4. **Content Rating**
   - Complete questionnaire
   - Likely rated "Everyone" or "Teen"

5. **Privacy Policy**
   - Create privacy policy
   - Host on website
   - Add URL in App content

6. **Submit**
   - Review all sections
   - Click "Start rollout to Production"
   - Wait 1-7 days for review

## 📝 App Store Listing Example

### Short Description (80 chars)
```
Professional stock selection system with advanced algorithmic analysis
```

### Full Description
```
Stock Selection System is a professional algorithmic trading platform that helps you identify high-probability trading opportunities using advanced technical analysis.

Features:
• Real-time stock analysis with multiple timeframes
• Volume-based breakout/breakdown detection
• Customizable trading parameters
• Historical data analysis
• Professional trading dashboard
• Export results to CSV

Perfect for traders who want to:
- Identify breakout and breakdown opportunities
- Analyze volume patterns
- Backtest trading strategies
- Monitor multiple stocks simultaneously

Built with professional-grade algorithms and designed with a clean, modern interface inspired by leading trading platforms.
```

## 🔧 Troubleshooting

### Build Issues

**SDK not found:**
- File → Project Structure → SDK Location
- Set Android SDK path

**Gradle sync failed:**
- Check internet connection
- File → Invalidate Caches / Restart

### Runtime Issues

**Blank screen:**
- Check Railway URL is correct
- Ensure Railway app is running
- Check device internet connection

**App crashes:**
- Check AndroidManifest.xml permissions
- Verify minSdkVersion compatibility

## ⚠️ Important Notes

1. **Keystore Security**: Store keystore file securely. Required for all updates.

2. **Version Updates**: 
   - Increment `versionCode` in `build.gradle` for each update
   - Update `versionName` (e.g., "1.0.0" → "1.0.1")

3. **Web Updates**: When you update Streamlit app on Railway, users see changes automatically (no APK update needed).

4. **Offline Mode**: App requires internet to load Streamlit app.

## 📚 Additional Resources

- [Android Developer Guide](https://developer.android.com/guide)
- [Google Play Console Help](https://support.google.com/googleplay/android-developer)
- [Material Design](https://material.io/design)

---

**Need Help?** Check the `android-app/README.md` for detailed instructions.

