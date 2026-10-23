# St. Gregorios Orthodox Syrian Church Accounting Portal
## Release Handover Document — Version 11.19

**Church:** St. Gregorios Orthodox Syrian Church & Pilgrim Centre, Mysuru  
**Workspace Root:** `C:\CASHBOOK_APP`  
**Current Active Version:** **v11.19** (Android `versionCode 82` / Web / Cloud / Offline PC)  
**Date of Release:** October 23, 2026  
**Git Remote Origin:** `https://github.com/sajubeml/Church_account.git` (Main Codebase Backup)  
**Git Remote Church-App:** `https://github.com/sajubeml/church-app.git` (GitHub Pages Live Site)  
**Live GitHub Pages Site:** `https://sajubeml.github.io/church-app/`  
**Live cPanel Web URL:** `https://orthodoxchurchmysore.in/accounting/`  

---

## 1. Release Highlights (v11.19)

### A. Streamlined Navigation: Decommissioned Redundant "Trial Balance" Tab
- **Background & Requirement:** The user requested removing the legacy Trial Balance tab and sheet, as the comprehensive **📑 Balance Sheet** (`tabBalanceSheet`) dynamically calculates all period financial statements (Opening Balances, Receipts by RP Code, Payments by RP Code, Closing Balances, and Net Surplus/Deficit) with date-range filtering, making the separate Trial Balance tab redundant.
- **UI & DOM Optimization:**
  - Removed `<button class="nav-tab" data-tab="tabTrialBalance">⚖️ Trial Balance</button>` from the navigation bar across `index_offline.html`, `index_supabase.html`, and root `index.html`.
  - Removed `<div class="tab-pane" id="tabTrialBalance">...</div>` from all HTML templates.
  - Reduced navigation clutter, allowing cleaner horizontal panning on tablet, desktop, and mobile displays.
- **Preservation of Internal Accounting Data:**
  - `state.trialBalance` is safely retained in the in-memory state engine so that opening cash/bank baseline extraction in `calculateCashbookTotals()` and master account heads discovery remain 100% operational.
  - `renderTrialBalance()` gracefully guards against the missing DOM elements via `if (!tbody) return;`, maintaining complete backward compatibility.

---

## 2. Updated Deliverables in v11.19

| Target Platform | Location / Artifact | Core Code / Asset | Data Source / Connectivity | Deployment Command / Action |
|---|---|---|---|---|
| **Android APK (Full)** | `St_Gregorios_Church_Accounting_v11.19.apk` | `app.js?v=11.19`, `data.js`, `logo_data.js?v=11.19` | Standalone SQLite & LocalStorage | Install APK onto Android phones / tablets |
| **Android APK (Fresh Start)** | `St_Gregorios_Church_Accounting_Fresh_v11.19.apk` | `app.js?v=11.19`, `data_fresh.js` | Fresh dataset with 7-day trial mode | Install fresh-start APK for blank ledger testing |
| **Windows Desktop Launcher** | `St_Gregorios_Church_Accounting.exe` | `index_offline.html`, `app.js?v=11.19` | Local JSON files in `data_export/` | Double-click .exe to launch local Edge app window |
| **GitHub Pages** | `deployment_files/github-supabase/` | `app_supabase.js?v=11.19`, `logo_data.js?v=11.19` | Supabase Cloud PostgreSQL | `git push church-app main` |
| **cPanel Production** | `deployment_files/cpanel/` | `app_supabase.js?v=11.19`, `logo_data.js?v=11.19` | Supabase Cloud PostgreSQL | Upload via cPanel File Manager to `public_html/accounting/` |
| **Offline Portable ZIP** | `St_Gregorios_Church_Accounting_Offline_PC_v11.19.zip` | Bundled standalone distribution suite | Embedded JSON | Unzip and run on offline PC |

---

## 3. Verification & Safety Checks
- **Balance Sheet Integrity:** The Balance Sheet tab (`tabBalanceSheet`) remains the primary balanced statement controller, computing all Debit and Credit items with zero variance.
- **Smart Report Studio:** Fully active under `📊 Smart Reports` for detailed transaction queries, member contribution summaries, and account head breakdowns.
- **All Core Accounting Functions Intact:** Cash book entries, voucher generation, member directory with promised amounts, and PDF/Excel export modules are 100% functional.
