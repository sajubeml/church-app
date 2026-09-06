# St. Gregorios Church Accounting Portal — Handover Document & Continuation Guide
**St. Gregorios Orthodox Syrian Church & Pilgrim Centre, Mysuru**  
**Workspace:** `c:\saju_old pc\Church_App\anti_gravity_v9.2`  
**Current Active Release:** v10.6 (A5 Portrait Print Engine & Script Fixes)  
**Last Updated:** September 6, 2026  

---

## 📌 Executive Summary

This project serves as a comprehensive cross-platform accounting system replacing the legacy Excel Macro-Enabled Accounting Workbook. It features:
1. **Multi-Platform Cloud Sync (Supabase PostgreSQL):** Serverless architecture connected to Supabase PostgreSQL, deployed in sync across GitHub Pages (`church-app` repo) and cPanel host.
2. **Standalone Offline Mobile Applications (.apk):** Standalone offline version for Android devices running pure LocalStorage with zero internet dependency, supporting full JSON export/import.
3. **Cashbook-Brain Architecture:** Monolithic state where the Cash Book (`cashbook` array) acts as the **absolute single source of truth** for Trial Balance, Individual Ledgers, and Subscription Validity dates.
4. **Enhanced Receipt Printing Engine (v10.6):** Built-in A5 Portrait printing engine separating Original and Office Copy into 2 distinct pages (`page-break-after: always`), formatted with `DD-MM-YYYY` date strings, bold member names, and full `"ST. GREGORIOS ORTHODOX SYRIAN CHURCH & PILGRIM CENTRE"` header. Includes interactive orientation switcher (A5 Portrait, A5 Landscape, A4 2-Up).

---

## 🏗️ Architecture & Single Source of Truth Rules

### 1. Database Model
- Monolithic JSON backup file (e.g., `St_Gregorios_Church_Backup_YYYY-MM-DD.json`).
- **Cash Book (`cashbook` array):** Absolute single source of truth for:
  - Trial Balance calculations
  - Individual Member Ledger amounts & column allocations
  - Member Subscription Upto validity dates (parsed live from receipt remarks)
- **Individual Ledger (`individual` array):** Used ONLY for register numbers, names, and column headers (rows 0-3). Financial cells in the ledger grid are dynamically aggregated from the Cash Book at render time and any direct manual edits in ledger cells are ignored.

### 2. Master Account Code Standard
Source of truth hardcoded in `app_supabase.js` (`MASTER_RECEIPT_HEADS` and `MASTER_PAYMENT_HEADS`):
- **Receipt Head Codes (Left Side - Columns A..I):** Prefix `RP-10.xx`, `RP-2.xx`, `RP-3.xx`.
  - `RP-3.82` = Monthly Subscription (Current Year)
  - `RP-3.83` = Monthly Subscription (Previous Year)
  - `RP-3.32` = St. Mary's Feast Receipt
- **Payment Head Codes (Right Side - Columns K..P):** Prefix `RP-12.xx`, `RP-14.xx`, `RP-16.xx`, `RP-19.xx`.
  - `RP-16.47` = St. Mary's Feast Expense
- **CRITICAL AUDIT RULE:** Receipt code column (`F`) must NEVER contain payment codes, and Payment code column (`N`) must NEVER contain receipt codes. Code swapping breaks Trial Balance totals silently.

---

## 🛠️ Work Accomplished & Recent Enhancements (v10.0 → v10.6)

### 1. A5 Portrait Receipt & Voucher Printing (v10.6 Update)
- **Page Separation:** Formatted Original and Office Copy into 2 distinct pages (`A5 Portrait`) with clean page breaks (`page-break-after: always`).
- **Zero Spillover Height:** Set `@page { size: A5 portrait; margin: 3mm; }` with receipt card `height: 182mm !important;` and `padding: 6mm 8mm;`, guaranteeing Page 1 (ORIGINAL) and Page 2 (OFFICE COPY) span strictly across 2 sheets of paper without a 3rd blank/overflow page (tested & verified on Canon LBP2900).
- **Interactive Orientation Control:** Live dropdown toggle inside the receipt print window allowing switching between **A5 Portrait (Default)**, **A5 Landscape**, and **A4 Landscape 2-Up**.
- **Date Formatting:** Dates formatted as `DD-MM-YYYY` (e.g., `06-09-2026`).
- **Member Label & Styling:** Changed label from `"Party / Member:"` to `"Member:"` and made member name **bold** (`<strong>Abraham.M.O</strong>`).
- **Full Church Branding:** Enforced `"ST. GREGORIOS ORTHODOX SYRIAN CHURCH & PILGRIM CENTRE"` header across all receipts and vouchers.

