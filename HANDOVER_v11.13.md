# St. Gregorios Orthodox Syrian Church Accounting Portal
## Master Handover Document & System Architecture Guide (v11.13)

**Church:** St. Gregorios Orthodox Syrian Church & Pilgrim Centre, Mysuru  
**Workspace Root:** `C:\CASHBOOK_APP`  
**Current Active Version:** **v11.13** (Android `versionCode 76` / Web / Cloud / Offline PC)  
**Date of Release:** October 8, 2026  
**Git Remote Origin:** `https://github.com/sajubeml/Church_account.git` (Main Codebase Backup)  
**Git Remote Church-App:** `https://github.com/sajubeml/church-app.git` (GitHub Pages Live Site)  
**Live GitHub Pages Site:** `https://sajubeml.github.io/church-app/`  
**Live cPanel Web URL:** `https://orthodoxchurchmysore.in/accounting/`  

---

## 1. Executive Summary & Purpose

The **St. Gregorios Church Accounting Portal** is a cross-platform financial accounting software suite custom-built for St. Gregorios Orthodox Syrian Church & Pilgrim Centre, Mysuru. It replaces legacy Excel macro workbooks with a robust, zero-spillover accounting system supporting:

1. **Multi-Target Synchronized Deployment:**
   - **Local Offline PC:** Standalone Windows desktop launcher (`St_Gregorios_Church_Accounting.exe` + `index.html` + `app.js`).
   - **Android Mobile Application:** Standalone native APK with embedded WebView SQLite/LocalStore (`St_Gregorios_Church_Accounting_v11.13.apk`).
   - **Cloud cPanel Web Portal:** `https://orthodoxchurchmysore.in/accounting/` (Apache/cPanel).
   - **GitHub Pages:** `https://sajubeml.github.io/church-app/`.
   - **Cloud PostgreSQL DB:** Supabase cloud database synchronization (`app_supabase.js`).

2. **The "Cashbook-Brain" Single Source of Truth:**
   - All financial balances, Individual Member Ledgers, Trial Balance sheets, and Subscription Upto validity dates are computed dynamically on the fly from the Cash Book (`cashbook` array).

3. **Strict A5 Portrait Laser Print Engine:**
   - Zero-spillover receipt card formatting (`height: 172mm !important; margin: 6mm;`) ensuring Original and Copy fit strictly on 2 pages across standard laser printers (e.g., Canon LBP2900 / HP LaserJet).

---

## 2. Key Updates & Bug Fixes in v11.11 – v11.13

### A. Receipt Item Row Spacing & Grid Borders (v11.13 - Major Fix)
* **Problem:** In newly generated receipts (e.g., RT4472), receipt items had huge 3–4 inch blank gaps between them, whereas admin reprints looked compact and clean.
* **Root Cause:** In `showReceiptModal()`, the items `<table>` had `flex: 1` assigned inside the `172mm` flex container. When a receipt had only 1 to 3 items, the browser distributed the entire remaining card height equally across the `<tr>` rows, stretching each row 30–40mm tall.
* **Resolution:**
  - Removed `flex: 1` from the items table (`app_supabase.js` & `app.js`), allowing table rows to remain compact at their natural height.
  - Added clean cell borders (`border: 1px solid #cbd5e1;` with `padding: 4px 6px;`) to match the neat grid lines of old reprints.
  - Inserted a `<div style="flex: 1;"></div>` spacer directly below the Total box. Extra vertical space is now absorbed cleanly in the blank area above the Vicar / Trustee signature line, keeping the footer at the bottom of the 172mm card without stretching the items table.

### B. Mode of Payment in Admin Reprint (v11.11)
* **Problem:** When reprinting receipts or payment vouchers from the Admin panel, the **Mode** indicator (`CASH`, `BANK`, `CASH+BANK`) was missing from the header info table.
* **Resolution:** Enhanced `reprintTxnDocument()` to inspect columns `H` & `I` (Receipts: Cash Amount / Bank Amount) and `P` & `Q` (Payments: Cash / Bank). It dynamically calculates the exact payment mode and displays a styled badge in the reprinted document header.

### C. Row Item Alignment & Sl No Alignment (v11.12)
* **Problem:** Sl No `#` column appeared drifting lower down relative to particulars text.
* **Resolution:** Enforced `vertical-align: top;` on `#`, `Particulars`, and `Amount` cells. Applied `white-space: nowrap;` on `#` and `Amount` cells to prevent text wrapping on narrow mobile screens.

