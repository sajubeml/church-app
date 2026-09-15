# St. Gregorios Orthodox Syrian Church Accounting Portal
## Master Handover Document & Historical Continuation Guide (From Project Origin to v11.2)

**Church:** St. Gregorios Orthodox Syrian Church & Pilgrim Centre, Mysuru  
**Workspace Root:** `c:\saju_old pc\Church_App\anti_gravity_v9.2`  
**Current Active Version:** **v11.0** (Android APKs) / **v11.2** (Web & Cloud Deployments)  
**Last Updated:** September 10, 2026  
**Git Remote Origin:** `https://github.com/sajubeml/Church_account.git` (Main Codebase Backup)  
**Git Remote Church-App:** `https://github.com/sajubeml/church-app.git` (GitHub Pages Live Site)  
**Live GitHub Pages URL:** `https://sajubeml.github.io/church-app/`  
**Live cPanel Web URL:** `https://orthodoxchurchmysore.in/accounting/`  

---

## 1. Executive Summary & Project Purpose

This project is a mission-critical, full-fledged cross-platform accounting software suite designed to manage the entire financial operations of **St. Gregorios Orthodox Syrian Church & Pilgrim Centre, Mysuru**.

### Historical Problem
Historically, the church operated its accounts on a complex, macro-enabled Excel workbook (`.xlsm`). This legacy workbook suffered from severe limitations:
- Prone to silent data corruption, broken formula references, and accidental manual cell overrides.
- Inability to operate concurrently or access accounts from mobile phones.
- Difficulties in printing receipts without desktop printer drivers and complex print macros.
- Lack of an automated subscription tracking system, requiring manual inspection of member subscription validity.

### Modern Solution
The system was engineered into a modern, zero-dependency, multi-target web and native Android accounting suite:
1. **Multi-Target Deployment:** Works seamlessly as an offline desktop web app, an online cloud portal (Supabase PostgreSQL synced), an online cPanel deployment, and a standalone native Android mobile app (`.apk`).
2. **Cashbook-Brain Philosophy:** The Cash Book (`cashbook` array) is the **absolute single source of truth** for all financial ledgers, trial balance sheets, and member subscription dates.
3. **Pristine A5 Portrait Print & Silent PDF Engine:** Zero-prompt auto-generation of A5 portrait receipts and payment vouchers (Original + Office Copy) compliant with laser printer hardware boundaries.
4. **Dual-Flavor Android Application:** Provides a **Full Data** standalone version (bundled historical parish records) and a **Fresh Start** version (zeroed transactions, ready for new financial years or backup restore).

---

## 2. Core Architectural Philosophy: The "Cashbook-Brain"

The foundational rule of this codebase is that **financial amounts are never stored statically in individual member ledger cells**.

```
                           +------------------------------------+
                           |    CASH BOOK (cashbook array)      |
                           |   * Absolute Single Source of Truth*|
                           +-----------------+------------------+
                                             |
                   +-------------------------+-------------------------+
                   |                                                   |
                   v                                                   v
     +---------------------------+                       +---------------------------+
     |   Individual Ledgers      |                       |       Trial Balance       |
     |  (Dynamically Aggregated  |                       |  (Dynamically Aggregated  |
     |   at render time by Reg#) |                       |   at render time by Code) |
     +-------------+-------------+                       +---------------------------+
                   |
                   v
     +---------------------------+
     | Subscription Upto Date    |
     | (Max validity date parsed |
     |  across all member rcpts) |
     +---------------------------+
```

1. **Cash Book (`state.cashbook`):** Every financial transaction is recorded as a single receipt (Columns `A`–`I`) or payment voucher (Columns `K`–`Q`).
2. **Individual Member Ledger (`state.individual`):** Used **strictly for identity** (Register No in `B`, Member Name in `C`) and column headers (row index 3). Financial cells (`E` through `AM`) are computed dynamically on the fly by scanning `cashbook`. Any manual edits to ledger amount cells are intentionally ignored by the render engine.
3. **Trial Balance (`state.trialBalance`):** Computed by aggregating all debit and credit movements matching master account codes.

---

