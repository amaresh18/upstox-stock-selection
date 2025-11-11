# Android APK Build Guide

This guide will help you build an Android APK for the Play Store from your Streamlit web app.

## 📱 Overview

The Android app is a WebView wrapper that loads your Streamlit app from Railway. This approach:
- ✅ Maintains all web app functionality
- ✅ Provides native app experience
- ✅ Easy to update (just update the web app)
- ✅ No need to rebuild APK for web app changes

## 🛠️ Prerequisites

1. **Android Studio** - Download from [developer.android.com](https://developer.android.com/studio)
2. **Java JDK 11 or higher**
3. **Railway URL** - Your deployed Streamlit app URL
4. **Google Play Developer Account** - $25 one-time fee

## 📦 Project Structure

```
android-app/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── java/com/stockselection/
│   │       │   └── MainActivity.java
│   │       ├── res/
│   │       │   ├── layout/
│   │       │   ├── values/
│   │       │   └── mipmap/ (app icons)
│   │       └── AndroidManifest.xml
│   └── build.gradle
├── build.gradle (project level)
└── settings.gradle
```

## 🚀 Quick Start

### Step 1: Open Project in Android Studio

1. Open Android Studio
2. Select "Open an Existing Project"
3. Navigate to the `android-app` folder
4. Wait for Gradle sync to complete

### Step 2: Configure Your Railway URL

1. Open `app/src/main/java/com/stockselection/MainActivity.java`
2. Find the line: `private static final String WEB_URL = "YOUR_RAILWAY_URL_HERE";`
3. Replace with your Railway URL (e.g., `https://your-app.railway.app`)

### Step 3: Customize App Details

1. **App Name**: Edit `app/src/main/res/values/strings.xml`
2. **App Icon**: Replace icons in `app/src/main/res/mipmap-*/`
3. **Package Name**: Update in `app/build.gradle` (must be unique)

### Step 4: Build APK

1. In Android Studio, go to **Build → Build Bundle(s) / APK(s) → Build APK(s)**
2. Wait for build to complete
3. APK will be in `app/build/outputs/apk/debug/app-debug.apk`

### Step 5: Build Release APK (for Play Store)

1. **Generate Keystore**:
   ```bash
   keytool -genkey -v -keystore stock-selection-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias stock-selection
   ```

2. **Configure Signing**:
   - Create `keystore.properties` in project root:
     ```
     storePassword=YOUR_STORE_PASSWORD
     keyPassword=YOUR_KEY_PASSWORD
     keyAlias=stock-selection
     storeFile=../stock-selection-key.jks
     ```

3. **Build Release APK**:
   - In Android Studio: **Build → Generate Signed Bundle / APK**
   - Select **APK**
   - Choose your keystore
   - Build variant: **release**
   - APK will be in `app/build/outputs/apk/release/app-release.apk`

## 📱 Testing

### Test on Device

1. Enable **Developer Options** on your Android device
2. Enable **USB Debugging**
3. Connect device via USB
4. In Android Studio: **Run → Run 'app'**
5. Or install APK directly: `adb install app-debug.apk`

### Test APK

```bash
# Install on connected device
adb install app-debug.apk

# Or transfer APK to device and install manually
```

## 🏪 Play Store Submission

### Step 1: Create Google Play Developer Account

1. Go to [play.google.com/console](https://play.google.com/console)
2. Pay $25 one-time registration fee
3. Complete account setup

### Step 2: Create App Listing

1. Click **"Create app"**
2. Fill in:
   - App name: "Stock Selection" (or your choice)
   - Default language: English
   - App or game: App
   - Free or paid: Free
   - Declarations: Complete all required

### Step 3: Prepare Store Listing

**Required Assets:**
- **App Icon**: 512x512px PNG (no transparency)
- **Feature Graphic**: 1024x500px PNG
- **Screenshots**: 
  - Phone: At least 2 (min 320px, max 3840px)
  - Tablet (optional): At least 2
- **Short Description**: 80 characters max
- **Full Description**: 4000 characters max

**Example Description:**
```
Short: Professional stock selection system with advanced algorithmic analysis

Full:
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

### Step 4: Upload APK/AAB

1. Go to **Production → Create new release**
2. Upload your **signed APK** or **AAB** (recommended)
3. Add **Release notes**
4. Click **Save**

### Step 5: Content Rating

1. Complete the **Content Rating** questionnaire
2. Your app will likely be rated **Everyone** or **Teen**

### Step 6: Privacy Policy

1. Create a privacy policy (required)
2. Host it on your website or use a free service
3. Add URL in **App content → Privacy Policy**

### Step 7: Submit for Review

1. Review all sections (green checkmarks)
2. Click **"Start rollout to Production"**
3. Review process takes 1-7 days typically

## 🔧 Troubleshooting

### Build Errors

**Error: "SDK location not found"**
- Go to **File → Project Structure → SDK Location**
- Set Android SDK location

**Error: "Gradle sync failed"**
- Check internet connection
- Invalidate caches: **File → Invalidate Caches / Restart**

### Runtime Issues

**App shows blank screen:**
- Check Railway URL is correct
- Ensure Railway app is running
- Check internet connection on device

**App crashes:**
- Check AndroidManifest.xml permissions
- Ensure minSdkVersion is compatible with device

## 📝 Important Notes

1. **Keep Keystore Safe**: Store your keystore file securely. You'll need it for all future updates.

2. **Version Code**: Increment `versionCode` in `build.gradle` for each Play Store update.

3. **Version Name**: Update `versionName` (e.g., "1.0.0", "1.0.1") for each release.

4. **Updates**: When you update your Streamlit app on Railway, users will automatically see the new version (no APK update needed).

5. **Offline Mode**: The app requires internet connection to load the Streamlit app.

## 🎨 App Icon Guidelines

- **Size**: 512x512px
- **Format**: PNG (no transparency for Play Store)
- **Design**: Should represent your app clearly
- **Background**: Solid color or gradient
- **Text**: Keep minimal, readable at small sizes

## 📊 Analytics (Optional)

Consider adding:
- **Firebase Analytics**: Track app usage
- **Crashlytics**: Monitor crashes
- **Google Analytics**: Web app analytics

## 🔐 Security

- Never commit keystore files to Git
- Add `*.jks` and `keystore.properties` to `.gitignore`
- Use environment variables for sensitive data

## 📚 Resources

- [Android Developer Guide](https://developer.android.com/guide)
- [Google Play Console Help](https://support.google.com/googleplay/android-developer)
- [Material Design Guidelines](https://material.io/design)

---

**Need Help?** Check the Android Studio documentation or Stack Overflow for specific issues.

