# Project Handover Document & Continuation Guide
**St. Gregorios Orthodox Syrian Church & Pilgrim Centre Accounting Portal**
*Workspace: `c:\saju_old pc\Church_App\anti_gravity_v9.2`*
*Active Release Version: 9.2*

---

## 📌 Executive Summary

This project serves as a comprehensive cross-platform accounting system replacing the legacy Excel Macro-Enabled Accounting Workbook. It features:
1.  **Web Accounting Cloud App (cPanel / PHP / MySQL):** An online portal with multi-device live data synchronization.
2.  **Standalone Windows Desktop Application (`.exe`):** A C# wrapper served locally on port `8088` (with system tray icon).
3.  **Android Mobile Applications (`.apk`):** Compiled applications bundling the client script for on-the-go access.
4.  **Automatic Compilation System:** Python-based builders that bundle assets, compile C# binaries, build Android APKs, and package portable ZIP distributables.

---

## 🛠️ Work Accomplished & Recent Fixes (Version 9.2)

### 1. Cloud Synchronization Routing Fixes
- **Cashbook Edit Sync Bug:** Resolved a critical bug in `app_cloud_final.js` where editing an existing cashbook transaction via the Admin portal failed to sync to the online database. The application previously hardcoded the `fetch` request to the local Python server (`/api/bulk_import`). We introduced dynamic environment detection to route requests properly to the PHP/MySQL backend (`./api.php`) when hosted online, preventing edits from reverting upon subsequent syncs.
- **Backup Restoration Sync:** Applied the identical environment-aware routing fix to the backup restoration logic. Uploading a `.json` backup file now correctly flushes and updates the cloud database rather than failing silently.

### 2. Migration Pathways Evaluated
- Created comprehensive documentation detailing the architecture and step-by-step procedures required to fully migrate the backend infrastructure from cPanel PHP/MySQL to **Supabase Cloud (PostgreSQL)**, paving the way for real-time collaboration and improved security.

### 3. Dynamic Path Compatibility & Cloud Script Pipeline (Inherited from v9.0)
- Compiler scripts (`build_all_releases.py`, `copy_assets_to_android.py`, etc.) dynamically resolve paths using Python's `os.path.dirname`.
- `generator_final.py` compiles `app.js` into targeted scripts:
  - **`app_cloud_final.js`:** Cloud deployment script connected to MySQL via `api.php`.
  - **`app_cloud_v10.js`:** Android/Desktop offline script with LocalStorage / Python SQLite integration.

### 4. Member Contact Directory & CSV Tooling (Inherited from v9.0)
- Full CRUD Member Directory syncable to MySQL.
- Built-in BOM-enabled CSV Exporter and RFC-compliant CSV Parser for importing.

---

## 📁 Key File Inventory

| File / Folder | Purpose |
| :--- | :--- |
| **`St_Gregorios_Church_Accounting.exe`** | C# standalone Windows launcher with tray icon (runs server on port 8088) |
| **`Start_Portal.cmd`** | Runs python backend server and launches Edge in app mode |
| **`index.html`** & **`index_cloud.html`** | Offline local and online Cloud portal layouts respectively |
| **`app.js`** | Core client-side javascript application code |
| **`app_cloud_final.js`** | Compiled cPanel Cloud Web javascript script (recently patched) |
| **`app_cloud_v10.js`** | Compiled Android WebView and Desktop offline javascript script |
| **`cloud_api/api.php`** | PHP script to process queries (save/load/import cashbook/members) |
| **`generator_final.py`** | Compiles app.js into cloud versions |
| **`build_all_releases.py`** | Orchestrates compilation of Android APKs, EXE, and ZIP portable packages |
| **`package_distributable.py`** | Assembles ZIP distribution packages under `dist/` |

---

## 🚀 How to Run Compiler Scripts

All builder tasks are run using Python (`py`):

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