## 3. Master Chart of Accounts & Critical Audit Rules

Accounting codes are standardized in `app_supabase.js` and `app.js` under `MASTER_RECEIPT_HEADS` and `MASTER_PAYMENT_HEADS`.

### Receipt Heads (Left Side — Columns A to I)
Receipt codes always start with `RP-10.xx`, `RP-2.xx`, or `RP-3.xx`:
- `RP-3.82`: Monthly Subscription (Current Year)
- `RP-3.83`: Monthly Subscription (Previous Year)
- `RP-2.02` / `RP-2.02(a)`: Donation General / Furniture & Items
- `RP-2.13`: Passion Week Collection
- `RP-3.32`: St. Mary's Feast
- `RP-3.33`: St. Gregorios Feast (Annual Feast)
- `RP-3.31`: St. Thomas Feast
- `RP-16.50`: St. George Feast
- `RP-2.15(a)`: Auction Dues - Old

### Payment Heads (Right Side — Columns K to Q)
Payment codes always start with `RP-12.xx`, `RP-14.xx`, `RP-16.xx`, `RP-19.xx`:
- `RP-16.47`: St. Mary's Feast Expense
- `RP-16.48`: St. Gregorios Feast Expense
- `RP-12.xx`: Administrative & Church Maintenance Expenses

### Internal Contra Transfers
- `CD`: Contra Deposit (Excess Cash Deposited to Bank) — creates simultaneous matching receipt and voucher entries.

> [!CAUTION]
> **CRITICAL AUDIT RULE:** Receipt code column (`F`) must **NEVER** contain a payment code (`RP-12/14/16/19`), and Payment code column (`N`) must **NEVER** contain a receipt code (`RP-2/3/10`). Swapping codes causes the Trial Balance to fall out of equilibrium silently.

---

## 4. Chronological Evolution & Milestones (From Origin to v11.2)

### Phase 1: Legacy Excel Migration (v1.0 – v7.0)
- Extracted sheets from Excel workbook `St_Gregorios_Accounts.xlsm` to monolithic JSON data structures (`data.js` and `data_export/*.json`).
- Established offline web portal (`index.html`) capable of rendering Cash Book, Individual Ledger, Trial Balance, and Reconciliation Audit.

### Phase 2: Cashbook-Brain Refactor (v8.0 – v9.3)
- Discovered that operators had manually edited ledger cells in the old system, leading to ₹23,000+ discrepancies between the Cash Book and Member Ledgers.
- Rewrote `renderIndividualLedgers()` to dynamically compute all member contributions directly from `cashbook` using `findIndividualColKey({ head, code })`.
- Established the rule: If a ledger number is wrong, fix the Cash Book entry, never the ledger table.

### Phase 3: Android Native Offline Wrapper (v9.4 – v10.0)
- Created `android-app/` utilizing Android WebView, Kotlin, and `MainActivity.kt`.
- Built native SQLite local cache and bridge (`window.AndroidBridge`) allowing offline operation without internet connectivity.
- Created flavors: `full` (bundled existing parish data) and `fresh` (fresh start for new financial years).

### Phase 4: A5 Portrait Dual-Page Print Engine (v10.1 – v10.6)
- **Problem:** Laser printers (Canon LBP2900, HP LaserJet) were spilling receipts onto 3 or 4 pages, clipping outer borders due to printer unprintable hardware margins (5mm).
- **Solution:** 
  - Standardized `@page { size: A5 portrait; margin: 6mm; }`.
  - Set receipt card `height: 172mm !important;` and `padding: 4mm 6mm !important;`.
  - Strict page breaks: Page 1 (`ORIGINAL`) and Page 2 (`OFFICE COPY`) formatted with `page-break-after: always`, while `.receipt-card:last-child` has `page-break-after: avoid !important;`.
  - Added live orientation dropdown switcher (A5 Portrait, A5 Landscape, A4 2-Up).
  - Escaped all closing script tags inside JS string literals as `<\/script>` to prevent browser HTML pre-parser crashes.

