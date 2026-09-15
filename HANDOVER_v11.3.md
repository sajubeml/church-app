# Master Handover Document & Flawless Build Guide — v11.3

## 📌 Executive Summary
* **Active Release Version:** **v11.3** (`versionCode 67`)
* **Project Name:** St. Gregorios Orthodox Syrian Church Accounting Application
* **Deployment Targets:**
  - **Android Twin Release APKs:** `St_Gregorios_Church_Accounting_v11.3.apk` (Full) & `St_Gregorios_Church_Accounting_Fresh_v11.3.apk` (Fresh Start)
  - **Desktop Executable:** `St_Gregorios_Church_Accounting.exe`
  - **Web Application / GitHub Pages:** Live at `https://sajubeml.github.io/church-app/` (`church-app` remote)
  - **cPanel Production Web Server:** Files uploaded to `/public_html/accounting/`

---

## 🛠️ Required Build Tools & Environment Variables

| Tool / Dependency | Absolute File Path / Value |
| :--- | :--- |
| **JDK 17 (Java Development Kit)** | `C:\Users\sajub\AppData\Local\JDK17\jdk-17.0.10+7` |
| **Android SDK** | `C:\Users\sajub\AppData\Local\Android\Sdk` |
| **Python 3.11** | System `py` or `python` command |
| **Gradle Wrapper** | `c:\CASHBOOK_APP\android-app\gradlew.bat` |
| **C# Compiler (`csc.exe`)** | `C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe` |

---

## 📁 Key File & Directory Map

```
C:\CASHBOOK_APP\
├── AGENTS.md                          # Mandatory System Rules & Learned Architecture
├── build_all_releases.py              # Master Automated Build Script for Twin Release (Full & Fresh)
├── build_data_js.py                   # Data ingestion script generating data.js
├── build_fresh_start_data.py          # Fresh start dataset generator (data_fresh.js, Individual_fresh.json)
├── build_executable.py                # Compiles St_Gregorios_Church_Accounting.exe launcher
├── copy_assets_to_android.py          # Assets bundler for Android WebViews (full or fresh)
├── app.js                             # Standalone Offline / Android JS Application Logic
├── app_supabase.js                    # Web Application / Supabase JS Application Logic
├── index_offline.html                 # Offline Standalone HTML Template (Copied to index.html in APK)
├── index_supabase.html                # Web Portal HTML Template (Copied to index.html for Web)
├── styles.css                         # Shared CSS Stylesheet
├── data.js                            # Ingested Full Data Bundle
├── data_fresh.js                      # Zeroed Fresh Start Data Bundle
├── data_export/                       # Exported JSON Data Files (Members, Individual, Cash_Book, etc.)
└── android-app/                       # Native Android Studio Project
    ├── build.gradle.kts               # Root Gradle script
    └── app/
        ├── build.gradle.kts           # App Gradle script (versionCode, versionName, namespace)
        └── src/main/
            ├── AndroidManifest.xml    # Native Android Manifest
            ├── assets/                # Web runtime assets (populated by copy_assets_to_android.py)
            └── java/com/stgregorios/churchaccounting/
                ├── MainActivity.kt    # Main Activity & Native WebView Bridge
                └── ChurchDatabaseHelper.kt # Native SQLite Database Engine
```

---

## 📜 Learned Architectural Rules & Constraints

### 1. Mandatory Version Bump Rule
- **Rule:** Every update, patch, fix, or new release **MUST** increment the version (e.g. `v11.3` ➔ `v11.4` / `versionCode 67` ➔ `versionCode 68`).
- **Files to update:**
  1. `android-app/app/build.gradle.kts` (`versionCode = 68`, `versionName = "11.4"`)
  2. `build_all_releases.py` (`v11.4` file output strings)
  3. `index_supabase.html` (`app_supabase.js?v=11.4`)
  4. `index_offline.html` (`app.js?v=11.4`)

### 2. Android Activity Package Resolution Rule
- **Rule:** `namespace` and `applicationId` in `android-app/app/build.gradle.kts` **MUST BE `com.stgregorios.churchaccounting`**.
- **Rule:** `AndroidManifest.xml` must explicitly register: `<activity android:name="com.stgregorios.churchaccounting.MainActivity"`.
- *Why:* If `.MainActivity` is used with a different `namespace`, Gradle manifest merger resolves the class to `com.saju.cashbook.MainActivity`, causing a `ClassNotFoundException` that auto-closes the app immediately on launch.

### 3. Sequential Twin Asset Copy Rule
- **Rule:** Never run `gradlew.bat assembleFullRelease assembleFreshRelease` in a single Gradle call without re-running asset copy in between!
- **Order:**
  1. `py copy_assets_to_android.py full` ➔ `.\gradlew.bat assembleFullRelease`
  2. `py copy_assets_to_android.py fresh` ➔ `.\gradlew.bat assembleFreshRelease`

### 4. Fresh Start User Data Persistence Rule (`CHURCH_FRESH_START_HAS_USER_DATA`)
- In `data_fresh.js`, `window.isFreshStartBuild = true`.
- On initial launch, `loadAllData()` purges native SQLite (`window.AndroidBridge.bulkSync("[]")`) so the app opens with **₹ 0.00** balances.
- Whenever a user restores a JSON backup (`processBackupRestoreData`) or creates a transaction (`showReceiptModal`), the app sets `localStorage.setItem("CHURCH_FRESH_START_HAS_USER_DATA", "true")`.
- This ensures `loadAllData()` permanently retains all imported/entered records across app restarts without wiping them.

---

## 🚀 How to Execute a Flawless Build for Future Versions

To build a new release (e.g. `v11.4`), follow these steps:

1. **Bump Version Numbers**:
   - In `android-app/app/build.gradle.kts`: Set `versionCode = 68` and `versionName = "11.4"`.
   - In `build_all_releases.py`: Change `v11.3` references to `v11.4`.
   - In `index_supabase.html`: Set `<script src="app_supabase.js?v=11.4"></script>`.

2. **Run Master Build Script**:
   ```bash
   py build_all_releases.py
   ```
   *This automatically regenerates `data.js`, builds `St_Gregorios_Church_Accounting.exe`, packages assets, and compiles both `St_Gregorios_Church_Accounting_v11.4.apk` and `St_Gregorios_Church_Accounting_Fresh_v11.4.apk`.*

3. **Stage, Commit, and Push**:
   ```bash
   git add .
   git commit -m "Release v11.4 with automated twin APK build"
   git push origin main
   git push church-app main
   ```

---

## 🎯 Verification Checklist

- [x] Full APK opens cleanly and loads all historical cashbook transactions & ledgers.
- [x] Fresh Start APK opens cleanly with **₹ 0.00** balances and empty cashbook records.
- [x] Restoring a JSON backup file in Fresh Start APK imports all transactions and retains them permanently across restarts.
- [x] Pushed to both `origin` and `church-app` GitHub remotes.