### 2. JavaScript Engine & Browser Pre-parser Stability
- **ReferenceError Fix:** Re-ordered `attemptLogin` declaration before initial execution in `app_supabase.js` to ensure function hoisting and early initialization.
- **HTML Pre-parser Rule (`<\/script>`):** Escaped closing script tags inside JS string literals passed to child window `document.write()` to prevent premature script block termination in Edge and Chrome.

### 3. Cashbook-Brain Member Ledger Engine
- Financial amounts dynamically calculated via `findIndividualColKey({ head, code })`.
- Fixed fallback mapping issues that misallocated non-subscription items to subscription columns.

### 4. Automatic Subscription Upto Parsing (`getLatestSubscriptionRemark`)
- Scans `RP-3.82` and `RP-3.83` receipt remarks (e.g., "Apr 25 to Sept 26") and auto-calculates Subscription Upto date (`09/2026`).
- Displays `-` if no subscription receipts exist. Fixed default `03/2027` fallback bug.

---

## 📁 Key File Inventory

| File / Path | Purpose |
| :--- | :--- |
| [app_supabase.js](file:///c:/saju_old%20pc/Church_App/anti_gravity_v9.2/app_supabase.js) | Core client JS application code connected to Supabase Cloud backend. |
| [app.js](file:///c:/saju_old%20pc/Church_App/anti_gravity_v9.2/app.js) | Core client JS application code using offline LocalStorage (for APK & offline mode). |
| [index_supabase.html](file:///c:/saju_old%20pc/Church_App/anti_gravity_v9.2/index_supabase.html) | Main web portal HTML layout with Supabase auth login overlay. |
| [index_offline.html](file:///c:/saju_old%20pc/Church_App/anti_gravity_v9.2/index_offline.html) | Standalone local/offline portal HTML layout. |
| [AGENTS.md](file:///c:/saju_old%20pc/Church_App/anti_gravity_v9.2/AGENTS.md) | Knowledge base containing domain rules, deployment targets, print engine rules, and code mappings. |
| [prepare_deployments.py](file:///c:/saju_old%20pc/Church_App/anti_gravity_v9.2/prepare_deployments.py) | Packaging script that populates `deployment_files/`. |
| `android-app/` | Native Android Gradle application source (Offline release APK build target). |

---

## 🚀 Deployment & Operations Guide

### 1. Updating Web Portal (Cloud Sync)
1. Execute packaging script:
   ```powershell
   python prepare_deployments.py
   python copy_assets_to_android.py full
   ```
2. **GitHub Pages (`church-app` live site):**
   ```powershell
   git add .
   git commit -m "deploy: release update v10.6 with A5 portrait receipt printing engine & stability fixes"
   git push origin main
   git push church-app main
   ```
   *Live URL:* `https://sajubeml.github.io/church-app/`
3. **cPanel Host:**
   Upload contents of `deployment_files/cpanel/` to the web root via cPanel File Manager.

### 2. Building Standalone Android Release APK
1. Navigate to Android project directory:
   ```powershell
   cd android-app
   .\gradlew.bat assembleFullRelease
   ```
2. The compiled APK is located at:
   `android-app\app\build\outputs\apk\full\release\app-full-release.apk`
3. Copy to project root and rename to `St_Gregorios_Church_Accounting_v10.6.apk`.

---

## 🔍 Diagnostics & Verification Utilities

- **Trial Balance Audit:** `python scratch/audit_tb.py`
- **Member Ledger Audit:** `python scratch/audit_all_members.py`
- **Handover Status Checker:** `python handover_status.py`