### Phase 5: Self-Contained Media & Print Modal Bleed Isolation (v10.7 – v10.8)
- **Base64 Church Logo (`logo_data.js`):** Replaced asynchronous `fetch('church_logo.png')` with synchronous embedded base64 data URI (`window.CHURCH_LOGO_BASE64`), making downloaded receipt HTML files 100% self-contained and viewable offline anywhere.
- **Modal Bleed Isolation:** Configured `@media print` to explicitly hide all modal backdrops (`.modal-backdrop`, `#memberCrudModal`, etc.), preventing empty form outlines from printing.

### Phase 6: Silent Zero-Prompt Auto PDF Generation (v10.9 – v11.0)
- **Instant Auto-Save:** Creating a receipt/voucher automatically generates `Receipt_XXXX.pdf` without opening the OS print prompt.
- **Android MediaStore Integration:** On Android 10+ (API 29+), `MainActivity.kt` uses Android `MediaStore.Downloads` API to silently write PDFs directly into `Downloads/Church_Receipts/` with instant notification toast.
- **Browser Silent Download:** On PC/Web, auto-triggers a virtual anchor download click.
- **Transaction Mode Badge:** Added `Mode: CASH` or `Mode: BANK` header badge to all receipts and payment vouchers.

### Phase 7: Mobile Cashbook Responsiveness & SQLite Backup Sync (v11.0)
- Replaced fixed table percentages on `#cashbookTable` with `table-layout: auto; min-width: 100%;` inside an `overflow-x: auto;` wrapper, ensuring 16 accounting columns pan smoothly on mobile without collapsing words letter-by-letter.
- Fixed JSON backup restore in Android APK (`processBackupRestoreData`) to invoke `AndroidBridge.bulkSync()` so restored data survives app restarts.

### Phase 8: Universal Subscription Date Engine & Multi-Receipt Aggregation (v11.1 – v11.2)
- **The "01/2010" Bug:** Fixed bug where full dates like `01-10-2026` (1st Oct 2026) were matched by 2-part regex as Month `01` and Year `10` (`2010`), displaying `01/2010`.
- **Universal Date Parser (`extractSubDatesFromText`):**
  - Full 3-part dates: `DD-MM-YYYY` / `DD/MM/YYYY` (`01-10-2026` $\rightarrow$ `10/2026`).
  - ISO dates: `YYYY-MM-DD` (`2026-08-09` $\rightarrow$ `08/2026`).
  - Spaced or hyphenated month names: `Oct-25 to march-26`, `Apr-25 to Jan-26`, `apr 26 to june 26`, `apr26 to mar27`.
  - Isolated 2-part dates: `10/2026`, `03/2027`.
- **Multi-Receipt Aggregation:** `getLatestSubscriptionRemark()` scans **all** subscription receipts (`RP-3.82` & `RP-3.83`) plus Column D for each member, computing the absolute **MAXIMUM (latest)** paid month and year.
- Preserved non-member suppression: `#NM` always displays `-`.

---

## 5. Deployment Architecture & File Matrix

| Target Platform | Primary Files | Script Engine | Data Backend | Deployment Method |
| :--- | :--- | :--- | :--- | :--- |
| **Offline Local Web** | `index_offline.html`, `styles.css` | `app.js` | `data.js` (LocalStorage) | Double-click `index_offline.html` or run `python start_server.py` |
| **GitHub Pages** | `deployment_files/github-supabase/` | `app_supabase.js?v=11.2` | Supabase Cloud PostgreSQL | `git push church-app main` |
| **cPanel Production** | `deployment_files/cpanel/` | `app_supabase.js?v=11.2` | Supabase Cloud PostgreSQL | cPanel File Manager upload to `public_html/accounting/` |
| **Android Full APK** | `St_Gregorios_Church_Accounting_v11.0.apk` | `app.js` | Embedded `data.js` + SQLite Cache | Sideload APK onto Android phone |
| **Android Fresh APK** | `St_Gregorios_Church_Accounting_Fresh_v11.0.apk` | `app.js` | Zeroed transactions (`data_fresh.js`) | Sideload APK onto Android phone |

---

## 6. Complete Standard Operating Procedures (SOP)

