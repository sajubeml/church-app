# St. Gregorios Orthodox Syrian Church Accounting Portal
## Release Handover Document — Version 11.18

**Church:** St. Gregorios Orthodox Syrian Church & Pilgrim Centre, Mysuru  
**Workspace Root:** `C:\CASHBOOK_APP`  
**Current Active Version:** **v11.18** (Android `versionCode 81` / Web / Cloud / Offline PC)  
**Date of Release:** October 23, 2026  
**Git Remote Origin:** `https://github.com/sajubeml/Church_account.git` (Main Codebase Backup)  
**Git Remote Church-App:** `https://github.com/sajubeml/church-app.git` (GitHub Pages Live Site)  
**Live GitHub Pages Site:** `https://sajubeml.github.io/church-app/`  
**Live cPanel Web URL:** `https://orthodoxchurchmysore.in/accounting/`  

---

## 1. Release Highlights (v11.18)

### A. Integrated "Smart Report Studio" Across All Targets
- **Interactive Multi-Filter Portal:** An in-app ad-hoc reporting studio embedded under the top navigation tab **`📊 Smart Reports`** across Offline Desktop, Online Cloud (Supabase/cPanel/GitHub Pages), and Android APK.
- **Dynamic Filter Controls:**
  - **Quick Presets:** One-click shortcuts for *All Dates*, *Past 30 Days*, *Past 2 Months*, and *Current FY (2026-27)*.
  - **Date Range Selection:** Standard HTML5 `From Date` and `To Date` selectors.
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

### B. Member Directory "Amount Promised" Fix
- **Root Cause Resolution:** Synchronized `masterMembers` array from monolithic backups into `data_export/Members.json` via `build_data_js.py`.
- **Embedded Database Updates:** Re-compiled `data.js` so that `window.CHURCH_DATA.members` contains Column `F` (`Amount Promised`) for all 111 member records (108 members with promised pledges).
- **Auto-Enrichment on Load:** Added startup routines in both `app.js` and `app_supabase.js` that check the browser's `localStorage` (`CHURCH_MASTER_MEMBERS`) and immediately enrich Column `F` if missing, ensuring promised amounts display immediately upon page reload without requiring manual cache clears or re-importing.

---

## 2. Updated Deliverables in v11.18

| Target Platform | Location / Artifact | Core Code / Asset | Data Source / Connectivity | Deployment Command / Action |
|---|---|---|---|---|
| **Android APK (Full)** | `St_Gregorios_Church_Accounting_v11.18.apk` | `app.js?v=11.18`, `data.js`, `logo_data.js?v=11.18` | Standalone SQLite & LocalStorage | Install APK onto Android phones / tablets |
| **Android APK (Fresh Start)** | `St_Gregorios_Church_Accounting_Fresh_v11.18.apk` | `app.js?v=11.18`, `data_fresh.js` | Fresh dataset with 7-day trial mode | Install fresh-start APK for blank ledger testing |
| **Windows Desktop Launcher** | `St_Gregorios_Church_Accounting.exe` | `index_offline.html`, `app.js?v=11.18` | Local JSON files in `data_export/` | Double-click .exe to launch local Edge app window |
| **GitHub Pages** | `deployment_files/github-supabase/` | `app_supabase.js?v=11.18`, `logo_data.js?v=11.18` | Supabase Cloud PostgreSQL | `git push church-app main` |
| **cPanel Production** | `deployment_files/cpanel/` | `app_supabase.js?v=11.18`, `logo_data.js?v=11.18` | Supabase Cloud PostgreSQL | Upload via cPanel File Manager to `public_html/accounting/` |
| **Offline Portable ZIP** | `St_Gregorios_Church_Accounting_Offline_PC_v11.18.zip` | Bundled standalone distribution suite | Embedded JSON | Unzip and run on offline PC |

---

## 3. Audit & Safety Verification
- **Zero Disruption to Existing Ledger Logic:** Cashbook balances, multi-split transactions, voucher sequence counters, individual member ledger dynamic computations, trial balance arithmetic, and balance sheet sums remain completely untouched and identical to previous releases.
- **Safe Read-Only Querying:** All Smart Report filtering executes against read-only in-memory copies without mutating `state.cashbook`.
