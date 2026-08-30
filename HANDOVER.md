# Project Handover Document & Continuation Guide
**St. Gregorios Orthodox Syrian Church & Pilgrim Centre Accounting Portal**
*Workspace: c:\saju_old pc\Church_App\anti_gravity_v9.2*
*Active Release Version: 9.4 (Stable Fallback)*

---

## 📌 Executive Summary

This project serves as a comprehensive cross-platform accounting system replacing the legacy Excel Macro-Enabled Accounting Workbook. It has evolved through several iterations and now features:
1.  **Multi-Platform Cloud Sync:** A modern serverless architecture connected to **Supabase (PostgreSQL)**, deployed perfectly in-sync across both GitHub Pages (church-app repo) and CPanel.
2.  **Standalone Offline Mobile Applications (.apk):** Fully independent offline versions (v9.4) for Android devices, utilizing LocalStorage for environments without internet access, allowing manual exports/imports to the cloud.
3.  **Automatic Deployment System:** Python-based builders (prepare_deployments.py) that cleanly segregate environments into ready-to-deploy folders.

---

## 🛠️ Work Accomplished & Recent Fixes (Versions 9.3 to 9.4)

### 1. The Supabase Serverless Migration (v9.3)
- **Legacy PHP/MySQL Removed:** The application was fully migrated away from the legacy CPanel PHP/MySQL and local Python SQLite backend architectures.
- **Fetch Interceptor (pp_supabase.js):** Built a seamless interceptor that catches all legacy pi.php requests and translates them into secure Supabase REST API requests on the fly. This saved us from rewriting thousands of lines of legacy frontend code.
- **Authentication & Security:** Implemented Supabase JWT Authentication and Row Level Security (RLS). The application now requires an email/password login to fetch or modify data.

### 2. Multi-Cloud Deployment Architecture (v9.3)
- Created prepare_deployments.py which organizes the codebase into three strict deployment folders:
  - deployment_files/cpanel/: Files ready for CPanel host (using index.html sourced from index_supabase.html).
  - deployment_files/github-supabase/: Files ready for GitHub Pages (using index.html sourced from index_supabase.html).
  - deployment_files/mobile apk v1.0/: Files ready for offline mobile apps (using index_offline.html renamed to index.html and pp.js).
- Both CPanel and GitHub deployments successfully point to the *exact same* Supabase cloud database, remaining perfectly in sync.

### 3. Print Layout, Admin Fixes, and Cache Management (v9.4)
- **Admin Delete Bug Fix:** Fixed a critical bug in confirmDeleteCashbookEntry inside both pp.js and pp_supabase.js. The payload was incorrectly parsing objects instead of JSON strings. Deletions in the Admin Panel now correctly process and immediately reflect in the Supabase backend.
- **Receipt Print Styles:** Standardized the print layouts for Receipts to enforce A4 Landscape printing globally, preventing cut-offs and misalignments across different browsers.
- **Cache Busting Versioning:** Implemented forced cache-busting (e.g. ?v=9.4) in the HTML script tags. This ensures that browsers on cPanel and GitHub immediately download the newest .js code instead of silently loading outdated offline cache.
- **Two GitHub Repositories:** Clarified the repository structure. 
  - Church_account (origin) acts as the main local backup repo.
  - church-app is the actual live GitHub Pages deployment repo. 
  - Code pushed to church-app main deploys the live site.

---

## 📁 Key File Inventory

| File / Folder | Purpose |
| :--- | :--- |
| **deployment_files/** | The finalized output directory containing the 3 deployment environments. |
| **pp_supabase.js** | Core client-side javascript application code connected to Supabase Cloud. |
| **pp.js** | Core client-side javascript application code using offline LocalStorage (for APK). |
| **index.html (root)** | The cloud portal layout containing the Secure Gateway Login overlay (Source for cloud deployments). |
| **index_offline.html** | Offline local portal layout (No login overlay - Source for mobile APKs). |
| **prepare_deployments.py** | Packages the repository into the 3 deployment folders. |

---

## 🚀 How to Re-Deploy (v9.4 onwards)

1.  **To Update Web Deployments:** 
    If you make changes to HTML/CSS/JS, run python prepare_deployments.py. 
    - For cPanel: Upload the generated contents of the deployment_files/cpanel/ folder to your cPanel File Manager.
    - For GitHub: Run git push church-app main to push the root files to the live site. (Ensure index.html cache version numbers match between HTML and JS to prevent caching).
2.  **To Rebuild Mobile APKs:**
    Navigate to the ndroid-app/ directory and run .\gradlew assembleRelease. The output will be located in ndroid-app/app/build/outputs/apk/full/release/. Then copy the files into deployment_files/mobile apk v1.0/.
3.  **To sync Offline Mobile Data:**
    Export the JSON backup from the CPanel web admin portal and import it into the Android Mobile App via **Restore/Replace Data**.
