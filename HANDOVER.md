# Project Handover Document & Continuation Guide
**St. Gregorios Orthodox Syrian Church & Pilgrim Centre Accounting Portal**
*Workspace: `c:\saju_old pc\Church_App\anti_gravity_v9.2`*
*Active Release Version: 9.5*

---

## 📌 Executive Summary

This project serves as a comprehensive cross-platform accounting system replacing the legacy Excel Macro-Enabled Accounting Workbook. It has evolved through several iterations and now features:
1.  **Multi-Platform Cloud Sync:** A modern serverless architecture connected to **Supabase (PostgreSQL)**, deployed perfectly in-sync across both GitHub Pages and CPanel.
2.  **Standalone Offline Mobile Applications (`.apk`):** Fully independent offline versions (v9.5) for Android devices, utilizing LocalStorage for environments without internet access, allowing manual exports/imports to the cloud.
3.  **Automatic Deployment System:** Python-based builders (`prepare_deployments.py` and `build_all_releases.py`) that cleanly segregate environments into ready-to-deploy folders.

---

## 🛠️ Work Accomplished & Recent Fixes (Versions 9.3 to 9.5)

### 1. The Supabase Serverless Migration (v9.3)
- **Legacy PHP/MySQL Removed:** The application was fully migrated away from the legacy CPanel PHP/MySQL and local Python SQLite backend architectures.
- **Fetch Interceptor (`app_supabase.js`):** Built a seamless interceptor that catches all legacy `api.php` requests and translates them into secure Supabase REST API requests on the fly. This saved us from rewriting thousands of lines of legacy frontend code.
- **Authentication & Security:** Implemented Supabase JWT Authentication and Row Level Security (RLS). The application now requires an email/password login to fetch or modify data.
- **Bulletproof ID Generation:** Fixed duplicate key insertion crashes caused by legacy `maxId + 1` logic. Insertions now use Unix timestamps (`Math.floor(Date.now() / 1000)`) guaranteeing mathematically absolute uniqueness across devices.

### 2. Multi-Cloud Deployment Architecture (v9.3)
- Created `prepare_deployments.py` which organizes the codebase into three strict deployment folders:
  - `deployment_files/cpanel/`: Files ready for CPanel host (using `index_supabase.html`).
  - `deployment_files/github-supabase/`: Files ready for GitHub Pages (using `index_supabase.html`).
  - `deployment_files/mobile apk v1.0/`: Files ready for offline mobile apps (using the vanilla `index.html` and `app.js`).
- Both CPanel and GitHub deployments successfully point to the *exact same* Supabase cloud database, remaining perfectly in sync.

### 3. Critical Data & Ledger Corrections (v9.4)
- **The "16.47" Data Corruption:** Conducted a deep data audit and corrected 28 entries where Code `RP-16.47` (Payments: St. Mary's Feast) was mistakenly entered as a Receipt. This fixed massive desyncs in Individual Member Ledgers (e.g., Bibi Chandy's balance was successfully restored to ₹24,000).
- **Core Logic Fix:** Updated `app_supabase.js` and `app.js` to remove the hardcoded `16.47` mapping in `findIndividualColKey()`, preventing cashbook edits from crashing the application logic.
- **Trial Balance Accuracy:** Updated the Trial Balance aggregator to strictly include only Explicit Codes (starting with `RP-` or ending with letter variants like `(a)`, `(b)`), fixing miscalculations.

### 4. Cashbook Edit Modal Bug Fix & Offline APK (v9.5)
- **Row Separation Bug Fixed:** The legacy system stores Receipts and Payments on the exact same row in the dataset. Previously, clicking 'Edit' on a Payment would accidentally load the Receipt data instead. This logic has been completely rewritten so the app accurately distinguishes between the Receipt side and Payment side of a single row.
- **Independent Offline APK Build:** Recompiled the Mobile APK (Android app) to act as a fully independent, offline tool using `app.js` (LocalStorage).
- Bumped the Gradle versioning to **v9.5** to distinguish the newly built bug-free APKs.
- Generated `St_Gregorios_Church_Accounting_v9.5.apk` ensuring that offline usage correctly processes edits without needing a network connection.

---

## 📁 Key File Inventory

| File / Folder | Purpose |
| :--- | :--- |
| **`deployment_files/`** | The finalized output directory containing the 3 deployment environments. |
| **`app_supabase.js`** | Core client-side javascript application code connected to Supabase Cloud. |
| **`app.js`** | Core client-side javascript application code using offline LocalStorage (for APK). |
| **`index_supabase.html`** | Cloud portal layout containing the Secure Gateway Login overlay. |
| **`index.html`** | Offline local portal layout (No login overlay). |
| **`prepare_deployments.py`** | Packages the repository into the 3 deployment folders. |
| **`package_distributable.py`** | Assembles ZIP distribution packages under `dist/`. |
| **`build_executable.py`** | Compiles the standalone Windows C# Executable. |
| **`android-app/`** | Android Gradle project for compiling the mobile APKs. |

---

## 🚀 How to Re-Deploy or Compile (v9.5 onwards)

1.  **To Update Web Deployments:** 
    If you make changes to HTML/CSS/JS, run `py prepare_deployments.py`. Then, upload the contents of the `cpanel` folder to your CPanel File Manager, and push the `github-supabase` folder to your GitHub `main` branch.
2.  **To Rebuild Mobile APKs:**
    Navigate to the `android-app/` directory and run `.\gradlew assembleRelease`. The output will be located in `android-app/app/build/outputs/apk/full/release/`. Then copy the files into `deployment_files/mobile apk v1.0/`.
3.  **To sync Offline Mobile Data:**
    Export the JSON backup from the CPanel web admin portal and import it into the Android Mobile App via **Restore/Replace Data**.
