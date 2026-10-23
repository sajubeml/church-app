# St. Gregorios Orthodox Syrian Church Accounting Portal
## Master Handover Document & System Architecture Guide (v11.19)

**Church:** St. Gregorios Orthodox Syrian Church & Pilgrim Centre, Mysuru  
**Workspace Root:** `C:\CASHBOOK_APP`  
**Current Active Version:** **v11.19** (Android `versionCode 82` / Web / Cloud / Offline PC)  
**Date of Release:** October 23, 2026  
**Git Remote Origin:** `https://github.com/sajubeml/Church_account.git` (Main Codebase Backup)  
**Git Remote Church-App:** `https://github.com/sajubeml/church-app.git` (GitHub Pages Live Site)  
**Live GitHub Pages Site:** `https://sajubeml.github.io/church-app/`  
**Live cPanel Web URL:** `https://orthodoxchurchmysore.in/accounting/`  

---

## 1. Executive Summary & Purpose

The **St. Gregorios Church Accounting Portal** is an all-in-one financial accounting software suite custom-built for St. Gregorios Orthodox Syrian Church & Pilgrim Centre, Mysuru. It completely replaces legacy Excel macro workbooks with a reliable, zero-spillover accounting system supporting:

1. **Multi-Target Synchronized Deployment:**
   - **Local Offline PC:** Standalone Windows desktop launcher (`St_Gregorios_Church_Accounting.exe` + `index.html` + `app.js`).
   - **Android Mobile Application:** Standalone native APK with embedded WebView SQLite/LocalStore (`St_Gregorios_Church_Accounting_v11.19.apk`).
   - **Cloud cPanel Web Portal:** `https://orthodoxchurchmysore.in/accounting/` (Apache/cPanel).
   - **GitHub Pages:** `https://sajubeml.github.io/church-app/` (Static Cloud Mirror).
   - **Cloud PostgreSQL DB:** Supabase cloud database synchronization (`app_supabase.js`).

2. **The "Cashbook-Brain" Single Source of Truth:**
   - All financial balances, Individual Member Ledgers, Trial Balance sheets, and Subscription Upto validity dates are computed dynamically on the fly from the Cash Book (`cashbook` array). Manual edits to ledger balance cells are ignored in favor of real cashbook transaction entries.

3. **Strict A5 Portrait Laser Print Engine:**
   - Zero-spillover receipt card formatting (`height: 172mm !important; margin: 6mm;`) ensuring Original and Office Copy fit strictly across 2 pages without overflow on standard laser printers (e.g., Canon LBP2900 / HP LaserJet).

---

## 2. Release Highlights (v11.18 — October 23, 2026)

### A. Integrated "Smart Report Studio" Across All Targets
- **Interactive Multi-Filter Portal:** An in-app ad-hoc reporting studio embedded under the top navigation tab **`📊 Smart Reports`** across Offline Desktop, Online Cloud (Supabase/cPanel/GitHub Pages), and Android APK.
- **Dynamic Filter Controls:**
  - **Quick Presets:** One-click shortcuts for *All Dates*, *Past 30 Days*, *Past 2 Months*, and *Current FY (2026-27)*.
  - **Date Range Selection:** Standard HTML5 `From Date` and `To Date` selectors with automatic date format normalization (`YYYY-MM-DD`, `DD-MM-YYYY`, `DD/MM/YYYY`).
  - **Flow Type Filter:** Filter by *Receipts (Income)*, *Payments (Expenses)*, or *All Entries*.
  - **Payment Mode:** Filter by *Cash*, *Bank / Online*, or *Combined*.
  - **Account Head & RP Code Dropdown:** Dynamic, sorted selection of all church accounts.
  - **Keyword Particulars Search:** Real-time search across remarks, member names, account heads, and notes (e.g. `candle cup`, `ovbs`, `calendar`).
  - **Member / Contributor Filter:** Filter for specific registered parish members (`Reg #1` to `Reg #128`) or non-members (`NM`).
