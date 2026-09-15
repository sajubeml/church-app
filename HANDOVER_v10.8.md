# St. Gregorios Orthodox Syrian Church Accounting Portal
## Handover Document — Release v10.8 (Offline Standalone & Supabase Cloud Sync)

**Date:** September 9, 2026  
**Repository:** `c:\saju_old pc\Church_App\anti_gravity_v9.2`  
**Git Remote Origin:** `https://github.com/sajubeml/Church_account.git`  
**Git Remote Church-App (GitHub Pages):** `https://github.com/sajubeml/church-app.git` (Live at: `https://sajubeml.github.io/church-app/`)

---

### 1. Executive Summary

All components of the accounting application have been updated and synchronized across all deployment targets:
1. **Online Supabase Cloud Web App** (GitHub Pages & cPanel)
2. **Offline Standalone Web App** (`index_offline.html` running locally in any browser without internet or web server)
3. **Offline Standalone Android APK** (`St_Gregorios_Church_Accounting_v10.8.apk` / `St_Gregorios_Church_Accounting.apk`)
4. **Fresh Start Trial APK** (`St_Gregorios_Church_Accounting_Fresh_v10.8.apk`)

---

### 2. What Was Added & Resolved

#### A. Synchronous Church Logo Embedding (100% Self-Contained Receipts & Vouchers)
- **Problem:** When receipts or vouchers were printed, saved to `Receipts/` or uploaded to Supabase Storage (`receipts/*.html`), the logo image source previously relied on an asynchronous `fetch('church_logo.png')` call. In sandboxed browsers, cross-origin GitHub Pages, local file protocols (`file:///`), or inside Supabase cloud storage buckets, relative paths failed, causing broken `[Church Logo]` images.
- **Solution:** 
  - Generated `logo_data.js` declaring `window.CHURCH_LOGO_BASE64` containing the full PNG Base64 Data URI.
  - Placed `logo_data.js` in:
    - Project Root
    - `deployment_files/github-supabase/logo_data.js`
    - `deployment_files/cpanel/logo_data.js`
    - `android-app/app/src/main/assets/logo_data.js`
  - Updated `saveReceiptPrintCopy` and `downloadReceiptHtml` in all JS files (`app_supabase.js`, `app.js`, and Android assets `app.js`) to replace any `church_logo` image tags with `window.CHURCH_LOGO_BASE64`.
  - Every downloaded or archived receipt is now **100% self-contained** and can be viewed anywhere on any device or printed without external network dependencies.

#### B. Offline Standalone Web App (`index_offline.html`)
- Updated script inclusions:
  ```html
  <script src="logo_data.js?v=10.8"></script>
  <script src="data.js?v=3.6"></script>
  <script src="app.js?v=10.8"></script>
  ```
- Works completely offline using `localStorage` and `data.js`.

#### C. Android APKs Rebuilt & Packaged (v10.8)
- Updated `copy_assets_to_android.py` to bundle `logo_data.js` into Android assets.
- Cleanly compiled both release flavors using Gradle:
  - `assembleFullRelease` (Offline full historical data version)
  - `assembleFreshRelease` (Fresh start 7-day trial version)
- Output APKs placed in the project root:
  - `St_Gregorios_Church_Accounting_v10.8.apk` (~9.5 MB)
  - `St_Gregorios_Church_Accounting.apk` (Root default)
  - `St_Gregorios_Church_Accounting_Fresh_v10.8.apk` (~9.5 MB)

---

### 3. Print Engine & Formatting Standards

- **Paper Size:** A5 Portrait (`@page { size: A5 portrait; margin: 6mm; }`)
- **Dual-Card Layout:** 
  - Page 1: **ORIGINAL** (`height: 180mm !important; padding: 5mm 7mm;`)
  - Page 2: **OFFICE COPY / DUPLICATE**
  - Outer borders clear laser printer 5mm hardware margins; no 3rd-page spillover.
- **Preview & Format Switcher:** Allows toggling between `A5 Portrait`, `A5 Landscape`, and `A4 Landscape` in real time before triggering `window.print()`.

---

### 4. Git Deployment Status

| Commit | Details | Remotes Pushed |
| :--- | :--- | :--- |
| `e696b14` | Synchronous Base64 logo embedding in Supabase cloud receipts and HTML downloads | `origin main`, `church-app main` |
| Latest | Build and package v10.8 offline standalone web app and APKs | `origin main`, `church-app main` |