### D. Offline PC Standalone Package Generator
* **Clarification:** `St_Gregorios_Church_Accounting.exe` (~13 KB) is a lightweight C# HTTP server launcher. It serves HTML/JS from its folder and cannot run in isolation in an empty directory.
* **Solution:** Created `create_offline_zip.py` which bundles only the required files into a 740 KB package:
  - `St_Gregorios_Church_Accounting_Offline_PC_v11.13.zip`
  - Includes: `St_Gregorios_Church_Accounting.exe`, `index.html`, `index_offline.html`, `app.js`, `data.js`, `styles.css`, `logo_data.js`, images, PDF libraries, `data_export/`, `Receipts/`, and `README_HOW_TO_RUN.txt`.

---

## 3. Deployment Artifacts & File Locations

| Target / Distribution | File / Path | Size | Description |
| :--- | :--- | :--- | :--- |
| **Android APK (Full Release)** | [`St_Gregorios_Church_Accounting_v11.13.apk`](file:///C:/CASHBOOK_APP/St_Gregorios_Church_Accounting_v11.13.apk) | 9.08 MB | Offline standalone Android APK with full parish data |
| **Android APK (Fresh Start)** | [`St_Gregorios_Church_Accounting_Fresh_v11.13.apk`](file:///C:/CASHBOOK_APP/St_Gregorios_Church_Accounting_Fresh_v11.13.apk) | 9.04 MB | Clean start APK for new financial years / fresh installs |
| **Android APK (Root Default)** | [`St_Gregorios_Church_Accounting.apk`](file:///C:/CASHBOOK_APP/St_Gregorios_Church_Accounting.apk) | 9.08 MB | Copy of Full Release APK |
| **Windows Desktop Launcher** | [`St_Gregorios_Church_Accounting.exe`](file:///C:/CASHBOOK_APP/St_Gregorios_Church_Accounting.exe) | 13 KB | Native C# launcher (launches server on `http://localhost:8088/`) |
| **Offline PC Bundle (ZIP)** | [`St_Gregorios_Church_Accounting_Offline_PC_v11.13.zip`](file:///C:/CASHBOOK_APP/St_Gregorios_Church_Accounting_Offline_PC_v11.13.zip) | 740 KB | Minimal offline Windows bundle for pen drive transfer |
| **cPanel Files** | [`deployment_files/cpanel/`](file:///C:/CASHBOOK_APP/deployment_files/cpanel) | ~2.1 MB | Files to upload to `/home/orthodox/public_html/accounting` |
| **GitHub Pages** | [`deployment_files/github-supabase/`](file:///C:/CASHBOOK_APP/deployment_files/github-supabase) | ~2.1 MB | Served live at `https://sajubeml.github.io/church-app/` |

---

## 4. How to Update Each Target

### 1. Web Portal on cPanel
Upload these files to `/home/orthodox/public_html/accounting`:
- `app_supabase.js` (from `deployment_files/cpanel/`)
- `index.html` (from `deployment_files/cpanel/`)

### 2. GitHub Pages
Automated via:
```powershell
git push origin main
git push church-app main
```

### 3. Offline Windows PC
1. Copy [`St_Gregorios_Church_Accounting_Offline_PC_v11.13.zip`](file:///C:/CASHBOOK_APP/St_Gregorios_Church_Accounting_Offline_PC_v11.13.zip) to pen drive.
2. Extract to any folder on the new PC.
3. Double-click `St_Gregorios_Church_Accounting.exe` (or `index.html`).

### 4. Android Phones / Tablets
Copy [`St_Gregorios_Church_Accounting_v11.13.apk`](file:///C:/CASHBOOK_APP/St_Gregorios_Church_Accounting_v11.13.apk) to phone and tap to install.

---

## 5. Build Pipeline Scripts

- `py build_all_releases.py`: Single command that compiles data bundles, desktop `.exe`, full APK, and fresh start APK.
- `py prepare_deployments.py`: Syncs and formats all separate deployment folders (`cpanel/`, `github-supabase/`, `mobile apk v1.0/`).
- `py create_offline_zip.py`: Packages minimal offline zip for Windows PC.
- `py copy_assets_to_android.py full` / `fresh`: Copies assets to Android project directory before Gradle build.