- **3 Presentation Layout Modes:**
  1. **Detailed Transaction Register (Chronological):** Complete journal listing with Date, Flow (IN/OUT), Doc #, Reg #, Contributor Name, Account Head, RP Code, Remarks, Cash, Bank, and Total.
  2. **Member-wise Summary:** Automatically groups and aggregates all transactions per person with count of entries, subtotal cash, subtotal bank, and grand total.
  3. **Account Head-wise Summary:** Groups and aggregates by RP Code and Head title with entry counts and total amounts.
- **Live KPI Metric Cards:** Real-time summary tiles showing *Matching Entries Count*, *Total Cash (₹)*, *Total Bank / Online (₹)*, and *Combined Grand Total (₹)*.
- **Exporting Options:** Full export to branded Excel spreadsheet (`.xlsx`) and print-ready PDF statement (`exportTableToPDF`) with church letterhead.

### B. Member Directory "Amount Promised" Fix & Auto-Enrichment
- **Root Cause Resolution:** Synchronized `masterMembers` array from monolithic backups into `data_export/Members.json` via `build_data_js.py`.
- **Embedded Database Updates:** Re-compiled `data.js` so that `window.CHURCH_DATA.members` contains Column `F` (`Amount Promised`) for all 111 member records (108 members with promised pledges).
- **Auto-Enrichment on Load:** Added startup routines in both `app.js` and `app_supabase.js` that check the browser's `localStorage` (`CHURCH_MASTER_MEMBERS`) and immediately enrich Column `F` if missing, ensuring promised amounts display immediately upon page reload without requiring manual cache clears or re-importing.

### C. Sunday School / OVBS Dynamic Column Merging (v11.17)
- `findIndividualColKey({ head, code })` updated in both Cloud (`app_supabase.js`) and Offline/Android (`app.js`) to route `RP-3.66` (OVBS), `RP-10.14` (Sunday School Day Collection), `RP-3.61` (Sunday School), and `RP-19.22` directly into Column `Q`.
- Column `Q` header renamed to **`Sunday School / OVBS`** in the DOM table, Excel export, and PDF export.

### D. Digital Signature Integration (v11.16)
- Vicar / Trustee signature digitally extracted and embedded as `window.CHURCH_SIGNATURE_BASE64` in `logo_data.js`, ensuring self-contained offline rendering with zero `Tainted canvas` errors during PDF export.

---

## 3. Current Deliverables & Artifact Locations (v11.18)