### SOP 1: Updating Web Deployments
When modifications are made to `app_supabase.js` or `styles.css`:
```powershell
# 1. Package all deployment folders and bust cache
python prepare_deployments.py

# 2. Push to GitHub (origin repository and GitHub Pages live site)
git add -A
git commit -m "deploy: update web deployments"
git push origin main
git push church-app main

# 3. Update cPanel
# Open cPanel File Manager -> /public_html/accounting/
# Upload deployment_files/cpanel/app_supabase.js and deployment_files/cpanel/index.html
```

### SOP 2: Rebuilding Android Release APKs
When modifications are made to core logic or offline app (`app.js`):
```powershell
# --- Step A: Build Fresh Start APK ---
python build_fresh_start_data.py
python copy_assets_to_android.py fresh
cd android-app
.\gradlew.bat assembleFreshRelease
cd ..
# Copy to root targets:
copy android-app\app\build\outputs\apk\fresh\release\app-fresh-release.apk St_Gregorios_Church_Accounting_Fresh_v11.0.apk
copy android-app\app\build\outputs\apk\fresh\release\app-fresh-release.apk St_Gregorios_Church_Accounting_Fresh.apk

# --- Step B: Build Full Data Standalone APK ---
python copy_assets_to_android.py full
cd android-app
.\gradlew.bat assembleFullRelease
cd ..
# Copy to root targets:
copy android-app\app\build\outputs\apk\full\release\app-full-release.apk St_Gregorios_Church_Accounting_v11.0.apk
copy android-app\app\build\outputs\apk\full\release\app-full-release.apk St_Gregorios_Church_Accounting.apk

# --- Step C: Commit and Push APKs ---
git add -A
git commit -m "build(android): rebuild fresh and full v11.0 release APKs"
git push origin main
git push church-app main
```

### SOP 3: Performing Database Backups & Restores
1. **To Backup:** In any web client or Android app, go to **Administration** $\rightarrow$ Click **Export Full Backup JSON**. Saves as `St_Gregorios_Church_Backup_YYYY-MM-DD.json`.
2. **To Restore:** Go to **Administration** $\rightarrow$ Click **Restore / Import Backup JSON** $\rightarrow$ Select the JSON backup file. The app validates JSON structure, synchronizes SQLite, updates LocalStorage, and reloads the memory state instantly.

---

## 7. Diagnostics & Verification Utilities Inventory

The repository contains automated python scripts in `scratch/` and root for system auditing:

- `python scratch/audit_tb.py` — Verifies that Cash Book left side totals equal Trial Balance debit/credit totals to the exact paise.
- `python scratch/audit_all_members.py` — Confirms that every individual member's dynamically computed ledger equals their Cash Book total.
- `python prepare_deployments.py` — Automatically distributes web code to `deployment_files/github-supabase/`, `deployment_files/cpanel/`, and `deployment_files/mobile apk v1.0/`.
- `python build_fresh_start_data.py` — Creates pristine zeroed dataset for new financial year deployments.
- `python copy_assets_to_android.py [full|fresh]` — Bundles web assets directly into Android app assets directory.

---

## 8. Summary of Key Files

- [app_supabase.js](file:///c:/saju_old%20pc/Church_App/anti_gravity_v9.2/app_supabase.js): Main web application script (Cloud Sync).
- [app.js](file:///c:/saju_old%20pc/Church_App/anti_gravity_v9.2/app.js): Main offline application script (Android APK & local offline).
- [index_supabase.html](file:///c:/saju_old%20pc/Church_App/anti_gravity_v9.2/index_supabase.html): Supabase cloud web entry point.
- [index_offline.html](file:///c:/saju_old%20pc/Church_App/anti_gravity_v9.2/index_offline.html): Standalone offline web entry point.
- [logo_data.js](file:///c:/saju_old%20pc/Church_App/anti_gravity_v9.2/logo_data.js): Self-contained Base64 church insignia for offline receipt rendering.
- [AGENTS.md](file:///c:/saju_old%20pc/Church_App/anti_gravity_v9.2/AGENTS.md): Machine-readable system rules and learned architectural knowledge.
