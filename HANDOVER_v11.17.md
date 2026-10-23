# St. Gregorios Orthodox Syrian Church Accounting Portal
## Release Handover Document — Version 11.17

**Church:** St. Gregorios Orthodox Syrian Church & Pilgrim Centre, Mysuru  
**Workspace Root:** `C:\CASHBOOK_APP`  
**Current Active Version:** **v11.17** (Android `versionCode 80` / Web / Cloud / Offline PC)  
**Date of Release:** October 23, 2026  
**Git Remote Origin:** `https://github.com/sajubeml/Church_account.git` (Main Codebase Backup)  
**Git Remote Church-App:** `https://github.com/sajubeml/church-app.git` (GitHub Pages Live Site)  
**Live GitHub Pages Site:** `https://sajubeml.github.io/church-app/`  
**Live cPanel Web URL:** `https://orthodoxchurchmysore.in/accounting/`  

---

## 1. Release Highlights (v11.17)

### A. Appended OVBS Income to Sunday School in Individual Member Ledgers
- **Background & Requirement:** The parish requested grouping OVBS (Orthodox Vacation Bible School) contributions alongside Sunday School contributions in the **Individual Member Accounts & Ledgers** tab, updating the column header from `Sunday School Day Collection` to `Sunday School / OVBS`.
- **Dynamic Ledger Aggregation:**
  - `findIndividualColKey({ head, code })` updated across both Cloud (`app_supabase.js`) and Offline/Android (`app.js`) to map:
    - Code `RP-3.66` (OVBS)
    - Code `RP-10.14` (Sunday School Day Collection)
    - Code `RP-3.61` (Sunday School)
    - Code `RP-19.22` (Sunday School Cover Collection)
    - Heads containing `sunday school` or `ovbs`
    to Column `Q`.
  - Column `Q` header dynamically renamed and normalized to **`Sunday School / OVBS`** in the DOM table, Excel export, and PDF export.
- **Data Persistence & Backwards Compatibility:**
  - Automatic normalization in `loadAllData()` and `restoreBackup()` ensures that even when loading older monolithic backup files, Column `Q` is seamlessly converted to `Sunday School / OVBS`.
  - Updated `data_export/Individual.json`, `Individual_fresh.json`, and monolithic backup snapshots.
  - Sunday School collection (35 members, ₹5,750.00) and OVBS contributions (23 members / NM, ₹62,000.00) now combine under Column `Q` to a new total of **₹67,750.00**, accurately reflecting every contributing member's balance.

---

## 2. Updated Deliverables in v11.17

| Target Platform | Location / Artifact | Core Code / Asset | Data Source / Connectivity | Deployment Command / Action |
|---|---|---|---|---|
| **Android APK (Full)** | `St_Gregorios_Church_Accounting_v11.17.apk` | `app.js?v=11.17`, `data.js`, `logo_data.js?v=11.17` | Standalone SQLite & LocalStorage | Install APK onto Android phones / tablets |
| **Android APK (Fresh Start)** | `St_Gregorios_Church_Accounting_Fresh_v11.17.apk` | `app.js?v=11.17`, `data_fresh.js` | Fresh dataset with 7-day trial mode | Install fresh-start APK for blank ledger testing |
| **Windows Desktop Launcher** | `St_Gregorios_Church_Accounting.exe` | `index_offline.html`, `app.js?v=11.17` | Local JSON files in `data_export/` | Double-click .exe to launch local Edge app window |
| **GitHub Pages** | `deployment_files/github-supabase/` | `app_supabase.js?v=11.17`, `logo_data.js?v=11.17` | Supabase Cloud PostgreSQL | `git push church-app main` |
| **cPanel Production** | `deployment_files/cpanel/` | `app_supabase.js?v=11.17`, `logo_data.js?v=11.17` | Supabase Cloud PostgreSQL | Upload via cPanel File Manager to `public_html/accounting/` |
| **Offline Portable ZIP** | `St_Gregorios_Church_Accounting_Offline_PC_v11.17.zip` | Bundled standalone distribution suite | Embedded JSON | Unzip and run on offline PC |

---

## 3. Verification & Safety Checks
- **Trial Balance Integrity:** Trial Balance calculation preserves separate account codes (`RP-3.66` for OVBS and `RP-10.14` for Sunday School Day Collection) so that official audited financial statements match the Cash Book source of truth.
- **Zero Loss of Past History:** All historical member subscription dates, voucher records, and multi-split receipts remain intact.