| Target / Distribution | File / Path | Size | Description |
| :--- | :--- | :--- | :--- |
| **Android APK (Full Release)** | [`St_Gregorios_Church_Accounting_v11.18.apk`](file:///C:/CASHBOOK_APP/St_Gregorios_Church_Accounting_v11.18.apk) | 9.20 MB | Offline standalone Android APK with full parish data (`versionCode 81`) |
| **Android APK (Fresh Start)** | [`St_Gregorios_Church_Accounting_Fresh_v11.18.apk`](file:///C:/CASHBOOK_APP/St_Gregorios_Church_Accounting_Fresh_v11.18.apk) | 9.13 MB | Clean start APK for new financial years / fresh installs (`versionCode 81`) |
| **Android APK (Root Default)** | [`St_Gregorios_Church_Accounting.apk`](file:///C:/CASHBOOK_APP/St_Gregorios_Church_Accounting.apk) | 9.20 MB | Copy of Full Release APK |
| **Windows Desktop Launcher** | [`St_Gregorios_Church_Accounting.exe`](file:///C:/CASHBOOK_APP/St_Gregorios_Church_Accounting.exe) | 13 KB | Native C# launcher (launches server on `http://localhost:8088/`) |
| **Offline PC Bundle (ZIP)** | [`St_Gregorios_Church_Accounting_Offline_PC_v11.18.zip`](file:///C:/CASHBOOK_APP/St_Gregorios_Church_Accounting_Offline_PC_v11.18.zip) | 0.86 MB | Minimal offline Windows bundle for pen drive transfer |
| **cPanel 1-Click ZIP** | [`cpanel_update_v11.18.zip`](file:///C:/CASHBOOK_APP/cpanel_update_v11.18.zip) | 0.95 MB | Complete package ready to extract in cPanel File Manager |
| **cPanel Raw Folder** | [`deployment_files/cpanel/`](file:///C:/CASHBOOK_APP/deployment_files/cpanel) | ~2.1 MB | Uncompressed files for direct upload to `/public_html/accounting` |
| **GitHub Pages** | [`deployment_files/github-supabase/`](file:///C:/CASHBOOK_APP/deployment_files/github-supabase) | ~2.1 MB | Served live at `https://sajubeml.github.io/church-app/` |

---

## 4. Standard Operating Procedure (SOP) for Future Updates

Whenever making changes, patches, or releasing new versions, **strictly follow this sequence**:

### Step 1: Mandatory Version Increment (Rule 13)
Before compiling or releasing, increment the version string and `versionCode`:
1. `android-app/app/build.gradle.kts`: update `versionCode = XX`, `versionName = "11.X"`
2. `build_all_releases.py`: update `full_apk_v11` and `fresh_apk_v11` target filenames
3. `create_offline_zip.py`: update `zip_name_v11` and README text
4. `index_supabase.html`: update `<script src="app_supabase.js?v=11.X"></script>`
5. `index_offline.html`: update `<script src="app.js?v=11.X"></script>`
6. Root `index.html`: keep identical to `index_supabase.html`

### Step 2: Multi-Target Code Synchronization (Rule 16)
If adding new features or modifying HTML/JS logic:
- Code changes in `app.js` must be mirrored in `app_supabase.js`.
- HTML structure changes in `index_offline.html` must be mirrored in `index_supabase.html` and copied to root `index.html`.
- Run `py prepare_deployments.py` to refresh the `deployment_files/` subfolders.

### Step 3: Execute Single Master Build Command (Rule 14)
Run from the workspace root:
```powershell
py build_all_releases.py
```
This automated master pipeline runs:
1. `build_data_js.py` & `build_fresh_start_data.py` (ingests latest backup and generates `data.js`)
2. `build_executable.py` (builds `St_Gregorios_Church_Accounting.exe`)
3. `copy_assets_to_android.py full` -> executes Gradle `assembleFullRelease`
4. `copy_assets_to_android.py fresh` -> executes Gradle `assembleFreshRelease`
5. Copies all built APKs to root and `/dist/`

### Step 4: Package Offline Windows Bundle
Run:
```powershell
py create_offline_zip.py
```
Produces `St_Gregorios_Church_Accounting_Offline_PC_v11.X.zip` (standalone Windows offline package).

### Step 5: Git Commit & Dual Remote Push (Rule 8)
Always push to BOTH Git remotes:
```powershell
git add -A
git commit -m "Release v11.X: <summary of changes>"
git push origin main
git push church-app main
```
- `origin` backs up the main source repository.
- `church-app` triggers instant deployment to the live GitHub Pages website (`https://sajubeml.github.io/church-app/`).

### Step 6: Deploy to cPanel (If Web Hosting Updated)
1. Open cPanel File Manager -> `public_html/accounting/`.
2. Upload `cpanel_update_v11.X.zip` and extract (or upload modified files from `deployment_files/cpanel/`).

---

## 5. Summary of Key Build Scripts

- **`build_all_releases.py`**: Compiles data bundles, builds desktop `.exe`, and executes sequential Gradle builds for Full & Fresh Android APKs.
- **`build_data_js.py`**: Automatically discovers the latest monolithic backup (`St_Gregorios_Church_Backup_YYYY-MM-DD.json`) from `Downloads/`, sanitizes contra codes, auto-calculates trial balances, updates `Members.json` (Amount Promised), and writes `data.js`.
- **`prepare_deployments.py`**: Refreshes distinct deployment folders (`cpanel/`, `github-supabase/`, `mobile apk v1.0/`).
- **`create_offline_zip.py`**: Packages the minimal standalone offline PC ZIP distribution.
- **`copy_assets_to_android.py full|fresh`**: Prepares isolated Android asset bundles for Gradle build flavors.
