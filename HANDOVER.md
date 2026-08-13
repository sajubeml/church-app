# Project Handover Document & Continuation Guide
**St. Gregorios Orthodox Syrian Church & Pilgrim Centre Accounting Portal**
*Workspace: `c:\saju_old pc\Church_App\anti_gravity`*
*Target Builds Directory: `C:\saju_old pc\Church_App\final working version-9`*
*Active Release Version: 9.0 (versionCode 50)*

---

## 📌 Executive Summary

This project converts the Excel Macro-Enabled Accounting Workbook into a cross-platform accounting system featuring:
1.  **Web Accounting Cloud App (cPanel / PHP / MySQL):** An online portal with multi-device live data synchronization.
2.  **Standalone Windows Desktop Application (`.exe`):** A C# wrapper served locally on port `8088` (with system tray icon).
3.  **Android Mobile Applications (`.apk`):** Dual flavors (Full and Fresh Start) compiled on target SDK 36.
4.  **Automatic Compilation System:** A Python-based builder that bundles assets, compiles C# binaries, builds Android APKs, and packages portable ZIP distributables.

---

## 🛠️ Work Accomplished Today (Version 9.0)

### 1. Dynamic Path Compatibility
- Modified all compiler scripts (`build_all_releases.py`, `copy_assets_to_android.py`, `build_fresh_start_data.py`, `generator_final.py`) to dynamically resolve paths using Python's `os.path.dirname(os.path.abspath(__file__))`. This prevents path failures when running in different repository locations.

### 2. Dual Cloud Script Pipeline
- Updated `generator_final.py` to compile the core `app.js` into two different optimized web scripts:
  - **`app_cloud_final.js` (Web Cloud App):** Connects to MySQL database online via `api.php`.
  - **`app_cloud_v10.js` (Android/Desktop App):** Integrates the local database API and provides an offline LocalStorage fallback check.

### 3. Bidirectional Database Synchronization
- **MySQL Integration:** Added `save_receipt` and `save_payment` SQL handlers to cPanel's `api.php`.
- **Unified Fetch Router:** Integrated a unified network router inside the client app to automatically switch saving and loading between local Python SQLite server endpoints and the online MySQL PHP database based on the browser's hostname.
- **Member Directory Cloud Sync:** Enabled syncing of `state.members` (the Member Directory) to MySQL under `CHURCH_MASTER_MEMBERS` so that phone/address edits sync permanently.

### 4. Member Contact Directory & CSV Import/Export
- Implemented a complete **Member Contact Directory** tab featuring CRUD operations (Add, Edit, Delete), pagination, and search.
- Built a **BOM-enabled CSV Exporter** to download directories readable in MS Excel.
- Built a **RFC-compliant CSV Parser** to import directories (matching Register No., Name, Phone, and Address) and sync them instantly to the database.

### 5. Essential Accounting Bug Fixes
- **Receipt Sequence Number Fix:** Recalculates `state.currentReceiptNo` and `state.currentVoucherNo` instantly after the asynchronous database load completes, correcting next receipt numbers (e.g. `4328`).
- **Opening Balance Accumulator:** Fixed `openingCash` and `openingBank` calculation, ensuring the first row values (e.g. `₹9,879` and `₹6,51,682`) are accumulated in net totals rather than hardcoded to `0`.
- **Default Port Alignment:** Changed `start_server.py` to prioritize port **`8088`** to match the C# launcher and `Start_Portal.cmd` batch scripts.

---

## 📁 Key File Inventory

| File / Folder | Purpose |
| :--- | :--- |
| **`St_Gregorios_Church_Accounting.exe`** | C# standalone Windows launcher with tray icon (runs server on port 8088) |
| **`Start_Portal.cmd`** | Runs python backend server and launches Edge in app mode |
| **`index.html`** & **`index_cloud.html`** | Offline local and online Cloud portal layouts respectively |
| **`app.js`** | Core client-side javascript application code |
| **`app_cloud_final.js`** | Compiled cPanel Cloud Web javascript script |
| **`app_cloud_v10.js`** | Compiled Android WebView and Desktop offline javascript script |
| **`cloud_api/api.php`** | PHP script to process queries (save/load/import cashbook/members) |
| **`generator_final.py`** | Compiles app.js into cloud versions |
| **`build_all_releases.py`** | Orchestrates compilation of Android APKs, EXE, and ZIP portable packages |
| **`package_distributable.py`** | Assembles ZIP distribution packages under `dist/` |
| **`dist/St_Gregorios_Church_Accounting_App_v9.0.zip`** | Full PC Portable ZIP distribution package |
| **`dist/St_Gregorios_Church_Accounting_Fresh_Start_Trial_v9.0.zip`** | Fresh Start PC Trial ZIP package |

---

## 🚀 How to Run Compiler Scripts

All builder tasks are run using Python (`py`) inside `final working version-9`:

1.  **Recompile all releases (APKs, EXE, and packaged ZIPs):**
    ```cmd
    py build_all_releases.py
    ```
2.  **Generate cloud scripts only:**
    ```cmd
    py generator_final.py
    ```
3.  **Package portable distributions only:**
    ```cmd
    py package_distributable.py
    ```
