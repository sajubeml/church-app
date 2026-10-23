# St. Gregorios Orthodox Syrian Church Accounting Portal
## Release Handover Document — Version 11.20

**Church:** St. Gregorios Orthodox Syrian Church & Pilgrim Centre, Mysuru  
**Workspace Root:** `C:\CASHBOOK_APP`  
**Current Active Version:** **v11.20** (Android `versionCode 83` / Web / Cloud / Offline PC)  
**Date of Release:** October 23, 2026  
**Git Remote Origin:** `https://github.com/sajubeml/Church_account.git` (Main Codebase Backup)  
**Git Remote Church-App:** `https://github.com/sajubeml/church-app.git` (GitHub Pages Live Site)  
**Live GitHub Pages Site:** `https://sajubeml.github.io/church-app/`  
**Live cPanel Web URL:** `https://orthodoxchurchmysore.in/accounting/`  

---

## 1. Release Highlights (v11.20)

### A. Cash in Hand & Liquidity Alignment: Fixed Balance Sheet Voucher #1 Omission
- **Audit Finding:**
  - The Cash Book reported a Net Cash Balance of **₹57,444**, while the Balance Sheet reported Closing Cash in Hand of **₹57,679** (an apparent difference of **₹235**).
  - The root cause was traced to transaction row index 0 (01-04-2026):
    - **Left Side:** Contains Opening Balance (`Cash: ₹9,879`, `Bank: ₹6,51,682`).
    - **Right Side:** Contains **Voucher #1** (`Payment: ₹235` cash under `RP-16.06 Passion Week Expenses` for *"coffee powder, sugar etc"*).
  - In `renderBalanceSheet()`, the loop had an early `if (isOpening) return;` statement to prevent double-counting opening balance as a receipt. However, this early return skipped the payment side of that same row, causing Voucher #1 (₹235) to be omitted from expenses, which left the cash unspent in the Balance Sheet.
- **The Resolution:**
  - Replaced early return with conditional receipt skipping:
    ```javascript
    const isOpening = rHeadRaw.toLowerCase().includes("opening") || rDetailsRaw.toLowerCase().includes("opening balance");

    // Receipts (skip Opening Balance as it is captured in baseline opening funds)
    if (!isOpening && (hR > 0 || iR > 0 || rCodeRaw || rHeadRaw)) { ... }
    ```
  - This ensures Voucher #1 on the payment side is properly processed and included in `RP-16.06 Passion Week Expenses` (now correctly totaling **₹54,350**).
  - **Closing Cash in Hand** in Balance Sheet now perfectly matches Cash Book at **₹57,444**.
  - **Total Cash & Bank Liquidity** perfectly matches at **₹21,21,381**.
  - Balance Sheet statement remains **100% perfectly balanced** with **Variance: ₹0.00**.

---

## 2. Updated Deliverables in v11.20

| Target Platform | Location / Artifact | Core Code / Asset | Data Source / Connectivity | Deployment Command / Action |
|---|---|---|---|---|
| **Android APK (Full)** | `St_Gregorios_Church_Accounting_v11.20.apk` | `app.js?v=11.20`, `data.js`, `logo_data.js?v=11.20` | Standalone SQLite & LocalStorage | Install APK onto Android phones / tablets |
| **Android APK (Fresh Start)** | `St_Gregorios_Church_Accounting_Fresh_v11.20.apk` | `app.js?v=11.20`, `data_fresh.js` | Fresh dataset with 7-day trial mode | Install fresh-start APK for blank ledger testing |
| **Windows Desktop Launcher** | `St_Gregorios_Church_Accounting.exe` | `index_offline.html`, `app.js?v=11.20` | Local JSON files in `data_export/` | Double-click .exe to launch local Edge app window |
| **GitHub Pages** | `deployment_files/github-supabase/` | `app_supabase.js?v=11.20`, `logo_data.js?v=11.20` | Supabase Cloud PostgreSQL | `git push church-app main` |
| **cPanel Production** | `deployment_files/cpanel/` | `app_supabase.js?v=11.20`, `logo_data.js?v=11.20` | Supabase Cloud PostgreSQL | Upload via cPanel File Manager to `public_html/accounting/` |
| **cPanel Update ZIP** | `cpanel_update_v11.20.zip` | Bundled cPanel web assets | Supabase Cloud PostgreSQL | Extract directly into `public_html/accounting/` |
| **Offline Portable ZIP** | `St_Gregorios_Church_Accounting_Offline_PC_v11.20.zip` | Bundled standalone distribution suite | Embedded JSON | Unzip and run on offline PC |

---

## 3. Verification & Safety Checks
- **Perfect Multi-Platform Parity:**
  - Cash Book: Cash = ₹57,444 | Bank = ₹20,63,937 | Total Liquidity = ₹21,21,381.
  - Balance Sheet: Cash in Hand = ₹57,444 | Bank = ₹20,63,937 | Total Net Assets = ₹21,21,381 | Variance = ₹0.00.
- **Voucher Sequence Continuity:** All 26 vouchers (including Voucher #1 through #26) are fully accounted for.
- **Offline / Cloud / APK Sync:** All platforms execute the identical payment parsing logic.
